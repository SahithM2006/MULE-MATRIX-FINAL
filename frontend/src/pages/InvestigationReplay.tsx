import React, { useEffect, useState } from 'react';
import { TransactionItem, ScenarioInfo } from '../types';
import { api } from '../services/api';
import { 
  History, 
  Play, 
  Pause, 
  SkipForward, 
  SkipBack, 
  RefreshCw, 
  ArrowRight,
  Clock,
  Layers 
} from 'lucide-react';

interface InvestigationReplayProps {
  onInvestigateAccount: (accountId: string) => void;
}

export const InvestigationReplay: React.FC<InvestigationReplayProps> = ({ onInvestigateAccount }) => {
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('');
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    api.getScenarios().then((data) => {
      setScenarios(data);
      if (data.length > 0) {
        setSelectedScenarioId(data[0].id);
      }
    });
  }, []);

  const loadScenarioTransactions = async (scenId: string) => {
    if (!scenId) return;
    try {
      setLoading(true);
      setIsPlaying(false);
      setCurrentStep(0);
      const data = await api.getTransactions({ scenario_id: scenId, limit: 100 });
      // Sort chronologically ascending for replay
      const sorted = [...data].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      setTransactions(sorted);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedScenarioId) {
      loadScenarioTransactions(selectedScenarioId);
    }
  }, [selectedScenarioId]);

  // Auto-play timer
  useEffect(() => {
    let timer: any;
    if (isPlaying && transactions.length > 0) {
      timer = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= transactions.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1400);
    }
    return () => clearInterval(timer);
  }, [isPlaying, transactions.length]);

  const activeTx = transactions[currentStep] || null;
  const cumulativeVolume = transactions.slice(0, currentStep + 1).reduce((sum, tx) => sum + tx.amount, 0);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Section 10 · Chronological Playback
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Investigation Replay
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Replays actual recorded financial transfers chronologically to observe how funds hop across banking institutions over time.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-xs font-mono text-[#858585]">Scenario:</label>
          <select
            value={selectedScenarioId}
            onChange={(e) => setSelectedScenarioId(e.target.value)}
            className="bg-[#FFFFFF] border border-[#D8D2C4] rounded px-3 py-1.5 text-xs font-mono"
          >
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div className="py-20 text-center text-[#858585]">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-[#111111]" />
          <span className="font-serif text-lg">Loading Replay Timeline...</span>
        </div>
      )}

      {transactions.length > 0 && !loading && (
        <div className="space-y-6">
          {/* Playback Controls & Progress */}
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E5E0D5]">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="p-3 bg-[#111111] text-white hover:bg-[#333] rounded-full transition shadow-sm"
                >
                  {isPlaying ? <Pause className="w-5 h-5 text-[#C6A45A]" /> : <Play className="w-5 h-5 text-[#C6A45A]" />}
                </button>
                <button
                  onClick={() => setCurrentStep((prev) => Math.max(0, prev - 1))}
                  disabled={currentStep === 0}
                  className="p-2 border border-[#D8D2C4] rounded hover:bg-[#FAF9F5] disabled:opacity-40"
                >
                  <SkipBack className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setCurrentStep((prev) => Math.min(transactions.length - 1, prev + 1))}
                  disabled={currentStep >= transactions.length - 1}
                  className="p-2 border border-[#D8D2C4] rounded hover:bg-[#FAF9F5] disabled:opacity-40"
                >
                  <SkipForward className="w-4 h-4" />
                </button>

                <div className="text-xs font-mono pl-3 border-l border-[#E5E0D5]">
                  <span className="text-[#858585]">STEP:</span>
                  <span className="font-bold text-[#111111] ml-1.5">{currentStep + 1} / {transactions.length}</span>
                </div>
              </div>

              <div className="flex items-center space-x-6 text-xs font-mono">
                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Cumulative Volume</span>
                  <span className="font-bold text-[#111111] text-sm">₹{cumulativeVolume.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Current Hop Time</span>
                  <span className="font-bold text-[#111111] text-sm">
                    {activeTx ? new Date(activeTx.timestamp).toLocaleTimeString() : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            {/* Slider */}
            <div>
              <input
                type="range"
                min={0}
                max={transactions.length - 1}
                value={currentStep}
                onChange={(e) => setCurrentStep(Number(e.target.value))}
                className="w-full accent-[#111111] cursor-pointer"
              />
            </div>
          </div>

          {/* Current Hop Callout Card */}
          {activeTx && (
            <div className="bg-[#FFFFFF] border-2 border-[#111111] rounded shadow-sm p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E5E0D5]">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#C83232] animate-ping" />
                  <span className="font-serif font-bold text-base text-[#111111]">
                    Active Transaction Hop #{currentStep + 1}
                  </span>
                </div>
                <span className="text-xs font-mono text-[#858585]">
                  Rail: <strong>{activeTx.channel}</strong> · Time: {new Date(activeTx.timestamp).toUTCString()}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center font-mono">
                {/* Source */}
                <div className="p-4 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
                  <span className="text-[10px] text-[#858585] uppercase block">Source Account</span>
                  <button
                    onClick={() => onInvestigateAccount(activeTx.source_account_id)}
                    className="font-bold text-sm text-[#111111] hover:text-[#7596C8] hover:underline block text-left"
                  >
                    {activeTx.source_account_number || activeTx.source_account_id}
                  </button>
                  <span className="text-xs text-[#555] block truncate">{activeTx.source_holder}</span>
                  <span className="text-[10px] text-[#858585] block">{activeTx.source_bank}</span>
                </div>

                {/* Amount Arrow */}
                <div className="text-center space-y-1">
                  <span className="font-serif text-2xl font-bold text-[#A63D40]">
                    ₹{activeTx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                  <div className="flex items-center justify-center space-x-1 text-[#858585]">
                    <div className="h-[1px] w-12 bg-[#D8D2C4]" />
                    <ArrowRight className="w-4 h-4 text-[#A63D40]" />
                    <div className="h-[1px] w-12 bg-[#D8D2C4]" />
                  </div>
                  <span className="text-[10px] text-[#858585] uppercase tracking-wider block">
                    {activeTx.description || 'P2P Transfer'}
                  </span>
                </div>

                {/* Destination */}
                <div className="p-4 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
                  <span className="text-[10px] text-[#858585] uppercase block">Destination Account</span>
                  <button
                    onClick={() => onInvestigateAccount(activeTx.dest_account_id)}
                    className="font-bold text-sm text-[#111111] hover:text-[#7596C8] hover:underline block text-left"
                  >
                    {activeTx.dest_account_number || activeTx.dest_account_id}
                  </button>
                  <span className="text-xs text-[#555] block truncate">{activeTx.dest_holder}</span>
                  <span className="text-[10px] text-[#858585] block">{activeTx.dest_bank}</span>
                </div>
              </div>
            </div>
          )}

          {/* Sequential Hops History Table */}
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-5 space-y-3">
            <h3 className="font-serif font-bold text-base text-[#111111]">
              Chronological Sequence ({transactions.length} Steps)
            </h3>
            <div className="overflow-x-auto max-h-72 overflow-y-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-[#E5E0D5] text-[10px] uppercase text-[#858585]">
                    <th className="py-2 px-3">#</th>
                    <th className="py-2 px-3">Time</th>
                    <th className="py-2 px-3">From</th>
                    <th className="py-2 px-3">To</th>
                    <th className="py-2 px-3 text-right">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E5E0D5]">
                  {transactions.map((tx, idx) => (
                    <tr
                      key={tx.id}
                      onClick={() => setCurrentStep(idx)}
                      className={`cursor-pointer transition ${
                        idx === currentStep ? 'bg-[#111111] text-white font-bold' : 'hover:bg-[#FAF9F5]'
                      }`}
                    >
                      <td className="py-2 px-3">{idx + 1}</td>
                      <td className="py-2 px-3">{new Date(tx.timestamp).toLocaleTimeString()}</td>
                      <td className="py-2 px-3 truncate max-w-[120px]">{tx.source_account_number || tx.source_account_id}</td>
                      <td className="py-2 px-3 truncate max-w-[120px]">{tx.dest_account_number || tx.dest_account_id}</td>
                      <td className="py-2 px-3 text-right">₹{tx.amount.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

