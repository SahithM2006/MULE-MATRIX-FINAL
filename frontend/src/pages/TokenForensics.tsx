import React, { useEffect, useState } from 'react';
import { LineageVerificationResult } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Layers, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Lock, 
  Key, 
  ArrowDown, 
  AlertTriangle,
  Play
} from 'lucide-react';

interface TokenForensicsProps {
  initialTokenId?: string;
  onInvestigateAccount: (accountId: string) => void;
}

export const TokenForensics: React.FC<TokenForensicsProps> = ({
  initialTokenId,
  onInvestigateAccount
}) => {
  const [tokenId, setTokenId] = useState(initialTokenId || '');
  const [availableTokens, setAvailableTokens] = useState<Array<{
    token_id: string;
    total_events: number;
    origin_account_id: string;
    terminal_account_id: string;
    amount: number;
    created_at: string;
  }>>([]);
  const [result, setResult] = useState<LineageVerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tamperingSimulated, setTamperingSimulated] = useState(false);

  const fetchLineage = async (id: string) => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      setTamperingSimulated(false);
      const data = await api.getTokenLineage(id);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Token lineage retrieval failed.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateTampering = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.simulateTamperTest(tokenId, 1);
      const v = res.verification_result;
      setResult({
        token_id: v.token_id || tokenId,
        is_intact: v.is_intact,
        total_events: v.total_events,
        first_broken_seq: v.first_broken_seq,
        verification_status: v.verification_status as any,
        error_reason: v.error_reason,
        chain: ((v as any).verified_chain || []).map((c: any) => ({
          id: `step_${c.event_seq}`,
          token_id: tokenId,
          event_seq: c.event_seq,
          tx_id: c.tx_id || '',
          from_account_id: c.from_account_id || '',
          to_account_id: c.to_account_id || '',
          amount: c.amount,
          previous_hash: c.recorded_previous_hash,
          current_hash: c.recorded_current_hash,
          computed_hash: c.recomputed_hash,
          is_valid: c.is_step_valid,
          created_at: new Date().toISOString(),
          payload_json: ''
        }))
      });
      setTamperingSimulated(true);
    } catch (err: any) {
      setError(err.message || 'Tamper simulation failed.');
    } finally {
      setLoading(false);
    }
  };

  const loadTokensAndInit = async () => {
    try {
      setLoading(true);
      const tokens = await api.getAvailableTokens();
      setAvailableTokens(tokens);
      if (tokens.length > 0) {
        const selectedId = (initialTokenId && tokens.some(t => t.token_id === initialTokenId))
          ? initialTokenId
          : tokens[0].token_id;
        setTokenId(selectedId);
        fetchLineage(selectedId);
      } else {
        setTokenId('');
        setResult(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to query token registry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTokensAndInit();
  }, [initialTokenId]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Editorial Header */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Algorithm 2 · Cryptographic Lineage
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Token Forensics & Hash Integrity
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Verifies cryptographic immutability of e₹ token assets using RFC 8785 canonical JSON serialization and SHA-256 recursive hash links.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {tamperingSimulated ? (
            <button
              onClick={() => fetchLineage(tokenId)}
              className="flex items-center space-x-2 px-4 py-2 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition font-semibold"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Verify Authentic Chain</span>
            </button>
          ) : (
            <button
              onClick={handleSimulateTampering}
              className="flex items-center space-x-2 px-4 py-2 bg-[#A63D40] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#852E30] transition font-semibold shadow-sm"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Simulate Tampering Test</span>
            </button>
          )}
        </div>
      </div>

      {/* Token Selector Strip */}
      <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-xs font-mono text-[#858585]">Active Token Ledger:</label>
          {availableTokens.length > 0 ? (
            <select
              value={tokenId}
              onChange={(e) => {
                setTokenId(e.target.value);
                fetchLineage(e.target.value);
              }}
              className="px-3 py-1.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono font-bold text-[#111111]"
            >
              {availableTokens.map((t) => (
                <option key={t.token_id} value={t.token_id}>
                  {t.token_id} ({t.total_events} hops, ₹{t.amount?.toLocaleString()})
                </option>
              ))}
            </select>
          ) : (
            <span className="text-xs font-mono text-[#858585]">No active tokens</span>
          )}

          <div className="flex items-center space-x-2">
            <input
              type="text"
              placeholder="Or enter token ID..."
              value={tokenId}
              onChange={(e) => setTokenId(e.target.value)}
              className="w-56 px-3 py-1.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono font-bold text-[#111111]"
            />
            <button
              onClick={() => fetchLineage(tokenId)}
              className="px-3 py-1.5 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition"
            >
              Verify
            </button>
          </div>
        </div>

        {result && (
          <div className="flex items-center space-x-3">
            <span className="text-xs font-mono text-[#858585]">VERIFICATION OUTCOME:</span>
            <StatusBadge status={result.verification_status} type="lineage" />
          </div>
        )}
      </div>

      {/* Empty Notice if No Lineage in DB */}
      {!loading && !result && availableTokens.length === 0 && !error && (
        <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded p-8 text-center space-y-2">
          <Layers className="w-8 h-8 text-[#858585] mx-auto mb-2" />
          <h3 className="font-serif text-lg font-bold text-[#111111]">No Token Lineage Records Present</h3>
          <p className="text-xs font-mono text-[#666] max-w-xl mx-auto">
            Standard transactions are ordinary bank transfers and do not carry cryptographic e₹ token headers.
            To generate and inspect a CBDC cryptographic token flow, visit the Scenario Simulator and inject a Token Lineage scenario.
          </p>
        </div>
      )}

      {/* Error Notice */}
      {error && (
        <div className="p-4 bg-[#C83232]/10 border border-[#C83232]/30 rounded text-xs font-mono text-[#C83232]">
          {error}
        </div>
      )}

      {/* Main Forensic View */}
      {result && (
        <div className="space-y-6">
          {/* Integrity Banner */}
          <div className={`p-4 rounded border flex items-start space-x-4 ${
            result.is_intact 
              ? 'bg-[#2E7D32]/5 border-[#2E7D32]/30 text-[#1B5E20]' 
              : 'bg-[#C83232]/10 border-[#C83232]/30 text-[#C83232]'
          }`}>
            {result.is_intact ? (
              <ShieldCheck className="w-6 h-6 shrink-0 mt-0.5" />
            ) : (
              <ShieldAlert className="w-6 h-6 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-serif font-bold text-base">
                {result.is_intact
                  ? 'Cryptographic Lineage Intact · 100% Hash Consistency'
                  : `Lineage Verification Failed · Link Broken at Step #${result.first_broken_seq}`}
              </div>
              <p className="text-xs mt-1 font-mono">
                {result.error_reason || 'Every cryptographic link in the hash chain satisfies recursive SHA-256 canonical verification.'}
              </p>
            </div>
          </div>

          {/* Sequential Cryptographic Chain Steps */}
          <div className="space-y-4">
            <h3 className="font-serif font-bold text-lg text-[#111111]">
              Cryptographic Event Chain ({result.chain.length} Hops)
            </h3>

            <div className="space-y-3">
              {result.chain.map((step, idx) => (
                <div key={step.event_seq} className="relative">
                  {/* Step Card */}
                  <div className={`bg-[#FFFFFF] border p-5 rounded shadow-sm transition ${
                    step.is_valid ? 'border-[#D8D2C4]' : 'border-[#C83232] bg-[#FFF8F8]'
                  }`}>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-[#E5E0D5]">
                      <div className="flex items-center space-x-3">
                        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold ${
                          step.is_valid ? 'bg-[#111111] text-white' : 'bg-[#C83232] text-white'
                        }`}>
                          {step.event_seq}
                        </span>
                        <div>
                          <span className="font-mono text-xs font-bold text-[#111111]">
                            Hop Reference: {step.tx_id}
                          </span>
                          <span className="text-[11px] text-[#858585] ml-2 font-mono">
                            Amount: ₹{step.amount.toLocaleString()}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => onInvestigateAccount(step.from_account_id)}
                          className="text-xs font-mono text-[#7596C8] hover:underline"
                        >
                          {step.from_account_id}
                        </button>
                        <span className="text-[#858585]">→</span>
                        <button
                          onClick={() => onInvestigateAccount(step.to_account_id)}
                          className="text-xs font-mono text-[#7596C8] hover:underline"
                        >
                          {step.to_account_id}
                        </button>

                        {step.is_valid ? (
                          <span className="flex items-center space-x-1 text-xs text-[#2E7D32] font-mono font-bold ml-4">
                            <CheckCircle2 className="w-4 h-4" />
                            <span>VALID</span>
                          </span>
                        ) : (
                          <span className="flex items-center space-x-1 text-xs text-[#C83232] font-mono font-bold ml-4">
                            <XCircle className="w-4 h-4" />
                            <span>TAMPERED</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Hash Preimage & Digests */}
                    <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                      <div>
                        <span className="text-[#858585] block text-[10px] uppercase">Recorded Previous Hash</span>
                        <span className="text-[#555] break-all block bg-[#FAF9F5] p-1.5 rounded border border-[#EAE6DC]">
                          {step.previous_hash}
                        </span>
                      </div>

                      <div>
                        <span className="text-[#858585] block text-[10px] uppercase">
                          {step.is_valid ? 'Verified Current SHA-256 Digest' : 'Mismatching Computed Digest'}
                        </span>
                        <span className={`break-all block p-1.5 rounded border ${
                          step.is_valid 
                            ? 'bg-[#FAF9F5] text-[#111111] border-[#EAE6DC]' 
                            : 'bg-[#FFEEEE] text-[#C83232] border-[#C83232]/40 font-bold'
                        }`}>
                          {step.computed_hash || step.current_hash}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Connecting Arrow */}
                  {idx < result.chain.length - 1 && (
                    <div className="flex justify-center my-1 text-[#858585]">
                      <ArrowDown className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
