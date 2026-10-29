import React, { useEffect, useState } from 'react';
import { AccountRiskProfile, EngineSignal } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { RiskGauge } from '../components/RiskGauge';
import { 
  Cpu, 
  ShieldAlert, 
  GitFork, 
  AlertTriangle, 
  Layers, 
  Activity, 
  CheckCircle2, 
  Info,
  RefreshCw,
  Search 
} from 'lucide-react';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer 
} from 'recharts';

interface DetectionLabProps {
  initialAccountId?: string;
  onNavigateToTrace: (accountId: string) => void;
  onNavigateToCase: (accountId: string, summary: string) => void;
}

export const DetectionLab: React.FC<DetectionLabProps> = ({
  initialAccountId = 'acc_mule_001',
  onNavigateToTrace,
  onNavigateToCase
}) => {
  const [accountId, setAccountId] = useState(initialAccountId);
  const [profile, setProfile] = useState<AccountRiskProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = async (targetId: string) => {
    if (!targetId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await api.getAccountRiskProfile(targetId);
      setProfile(data);
    } catch (err: any) {
      setError(err.message || 'Failed to generate detection profile.');
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialAccountId) {
      setAccountId(initialAccountId);
      loadProfile(initialAccountId);
    }
  }, [initialAccountId]);

  // Transform signals for Radar visualization
  const radarData = profile?.signals.map((s) => ({
    subject: s.engine_name.split(' ')[0],
    score: s.score,
    fullMark: 100
  })) || [];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Editorial Title */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Explainable Risk Aggregation
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Detection Lab & Algorithmic Matrix
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Normalized composite risk assessment across eight analytical engines with bounded signal contributions and plain-English factual synthesis.
          </p>
        </div>

        {profile && (
          <div className="flex items-center space-x-3">
            <button
              onClick={() => onNavigateToTrace(profile.account_id)}
              className="flex items-center space-x-2 px-4 py-2 border border-[#111111] text-[#111111] rounded text-xs font-mono uppercase tracking-wider hover:bg-[#F0ECE1] transition font-semibold"
            >
              <GitFork className="w-3.5 h-3.5" />
              <span>Trace Flow</span>
            </button>
            <button
              onClick={() => onNavigateToCase(profile.account_id, profile.narrative_explanation)}
              className="flex items-center space-x-2 px-4 py-2 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition font-semibold shadow-sm"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-[#C6A45A]" />
              <span>Open Incident Case</span>
            </button>
          </div>
        )}
      </div>

      {/* Target Selector */}
      <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm flex items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <label className="text-xs font-mono text-[#858585]">Target Account ID:</label>
          <input
            type="text"
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            placeholder="acc_mule_001"
            className="w-48 px-3 py-1.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono font-bold"
          />
          <button
            onClick={() => loadProfile(accountId)}
            className="px-4 py-1.5 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333]"
          >
            Assess
          </button>
        </div>

        {profile && (
          <div className="text-xs font-mono text-[#858585]">
            Evaluated by {profile.active_signals_count} active engines
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-[#C83232]/10 border border-[#C83232]/30 rounded text-xs font-mono text-[#C83232]">
          {error}
        </div>
      )}

      {loading && (
        <div className="py-20 text-center text-[#858585]">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-[#111111]" />
          <span className="font-serif text-lg">Synthesizing Algorithmic Signals...</span>
        </div>
      )}

      {profile && !loading && (
        <div className="space-y-6">
          {/* Executive Account Profile Summary */}
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
              {/* Gauge Column */}
              <div className="flex justify-center md:border-r border-[#E5E0D5] md:pr-6">
                <RiskGauge score={profile.composite_risk_score} tier={profile.risk_tier} size={150} />
              </div>

              {/* Identity Column */}
              <div className="md:col-span-2 space-y-2">
                <div className="flex items-center space-x-2">
                  <StatusBadge status={profile.risk_tier} type="risk" />
                  <span className="text-xs font-mono text-[#858585]">ID: {profile.account_id}</span>
                </div>
                <h2 className="font-serif text-2xl font-bold text-[#111111]">
                  {profile.holder_name}
                </h2>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs font-mono text-[#555]">
                  <div><span className="text-[#858585]">Account:</span> {profile.account_number}</div>
                  <div><span className="text-[#858585]">Institution:</span> {profile.bank_name}</div>
                  <div><span className="text-[#858585]">Type:</span> {profile.account_type}</div>
                  <div><span className="text-[#858585]">Balance:</span> ₹{profile.balance.toLocaleString()}</div>
                </div>
              </div>

              {/* Radar Chart Column */}
              <div className="h-44 w-full flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#E5E0D5" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#858585', fontSize: 10, fontFamily: 'monospace' }} />
                    <Radar name="Risk" dataKey="score" stroke="#C83232" fill="#C83232" fillOpacity={0.25} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Plain-English Factual Narrative */}
            <div className="mt-6 pt-5 border-t border-[#E5E0D5] bg-[#FAF9F5] p-4 rounded border border-[#ECE8DE]">
              <div className="text-[10px] font-mono uppercase tracking-widest text-[#858585] mb-1 font-bold">
                Analytical Narrative Synthesis
              </div>
              <p className="text-sm font-serif leading-relaxed text-[#222222]">
                {profile.narrative_explanation}
              </p>
            </div>
          </div>

          {/* Engine Contribution Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {profile.signals.map((sig) => (
              <div key={sig.engine_id} className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-5 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-[#E5E0D5]">
                  <span className="font-serif font-bold text-sm text-[#111111]">
                    {sig.engine_name}
                  </span>
                  <StatusBadge status={sig.status} />
                </div>

                <div className="flex items-baseline justify-between">
                  <span className="font-mono text-2xl font-bold text-[#111111]">
                    {sig.score.toFixed(1)}
                    <span className="text-xs text-[#858585] font-normal">/100</span>
                  </span>
                  <span className="text-xs font-mono text-[#858585]">
                    Weight: {(sig.weight * 100).toFixed(0)}%
                  </span>
                </div>

                <p className="text-xs text-[#555] line-clamp-3">
                  {sig.summary}
                </p>

                {sig.engine_id === 'isolation_forest' && sig.details.top_anomalous_features && (
                  <div className="pt-2 border-t border-[#E5E0D5] text-[11px] font-mono space-y-1">
                    <span className="text-[#858585] text-[10px] uppercase">Perturbation Drivers:</span>
                    {sig.details.top_anomalous_features.map((f: any, i: number) => (
                      <div key={i} className="flex justify-between text-[#444]">
                        <span>{f.feature}</span>
                        <span className="font-bold text-[#C83232]">+{f.impact}%</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Topological Feature Metrics Snapshot Table */}
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
            <h3 className="font-serif font-bold text-lg text-[#111111]">
              Topological Graph Metrics (Feature Snapshot)
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 font-mono text-xs">
              {Object.entries(profile.feature_metrics).map(([key, val]) => (
                <div key={key} className="bg-[#FAF9F5] p-3 rounded border border-[#E5E0D5]">
                  <span className="text-[#858585] text-[10px] uppercase block truncate">{key.replace(/_/g, ' ')}</span>
                  <span className="text-sm font-bold text-[#111111]">
                    {typeof val === 'number' ? (val >= 1000 ? `₹${val.toLocaleString()}` : val.toFixed(2)) : val}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Triggered Rule Predicates */}
          {profile.rule_evidences.length > 0 && (
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
              <h3 className="font-serif font-bold text-lg text-[#111111]">
                Rule Engine Predicate Evaluations ({profile.rule_evidences.length})
              </h3>
              <div className="divide-y divide-[#E5E0D5]">
                {profile.rule_evidences.map((r) => (
                  <div key={r.rule_code} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                    <div className="space-y-0.5">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-[#111111]">{r.rule_code}</span>
                        <span className="font-semibold text-[#111111]">{r.rule_name}</span>
                        <StatusBadge status={r.predicate_met ? 'TRIGGERED' : 'CLEAR'} />
                      </div>
                      <p className="text-[#555]">{r.description}</p>
                    </div>
                    <div className="font-mono text-right shrink-0">
                      <span className="text-[#858585]">Contribution: </span>
                      <span className="font-bold text-[#111111]">+{r.bounded_contribution} pts</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

