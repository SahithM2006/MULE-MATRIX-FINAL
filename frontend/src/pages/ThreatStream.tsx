import React, { useEffect, useState } from 'react';
import { TransactionItem } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Search, 
  Filter, 
  GitFork, 
  Cpu, 
  Layers, 
  ArrowRight, 
  RefreshCw,
  ExternalLink 
} from 'lucide-react';

interface ThreatStreamProps {
  onInvestigateAccount: (accountId: string) => void;
  onTraceFlow: (accountId: string) => void;
  onInspectToken: (tokenId: string) => void;
}

export const ThreatStream: React.FC<ThreatStreamProps> = ({
  onInvestigateAccount,
  onTraceFlow,
  onInspectToken
}) => {
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [channelFilter, setChannelFilter] = useState('');
  const [lineageOnly, setLineageOnly] = useState(false);
  const [minAmount, setMinAmount] = useState<string>('');

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await api.getTransactions({
        channel: channelFilter || undefined,
        has_lineage: lineageOnly ? true : undefined,
        min_amount: minAmount ? parseFloat(minAmount) : undefined,
        limit: 100
      });
      setTransactions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [channelFilter, lineageOnly]);

  const handleApplyFilter = (e: React.FormEvent) => {
    e.preventDefault();
    loadTransactions();
  };

  const filtered = transactions.filter((tx) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      tx.id.toLowerCase().includes(term) ||
      tx.tx_hash.toLowerCase().includes(term) ||
      (tx.source_account_number && tx.source_account_number.toLowerCase().includes(term)) ||
      (tx.dest_account_number && tx.dest_account_number.toLowerCase().includes(term)) ||
      (tx.source_holder && tx.source_holder.toLowerCase().includes(term)) ||
      (tx.dest_holder && tx.dest_holder.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Editorial Header */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Real-Time Surveillance Stream
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Threat Stream
          </h1>
          <p className="text-sm text-[#666] mt-0.5">
            Normalized ledger of cross-bank movements, synthetic settlement rails, and tokenized transfers.
          </p>
        </div>
        <div className="text-xs font-mono text-[#858585]">
          Viewing {filtered.length} settled movements
        </div>
      </div>

      {/* Swiss Filter Strip */}
      <form onSubmit={handleApplyFilter} className="bg-[#FFFFFF] border border-[#D8D2C4] p-4 rounded shadow-sm flex flex-wrap items-center gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-[#858585]" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search account, holder, hash, or ID..."
            className="w-full pl-9 pr-3 py-1.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono focus:outline-none focus:border-[#111111]"
          />
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-xs font-mono text-[#858585]">Channel:</label>
          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="bg-[#FAF9F5] border border-[#D8D2C4] rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none"
          >
            <option value="">All Rails</option>
            <option value="UPI">UPI</option>
            <option value="IMPS">IMPS</option>
            <option value="NEFT">NEFT</option>
            <option value="RTGS">RTGS</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-xs font-mono text-[#858585]">Min Amount:</label>
          <input
            type="number"
            value={minAmount}
            onChange={(e) => setMinAmount(e.target.value)}
            placeholder="e.g. 50000"
            className="w-28 px-2.5 py-1.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono focus:outline-none"
          />
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="lineage-toggle"
            checked={lineageOnly}
            onChange={(e) => setLineageOnly(e.target.checked)}
            className="rounded text-[#111111] focus:ring-0"
          />
          <label htmlFor="lineage-toggle" className="text-xs font-mono text-[#111111] cursor-pointer flex items-center space-x-1">
            <Layers className="w-3.5 h-3.5 text-[#C6A45A]" />
            <span>e₹ Token Lineage Only</span>
          </label>
        </div>

        <button
          type="submit"
          className="px-4 py-1.5 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition ml-auto"
        >
          Filter
        </button>
      </form>

      {/* Transaction Table */}
      <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#FAF9F5] border-b border-[#D8D2C4] text-[10px] font-mono uppercase tracking-wider text-[#858585]">
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">TX Reference</th>
                <th className="py-3 px-4">Source Account</th>
                <th className="py-3 px-2 text-center">Rail</th>
                <th className="py-3 px-4">Destination Account</th>
                <th className="py-3 px-4 text-right">Amount (INR)</th>
                <th className="py-3 px-4">Risk Signal</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E0D5] font-mono">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-[#858585]">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#111111]" />
                    <span>Loading stream records...</span>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-[#858585]">
                    No transactions match current filters.
                  </td>
                </tr>
              ) : (
                filtered.map((tx) => (
                  <tr key={tx.id} className="hover:bg-[#FAF9F5] transition">
                    <td className="py-3 px-4 text-[#666] whitespace-nowrap">
                      {new Date(tx.timestamp).toLocaleString('en-US', { timeZone: 'UTC', hour12: false })}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-bold text-[#111111]">{tx.id}</div>
                      <div className="text-[10px] text-[#858585] truncate max-w-[120px]">{tx.tx_hash}</div>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => onInvestigateAccount(tx.source_account_id)}
                        className="text-left font-bold text-[#111111] hover:text-[#7596C8] hover:underline block"
                      >
                        {tx.source_account_number || tx.source_account_id}
                      </button>
                      <div className="text-[10px] text-[#666] truncate max-w-[140px]">
                        {tx.source_holder} · {tx.source_bank}
                      </div>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-[#EAE6DC] text-[#444] font-semibold">
                        {tx.channel}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => onInvestigateAccount(tx.dest_account_id)}
                        className="text-left font-bold text-[#111111] hover:text-[#7596C8] hover:underline block"
                      >
                        {tx.dest_account_number || tx.dest_account_id}
                      </button>
                      <div className="text-[10px] text-[#666] truncate max-w-[140px]">
                        {tx.dest_holder} · {tx.dest_bank}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-[#111111] whitespace-nowrap">
                      ₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4">
                      {tx.risk_flag ? (
                        <span className="px-2 py-0.5 bg-[#C83232]/10 text-[#C83232] border border-[#C83232]/30 rounded text-[10px] font-bold">
                          {tx.risk_flag}
                        </span>
                      ) : tx.has_token_lineage ? (
                        <span className="px-2 py-0.5 bg-[#C6A45A]/15 text-[#9C7A28] border border-[#C6A45A]/30 rounded text-[10px] font-medium flex items-center w-max space-x-1">
                          <Layers className="w-3 h-3" />
                          <span>e₹ Verified</span>
                        </span>
                      ) : (
                        <span className="text-[10px] text-[#858585]">Normal Flow</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => onTraceFlow(tx.source_account_id)}
                          title="Trace Flow in Attack Graph"
                          className="p-1.5 hover:bg-[#EAE6DC] rounded text-[#444] transition"
                        >
                          <GitFork className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => onInvestigateAccount(tx.dest_account_id)}
                          title="Analyze in Detection Lab"
                          className="p-1.5 hover:bg-[#EAE6DC] rounded text-[#444] transition"
                        >
                          <Cpu className="w-3.5 h-3.5" />
                        </button>
                      </div>
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

