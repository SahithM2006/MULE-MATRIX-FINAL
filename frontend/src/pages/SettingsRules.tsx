import React from 'react';
import { Sliders, Shield, Scale, Cpu, Clock, Layers } from 'lucide-react';

export const SettingsRules: React.FC = () => {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4">
        <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
          System Configuration & Predicates
        </div>
        <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
          Rules & Algorithmic Parameters
        </h1>
        <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
          Documented thresholds, traversal bounds, and versioned risk aggregation weights powering the detection engines.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Rule Engine Predicates */}
        <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-[#E5E0D5]">
            <Shield className="w-5 h-5 text-[#C6A45A]" />
            <h2 className="font-serif font-bold text-lg text-[#111111]">
              Deterministic Rule Engine (Alg 5)
            </h2>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
              <div className="flex justify-between font-bold text-[#111111]">
                <span>R-101: Rapid Pass-Through Conduit</span>
                <span className="text-[#C83232]">&gt;= 85.0% Flow</span>
              </div>
              <p className="font-serif text-[#555] text-xs">
                Flags accounts where minimum turnover ratio is at least 85% within a 1-hour rolling window with cumulative flow exceeding ₹10,000.
              </p>
            </div>

            <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
              <div className="flex justify-between font-bold text-[#111111]">
                <span>R-102: High-Frequency Velocity Burst</span>
                <span className="text-[#C83232]">&gt;= 5 Transactions</span>
              </div>
              <p className="font-serif text-[#555] text-xs">
                Triggered when an account executes 5 or more transactions within any rolling 10-minute sliding window.
              </p>
            </div>

            <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
              <div className="flex justify-between font-bold text-[#111111]">
                <span>R-103: Structured Smurfing (Fan-In)</span>
                <span className="text-[#C83232]">&gt;= 4 Inward Deposits</span>
              </div>
              <p className="font-serif text-[#555] text-xs">
                Detects 4 or more incoming transfers below reporting thresholds (₹1,000 - ₹49,999) from distinct accounts followed by rapid dissipation.
              </p>
            </div>

            <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
              <div className="flex justify-between font-bold text-[#111111]">
                <span>R-104: Multi-Hop Layering Conduit</span>
                <span className="text-[#C83232]">Fan-In &gt;= 3 & Fan-Out &gt;= 3</span>
              </div>
              <p className="font-serif text-[#555] text-xs">
                Isolates balanced transit nodes where fan-in and fan-out both equal or exceed 3 counterparties with low capital retention (&gt;= 70% pass-through).
              </p>
            </div>

            <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
              <div className="flex justify-between font-bold text-[#111111]">
                <span>R-105: Cross-Bank Dispersion</span>
                <span className="text-[#C83232]">&gt;= 2 Distinct Institutions</span>
              </div>
              <p className="font-serif text-[#555] text-xs">
                Flags immediate fan-out to 2 or more distinct synthetic banking institutions within 2 hours.
              </p>
            </div>
          </div>
        </div>

        {/* Aggregation Weights & Traversal Limits */}
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-[#E5E0D5]">
              <Scale className="w-5 h-5 text-[#7596C8]" />
              <h2 className="font-serif font-bold text-lg text-[#111111]">
                Explainable Risk Aggregator (v1.2.0)
              </h2>
            </div>

            <p className="text-xs text-[#666] font-serif">
              Canonical weights allocated across available anomaly and detection engines. Dynamically renormalized when models are not trained.
            </p>

            <div className="space-y-2 font-mono text-xs">
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Deterministic Rules Engine</span>
                <strong className="text-[#111111]">35% Weight</strong>
              </div>
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Sliding-Window Temporal Velocity</span>
                <strong className="text-[#111111]">20% Weight</strong>
              </div>
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Inductive GraphSAGE GNN</span>
                <strong className="text-[#111111]">20% Weight</strong>
              </div>
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Isolation Forest Topological Outlier</span>
                <strong className="text-[#111111]">15% Weight</strong>
              </div>
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Louvain Modularity Community Clustering</span>
                <strong className="text-[#111111]">10% Weight</strong>
              </div>
            </div>
          </div>

          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-[#E5E0D5]">
              <Clock className="w-5 h-5 text-[#A63D40]" />
              <h2 className="font-serif font-bold text-lg text-[#111111]">
                BFS Traversal Engine Limits (Alg 3)
              </h2>
            </div>

            <div className="space-y-2 font-mono text-xs">
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Default Traversal Depth (Max Hops)</span>
                <strong className="text-[#111111]">4 Hops (Bound: 1-8)</strong>
              </div>
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Lookback / Lookahead Window</span>
                <strong className="text-[#111111]">72 Hours</strong>
              </div>
              <div className="flex justify-between p-2 bg-[#FAF9F5] rounded">
                <span>Search Budget Safety Ceiling</span>
                <strong className="text-[#111111]">250 Nodes / Edges</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

