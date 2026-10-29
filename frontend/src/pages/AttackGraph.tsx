import React, { useEffect, useState } from 'react';
import { TraceResult, GraphNode, GraphEdge } from '../types';
import { api } from '../services/api';
import { CytoscapeGraph } from '../components/CytoscapeGraph';
import { StatusBadge } from '../components/StatusBadge';
import { 
  GitFork, 
  ArrowRight, 
  AlertOctagon, 
  Layers, 
  Play, 
  Search, 
  Sliders, 
  Cpu, 
  ShieldAlert,
  Info,
  RefreshCw 
} from 'lucide-react';

interface AttackGraphProps {
  initialAccountId?: string;
  onNavigateToDetect: (accountId: string) => void;
  onNavigateToCase: (accountId: string) => void;
  onNavigateToLineage: (tokenId: string) => void;
}

export const AttackGraph: React.FC<AttackGraphProps> = ({
  initialAccountId = 'acc_mule_001',
  onNavigateToDetect,
  onNavigateToCase,
  onNavigateToLineage
}) => {
  const [accountId, setAccountId] = useState(initialAccountId);
  const [direction, setDirection] = useState<'FORWARD' | 'BACKWARD' | 'BIDIRECTIONAL'>('FORWARD');
  const [maxHops, setMaxHops] = useState(4);
  const [lookaheadHours, setLookaheadHours] = useState(72);
  const [traceResult, setTraceResult] = useState<TraceResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);

  const executeTrace = async (targetId?: string) => {
    const idToTrace = targetId || accountId;
    if (!idToTrace) return;

    try {
      setLoading(true);
      setError(null);
      setSelectedNode(null);
      setSelectedEdge(null);
      const res = await api.runBfsTrace({
        account_id: idToTrace,
        direction: direction,
        max_hops: maxHops,
        lookahead_hours: lookaheadHours,
        lookback_hours: lookaheadHours
      });
      setTraceResult(res);
      // Auto-select root node
      const root = res.nodes.find((n) => n.id === idToTrace);
      if (root) setSelectedNode(root);
    } catch (err: any) {
      setError(err.message || 'BFS Trace traversal failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialAccountId) {
      setAccountId(initialAccountId);
      executeTrace(initialAccountId);
    }
  }, [initialAccountId]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title & Operational Banner */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Reconstructive Flow Graph
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Attack Graph & Traversal Engine
          </h1>
          <p className="text-sm text-[#666] mt-0.5">
            Bidirectional time-constrained BFS graph traversal with cycle prevention, stop reason attribution, and multi-bank tracking.
          </p>
        </div>

        {traceResult && (
          <div className="flex items-center space-x-3 text-xs font-mono bg-[#FFFFFF] border border-[#D8D2C4] px-3 py-1.5 rounded shadow-sm">
            <span>VOL TRACED:</span>
            <span className="font-bold text-[#111111]">₹{traceResult.total_volume_traced.toLocaleString()}</span>
            <span className="text-[#858585]">|</span>
            <span>NODES:</span>
            <span className="font-bold text-[#111111]">{traceResult.nodes_count}</span>
            <span className="text-[#858585]">|</span>
            <span>EDGES:</span>
            <span className="font-bold text-[#111111]">{traceResult.edges_count}</span>
          </div>
        )}
      </div>

      {/* Traversal Parameter Control Bar */}
      <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <label className="text-xs font-mono text-[#858585]">Focus Entity:</label>
          <input
            type="text"
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            placeholder="acc_mule_001"
            className="px-3 py-1.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono focus:outline-none focus:border-[#111111] w-40"
          />
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-xs font-mono text-[#858585]">Direction:</label>
          <div className="flex border border-[#D8D2C4] rounded overflow-hidden text-xs font-mono">
            {(['FORWARD', 'BACKWARD', 'BIDIRECTIONAL'] as const).map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDirection(d)}
                className={`px-3 py-1.5 transition ${
                  direction === d ? 'bg-[#111111] text-white font-bold' : 'bg-[#FAF9F5] text-[#555] hover:bg-[#EAE5D9]'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-xs font-mono text-[#858585]">Max Hops:</label>
          <select
            value={maxHops}
            onChange={(e) => setMaxHops(Number(e.target.value))}
            className="bg-[#FAF9F5] border border-[#D8D2C4] rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none"
          >
            <option value={1}>1 Hop</option>
            <option value={2}>2 Hops</option>
            <option value={3}>3 Hops</option>
            <option value={4}>4 Hops</option>
            <option value={5}>5 Hops</option>
            <option value={6}>6 Hops</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-xs font-mono text-[#858585]">Lookahead Window:</label>
          <select
            value={lookaheadHours}
            onChange={(e) => setLookaheadHours(Number(e.target.value))}
            className="bg-[#FAF9F5] border border-[#D8D2C4] rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none"
          >
            <option value={12}>12 Hours</option>
            <option value={24}>24 Hours</option>
            <option value={48}>48 Hours</option>
            <option value={72}>72 Hours</option>
            <option value={168}>7 Days</option>
          </select>
        </div>

        <button
          onClick={() => executeTrace()}
          disabled={loading}
          className="flex items-center space-x-2 px-5 py-2 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#252830] transition ml-auto font-semibold shadow-sm"
        >
          {loading ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 text-[#C6A45A]" />
          )}
          <span>Trace Flow</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-[#C83232]/10 border border-[#C83232]/30 rounded text-xs font-mono text-[#C83232]">
          {error}
        </div>
      )}

      {/* Main Graph Canvas and Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left: Cytoscape Graph Canvas (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          {traceResult ? (
            <CytoscapeGraph
              nodes={traceResult.nodes}
              edges={traceResult.edges}
              startAccountId={traceResult.start_account_id}
              onSelectNode={(node) => {
                setSelectedNode(node);
                setSelectedEdge(null);
              }}
              onSelectEdge={(edge) => {
                setSelectedEdge(edge);
                setSelectedNode(null);
              }}
              height="640px"
            />
          ) : (
            <div className="h-[640px] bg-[#0F1117] border border-[#252A34] rounded flex flex-col items-center justify-center text-[#858585] font-mono text-sm">
              <GitFork className="w-10 h-10 mb-3 text-[#4A5060]" />
              <span>Select an account and click "Trace Flow" to reconstruct transaction graph.</span>
            </div>
          )}

          {/* Stop Reason Attributed Banner */}
          {traceResult && (
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm flex items-start space-x-3">
              <Info className="w-5 h-5 text-[#7596C8] shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-mono font-bold text-[#111111] flex items-center space-x-2">
                  <span>TERMINATION REASON:</span>
                  <span className="px-2 py-0.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-[11px] text-[#A63D40]">
                    {traceResult.stop_reason}
                  </span>
                </div>
                <p className="text-xs text-[#555] mt-1">
                  {traceResult.stop_reason_description}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right: Forensic Entity Inspector (1 col) */}
        <div className="space-y-6">
          {/* Selected Node Inspector */}
          {selectedNode ? (
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E5E0D5]">
                <h3 className="font-serif font-bold text-base text-[#111111]">
                  Account Inspector
                </h3>
                {selectedNode.is_start && (
                  <span className="text-[10px] font-mono bg-[#C6A45A]/20 text-[#8C6D1F] px-1.5 py-0.5 rounded font-bold">
                    ROOT FOCUS
                  </span>
                )}
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Account Number</span>
                  <span className="font-bold text-[#111111] text-sm">{selectedNode.account_number}</span>
                </div>

                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Holder Name</span>
                  <span className="font-semibold text-[#111111]">{selectedNode.holder_name}</span>
                </div>

                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Institution</span>
                  <span className="text-[#111111]">{selectedNode.bank_name}</span>
                  <span className="text-[#858585] block text-[10px]">({selectedNode.bank_swift})</span>
                </div>

                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Account Type</span>
                  <span className="text-[#111111]">{selectedNode.account_type}</span>
                </div>

                {selectedNode.is_offramp && (
                  <div className="p-2 bg-[#A63D40]/10 border border-[#A63D40]/30 rounded text-[#A63D40] text-[11px]">
                    ● Identified terminal crypto/cash off-ramp exit point.
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-[#E5E0D5] space-y-2">
                <button
                  onClick={() => onNavigateToDetect(selectedNode.id)}
                  className="w-full flex items-center justify-center space-x-2 py-2 bg-[#111111] text-white hover:bg-[#333] rounded text-xs font-mono uppercase tracking-wider transition font-medium"
                >
                  <Cpu className="w-3.5 h-3.5 text-[#C6A45A]" />
                  <span>Detection Lab</span>
                </button>

                <button
                  onClick={() => onNavigateToCase(selectedNode.id)}
                  className="w-full flex items-center justify-center space-x-2 py-2 border border-[#111111] text-[#111111] hover:bg-[#FAF9F5] rounded text-xs font-mono uppercase tracking-wider transition font-medium"
                >
                  <ShieldAlert className="w-3.5 h-3.5 text-[#A63D40]" />
                  <span>Open Incident Case</span>
                </button>

                <button
                  onClick={() => {
                    setAccountId(selectedNode.id);
                    executeTrace(selectedNode.id);
                  }}
                  className="w-full text-center text-[11px] font-mono text-[#7596C8] hover:underline pt-1 block"
                >
                  Pivot Trace From This Node
                </button>
              </div>
            </div>
          ) : selectedEdge ? (
            /* Selected Edge Inspector */
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-5 space-y-4">
              <div className="pb-3 border-b border-[#E5E0D5]">
                <h3 className="font-serif font-bold text-base text-[#111111]">
                  Movement Inspector
                </h3>
              </div>

              <div className="space-y-3 text-xs font-mono">
                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Settled Amount</span>
                  <span className="font-bold text-[#111111] text-base">
                    ₹{selectedEdge.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>

                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Timestamp (UTC)</span>
                  <span className="text-[#111111]">
                    {new Date(selectedEdge.timestamp).toISOString()}
                  </span>
                </div>

                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Rail Channel</span>
                  <span className="inline-block px-2 py-0.5 bg-[#EAE6DC] rounded text-[#333] font-bold text-[10px]">
                    {selectedEdge.channel}
                  </span>
                </div>

                <div>
                  <span className="text-[#858585] block text-[10px] uppercase">Transaction Hash</span>
                  <span className="text-[#858585] text-[10px] break-all block">{selectedEdge.tx_hash}</span>
                </div>

                {selectedEdge.has_lineage && (
                  <div className="p-2.5 bg-[#C6A45A]/15 border border-[#C6A45A]/40 rounded text-xs text-[#8C6D1F] space-y-1">
                    <div className="font-bold flex items-center space-x-1">
                      <Layers className="w-3.5 h-3.5" />
                      <span>e₹ Token Lineage Available</span>
                    </div>
                    <p className="text-[11px]">
                      Cryptographic serial lineage exists for this asset hop.
                    </p>
                    <button
                      onClick={() => onNavigateToLineage('eINR_TOKEN_101_9921')}
                      className="text-[11px] underline font-bold text-[#111111] hover:text-[#C6A45A]"
                    >
                      Inspect SHA-256 Chain
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 text-center text-xs font-mono text-[#858585]">
              Click any node or transaction edge in the canvas to inspect forensic properties.
            </div>
          )}

          {/* Chronological Paths Table */}
          {traceResult && traceResult.paths.length > 0 && (
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-4 space-y-2">
              <h4 className="font-serif font-bold text-xs uppercase tracking-wider text-[#111111] border-b border-[#E5E0D5] pb-2">
                Reconstructed Paths ({traceResult.paths.length})
              </h4>
              <div className="space-y-1.5 max-h-48 overflow-y-auto font-mono text-[11px]">
                {traceResult.paths.map((p, idx) => (
                  <div key={idx} className="p-1.5 bg-[#FAF9F5] rounded border border-[#E5E0D5] truncate text-[#444]">
                    <span className="font-bold text-[#111111] mr-1">#{idx + 1}:</span>
                    {p.join(' → ')}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

