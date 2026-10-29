import React, { useEffect, useState } from 'react';
import { ScenarioInfo } from '../types';
import { api } from '../services/api';
import { 
  Database, 
  PlusCircle, 
  Play, 
  RefreshCw, 
  Layers, 
  ArrowRight,
  GitFork,
  Radio 
} from 'lucide-react';

interface ScenarioSimulatorProps {
  onInvestigateScenario: (scenarioId: string) => void;
}

export const ScenarioSimulator: React.FC<ScenarioSimulatorProps> = ({ onInvestigateScenario }) => {
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedType, setSelectedType] = useState('RAPID_PASSTHROUGH');
  const [seed, setSeed] = useState(301);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const scenarioTypes = [
    {
      id: 'RAPID_PASSTHROUGH',
      name: 'Rapid Pass-Through Conduit',
      desc: 'High-velocity flow where >=90% of funds exit within 45 minutes to off-ramps.'
    },
    {
      id: 'SMURFING_FANIN',
      name: 'Structured Smurfing Syndicate',
      desc: 'Multiple senders transmit sub-reporting threshold sums to a central collector.'
    },
    {
      id: 'MULE_RING',
      name: 'Circular Mule Ring',
      desc: 'Closed clique of accounts circulating funds repeatedly to obscure origins.'
    },
    {
      id: 'LAYERING_CHAIN',
      name: 'Multi-Hop Layering Chain',
      desc: 'Linear 5-hop dispersion hopping across distinct banking institutions.'
    },
    {
      id: 'CROSS_BANK_SPLIT_MERGE',
      name: 'Cross-Bank Split-and-Merge',
      desc: 'Origin splits funds across 3 banks, which converge onto a single exit account.'
    }
  ];

  const loadScenarios = async () => {
    try {
      setLoading(true);
      const data = await api.getScenarios();
      setScenarios(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setGenerating(true);
      setSuccessMsg(null);
      const newScen = await api.generateScenario({
        scenario_type: selectedType,
        seed: seed,
        accounts_count: 20
      });
      setSuccessMsg(`Injected scenario '${newScen.name}' with ${newScen.transactions_count} transactions (Seed #${newScen.seed}).`);
      setSeed((prev) => prev + 1);
      loadScenarios();
    } catch (err: any) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4">
        <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
          Synthetic Injection Harness
        </div>
        <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
          Scenario Simulator
        </h1>
        <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
          Deterministic generation and real-time injection of multi-bank mule patterns into the active financial graph.
        </p>
      </div>

      {successMsg && (
        <div className="p-3 bg-[#2E7D32]/10 border border-[#2E7D32]/30 text-[#1B5E20] rounded text-xs font-mono flex items-center justify-between">
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-[#858585] hover:text-[#111111]">✕</button>
        </div>
      )}

      {/* Scenario Generation Form */}
      <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
        <h2 className="font-serif font-bold text-lg text-[#111111] pb-2 border-b border-[#E5E0D5]">
          Generate Deterministic Syndicate Scenario
        </h2>

        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-1">
              <label className="text-xs font-mono text-[#858585] uppercase">Select Pattern Topology:</label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full bg-[#FAF9F5] border border-[#D8D2C4] rounded p-2 text-xs font-mono font-bold text-[#111111] focus:outline-none"
              >
                {scenarioTypes.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.id})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-mono text-[#858585] uppercase">Random Seed:</label>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value))}
                className="w-full bg-[#FAF9F5] border border-[#D8D2C4] rounded p-2 text-xs font-mono font-bold text-[#111111] focus:outline-none"
              />
            </div>
          </div>

          <div className="text-xs text-[#555] font-serif bg-[#FAF9F5] p-3 rounded border border-[#E5E0D5]">
            {scenarioTypes.find((t) => t.id === selectedType)?.desc}
          </div>

          <button
            type="submit"
            disabled={generating}
            className="flex items-center space-x-2 px-5 py-2.5 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition font-semibold disabled:opacity-50 shadow-sm"
          >
            {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <PlusCircle className="w-4 h-4 text-[#C6A45A]" />}
            <span>Inject Scenario Into Matrix</span>
          </button>
        </form>
      </div>

      {/* Available Scenarios Table */}
      <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-[#E5E0D5]">
          <h3 className="font-serif font-bold text-lg text-[#111111]">
            Active Synthetic Scenarios ({scenarios.length})
          </h3>
          <span className="text-xs font-mono text-[#858585]">Persisted in SQLite database</span>
        </div>

        <div className="divide-y divide-[#E5E0D5]">
          {scenarios.map((scen) => (
            <div key={scen.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-[#111111]">{scen.name}</span>
                  <span className="text-[10px] font-mono bg-[#EAE6DC] px-2 py-0.5 rounded text-[#555]">
                    Seed #{scen.seed}
                  </span>
                  <span className="text-[10px] font-mono text-[#7596C8] uppercase">
                    {scen.scenario_type}
                  </span>
                </div>
                <p className="text-xs text-[#555] font-serif max-w-2xl">{scen.description}</p>
                <div className="text-[11px] font-mono text-[#858585]">
                  {scen.transactions_count} settled movements · Created {new Date(scen.created_at).toLocaleDateString()}
                </div>
              </div>

              <div className="flex items-center space-x-2 shrink-0">
                <button
                  onClick={() => onInvestigateScenario(scen.id)}
                  className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#171A1F] text-white hover:bg-[#333] rounded text-xs font-mono uppercase tracking-wider transition"
                >
                  <span>Filter Stream</span>
                  <ArrowRight className="w-3.5 h-3.5 text-[#C6A45A]" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

