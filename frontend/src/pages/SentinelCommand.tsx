import React, { useEffect, useState } from 'react';
import { SentinelSummary, AlertItem } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Radio, 
  AlertTriangle, 
  Layers, 
  ArrowRight, 
  PlusCircle, 
  Activity, 
  ShieldAlert, 
  Building2,
  RefreshCw 
} from 'lucide-react';

interface SentinelCommandProps {
  onInvestigateAccount: (accountId: string) => void;
  onNavigateToSimulator: () => void;
  onNavigateToStream: () => void;
}

export const SentinelCommand: React.FC<SentinelCommandProps> = ({
  onInvestigateAccount,
  onNavigateToSimulator,
  onNavigateToStream
}) => {
  const [summary, setSummary] = useState<SentinelSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getSentinelSummary();
      setSummary(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to Mule Matrix backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-[#858585]">
        <RefreshCw className="w-8 h-8 animate-spin mb-3 text-[#111111]" />
        <span className="font-serif text-lg">Polling Sentinel Multi-Bank Radar...</span>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="bg-[#FFFFFF] border border-[#C83232]/30 p-6 rounded-md my-8 max-w-2xl mx-auto shadow-sm">
        <div className="flex items-center space-x-3 text-[#C83232] mb-2">
          <AlertTriangle className="w-5 h-5" />
          <h3 className="font-serif font-bold text-lg">Sentinel Connection Error</h3>
        </div>
        <p className="text-sm text-[#444] mb-4">{error}</p>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Editorial Title Banner */}
      <div className="border-b border-[#D8D2C4] pb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Overview & Telemetry
          </div>
          <h1 className="font-serif text-3xl md:text-4xl font-bold tracking-tight text-[#111111]">
            Sentinel Command Radar
          </h1>
          <p className="text-sm text-[#666] mt-1 max-w-3xl">
            Real-time surveillance across synthetic banking institutions. Combines eight algorithmic engines to surface high-velocity dispersion, smurfing syndicates, and rapid conduits.
          </p>
        </div>

        {/* Primary User Action Choice */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onNavigateToSimulator}
            className="flex items-center space-x-2 px-4 py-2.5 bg-[#FFFFFF] hover:bg-[#F0ECE1] text-[#111111] border border-[#D8D2C4] rounded text-xs font-mono uppercase tracking-wider transition shadow-sm font-semibold"
          >
            <PlusCircle className="w-4 h-4 text-[#C6A45A]" />
            <span>Generate Scenario</span>
          </button>
          <button
            onClick={onNavigateToStream}
            className="flex items-center space-x-2 px-4 py-2.5 bg-[#111111] hover:bg-[#252830] text-[#FFFFFF] rounded text-xs font-mono uppercase tracking-wider transition shadow-sm font-semibold"
          >
            <Radio className="w-4 h-4 text-[#7596C8]" />
            <span>Investigate Threat Stream</span>
          </button>
        </div>
      </div>

      {/* Swiss KPI Metric Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm">
          <div className="text-[10px] font-mono text-[#858585] uppercase tracking-wider mb-1">
            Accounts Ingested
          </div>
          <div className="font-serif text-2xl font-bold text-[#111111]">
            {summary.total_accounts.toLocaleString()}
          </div>
          <div className="text-[11px] text-[#2E7D32] mt-1 font-mono flex items-center space-x-1">
            <span>● 100% Validated</span>
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm">
          <div className="text-[10px] font-mono text-[#858585] uppercase tracking-wider mb-1">
            Settled Movements
          </div>
          <div className="font-serif text-2xl font-bold text-[#111111]">
            {summary.total_transactions.toLocaleString()}
          </div>
          <div className="text-[11px] text-[#858585] mt-1 font-mono">
            Across 6 Rails
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm">
          <div className="text-[10px] font-mono text-[#858585] uppercase tracking-wider mb-1">
            Active Alerts
          </div>
          <div className="font-serif text-2xl font-bold text-[#A63D40]">
            {summary.active_alerts_count}
          </div>
          <div className="text-[11px] text-[#A63D40] mt-1 font-mono font-medium">
            {summary.critical_alerts_count} Critical Level
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm">
          <div className="text-[10px] font-mono text-[#858585] uppercase tracking-wider mb-1">
            Syndicate Entities
          </div>
          <div className="font-serif text-2xl font-bold text-[#C83232]">
            {summary.high_risk_accounts_count}
          </div>
          <div className="text-[11px] text-[#858585] mt-1 font-mono">
            Ground-Truth Isolated
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm">
          <div className="text-[10px] font-mono text-[#858585] uppercase tracking-wider mb-1">
            Total Rails Volume
          </div>
          <div className="font-serif text-2xl font-bold text-[#111111]">
            ₹{(summary.total_volume_inr / 10000000).toFixed(2)} Cr
          </div>
          <div className="text-[11px] text-[#858585] mt-1 font-mono">
            INR Settled
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm">
          <div className="text-[10px] font-mono text-[#858585] uppercase tracking-wider mb-1">
            Institutions
          </div>
          <div className="font-serif text-2xl font-bold text-[#111111]">
            {summary.total_institutions} Banks
          </div>
          <div className="text-[11px] text-[#7596C8] mt-1 font-mono">
            Multi-Bank Topology
          </div>
        </div>
      </div>

      {/* Main Dual Work Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: High-Severity Live Alerts (2 cols) */}
        <div className="lg:col-span-2 bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#E5E0D5]">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-[#C83232]" />
              <h2 className="font-serif text-xl font-bold text-[#111111]">
                Active Algorithmic Threats & Findings
              </h2>
            </div>
            <span className="text-xs font-mono text-[#858585]">
              Showing {summary.recent_alerts.length} prioritized signals
            </span>
          </div>

          <div className="divide-y divide-[#E5E0D5]">
            {summary.recent_alerts.length === 0 ? (
              <div className="py-12 text-center text-[#858585] font-mono text-sm">
                No active threats detected in current surveillance window.
              </div>
            ) : (
              summary.recent_alerts.map((alt) => (
                <div key={alt.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-[#FAF9F5] p-2 rounded transition">
                  <div className="space-y-1 max-w-xl">
                    <div className="flex items-center space-x-2">
                      <StatusBadge status={alt.severity} type="alert" />
                      <span className="font-mono text-xs font-bold text-[#111111]">
                        {alt.account_number}
                      </span>
                      <span className="text-xs text-[#858585]">
                        ({alt.holder_name}) · {alt.bank_name}
                      </span>
                    </div>
                    <div className="font-semibold text-sm text-[#111111]">
                      {alt.title}
                    </div>
                    <p className="text-xs text-[#555] line-clamp-2">
                      {alt.description}
                    </p>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <button
                      onClick={() => onInvestigateAccount(alt.account_id)}
                      className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#171A1F] text-[#FFFFFF] hover:bg-[#333] rounded text-xs font-mono tracking-wider transition"
                    >
                      <span>Investigate</span>
                      <ArrowRight className="w-3.5 h-3.5 text-[#C6A45A]" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Active Synthetic Scenarios & Topology (1 col) */}
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6">
            <div className="flex items-center space-x-2 pb-4 mb-4 border-b border-[#E5E0D5]">
              <Layers className="w-5 h-5 text-[#C6A45A]" />
              <h2 className="font-serif text-lg font-bold text-[#111111]">
                Active Scenarios
              </h2>
            </div>

            <div className="space-y-3">
              {summary.active_scenarios.map((scen) => (
                <div key={scen.id} className="border border-[#E5E0D5] p-3 rounded bg-[#FAF9F5]">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-[#111111]">
                      {scen.name}
                    </span>
                    <span className="text-[10px] font-mono bg-[#EAE6DC] px-1.5 py-0.5 rounded text-[#555]">
                      Seed #{scen.seed}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#666] mt-1 font-mono uppercase tracking-wider">
                    {scen.scenario_type.replace(/_/g, ' ')}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-[#E5E0D5]">
              <button
                onClick={onNavigateToSimulator}
                className="w-full py-2 border border-[#111111] text-[#111111] hover:bg-[#111111] hover:text-white rounded text-xs font-mono uppercase tracking-wider transition font-medium text-center block"
              >
                Open Scenario Simulator
              </button>
            </div>
          </div>

          {/* Synthetic Institutions Reference */}
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6">
            <div className="flex items-center space-x-2 pb-3 mb-3 border-b border-[#E5E0D5]">
              <Building2 className="w-4 h-4 text-[#7596C8]" />
              <h3 className="font-serif font-bold text-sm text-[#111111]">
                Synthetic Banking Rails
              </h3>
            </div>
            <ul className="text-xs space-y-2 text-[#555] font-mono">
              <li className="flex justify-between">
                <span>Apex Reserve Bank</span>
                <span className="text-[#858585]">APEXINBB</span>
              </li>
              <li className="flex justify-between">
                <span>Continental Commercial</span>
                <span className="text-[#858585]">CONTINBB</span>
              </li>
              <li className="flex justify-between">
                <span>Zenith Digital NeoBank</span>
                <span className="text-[#858585]">ZENIINBB</span>
              </li>
              <li className="flex justify-between">
                <span>Vanguard Cooperative</span>
                <span className="text-[#858585]">VANGINBB</span>
              </li>
              <li className="flex justify-between">
                <span>NeoPay Gateway (Offramp)</span>
                <span className="text-[#A63D40] font-bold">NEOPINBB</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

