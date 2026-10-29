import React, { useEffect, useState } from 'react';
import { AuditEventItem, AuditIntegrityReport } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Lock, 
  ShieldCheck, 
  ShieldAlert, 
  RefreshCw, 
  CheckCircle2, 
  Hash, 
  Clock, 
  User 
} from 'lucide-react';

export const AuditLedger: React.FC = () => {
  const [events, setEvents] = useState<AuditEventItem[]>([]);
  const [integrity, setIntegrity] = useState<AuditIntegrityReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const data = await api.getAuditEvents(100);
      setEvents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const verifyLedger = async () => {
    try {
      setVerifying(true);
      const res = await api.verifyAuditLedger();
      setIntegrity(res);
    } catch (err) {
      console.error(err);
    } finally {
      setVerifying(false);
    }
  };

  useEffect(() => {
    loadEvents();
    verifyLedger();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Section 10 · Compliance Ledger
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Tamper-Evident Audit Ledger
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Cryptographically chained record of every investigator action, trace execution, scenario generation, and evidence export with recursive SHA-256 previous-hash verification.
          </p>
        </div>

        <button
          onClick={verifyLedger}
          disabled={verifying}
          className="flex items-center space-x-2 px-4 py-2 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition font-semibold shadow-sm"
        >
          {verifying ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-[#2E7D32]" />}
          <span>Verify Cryptographic Chain</span>
        </button>
      </div>

      {/* Verification Status Banner */}
      {integrity && (
        <div className={`p-4 rounded border flex items-center justify-between gap-4 ${
          integrity.is_ledger_intact 
            ? 'bg-[#2E7D32]/5 border-[#2E7D32]/30 text-[#1B5E20]' 
            : 'bg-[#C83232]/10 border-[#C83232]/30 text-[#C83232]'
        }`}>
          <div className="flex items-center space-x-3">
            {integrity.is_ledger_intact ? (
              <CheckCircle2 className="w-5 h-5 text-[#2E7D32]" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-[#C83232]" />
            )}
            <div>
              <span className="font-serif font-bold text-sm block">
                {integrity.is_ledger_intact
                  ? 'Audit Chain 100% Intact & Verified'
                  : `Integrity Failure Detected at Record #${integrity.first_tampered_index}`}
              </span>
              <span className="text-xs font-mono">{integrity.verification_details}</span>
            </div>
          </div>

          <div className="text-xs font-mono text-right shrink-0">
            <span>Verified {integrity.total_events} Linked Events</span>
          </div>
        </div>
      )}

      {/* Audit Log Table */}
      <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="bg-[#FAF9F5] border-b border-[#D8D2C4] text-[10px] uppercase tracking-wider text-[#858585]">
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Action Type</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Action Details</th>
                <th className="py-3 px-4">Current Digest (SHA-256)</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E0D5]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-[#858585]">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#111111]" />
                    <span>Loading audit records...</span>
                  </td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-[#858585]">
                    No audit records logged yet.
                  </td>
                </tr>
              ) : (
                events.map((ev) => (
                  <tr key={ev.id} className="hover:bg-[#FAF9F5] transition">
                    <td className="py-3 px-4 text-[#666] whitespace-nowrap">
                      {new Date(ev.timestamp).toLocaleString('en-US', { timeZone: 'UTC', hour12: false })}
                    </td>
                    <td className="py-3 px-4 font-bold text-[#111111]">
                      {ev.event_type}
                    </td>
                    <td className="py-3 px-4 text-[#555] whitespace-nowrap">
                      {ev.actor}
                    </td>
                    <td className="py-3 px-4 text-[#333] max-w-md">
                      {ev.action_details}
                    </td>
                    <td className="py-3 px-4 text-[10px] text-[#858585] truncate max-w-[140px]" title={ev.current_hash}>
                      {ev.current_hash}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#2E7D32]/10 text-[#2E7D32] border border-[#2E7D32]/30 font-bold">
                        COMMITTED
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

