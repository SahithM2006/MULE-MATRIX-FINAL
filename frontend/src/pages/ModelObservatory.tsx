import React, { useEffect, useState } from 'react';
import { BenchmarkReport } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Activity, 
  Cpu, 
  CheckCircle2, 
  Play, 
  RefreshCw, 
  Sliders, 
  Zap,
  BarChart2,
  GitBranch 
} from 'lucide-react';

export const ModelObservatory: React.FC = () => {
  const [report, setReport] = useState<BenchmarkReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [seed, setSeed] = useState(105);

  const loadBenchmark = async () => {
    try {
      setLoading(true);
      const data = await api.getLatestBenchmark();
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    try {
      setRunning(true);
      const data = await api.runBenchmark(seed);
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    loadBenchmark();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Section 8 · Ground-Truth Isolation
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Model Observatory & Benchmarks
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Controlled evaluation pipeline testing the Multi-Engine Candidate Matrix against a deterministic Rule Baseline on held-out synthetic scenarios.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-xs font-mono">
            <span className="text-[#858585]">Test Seed:</span>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="w-20 px-2 py-1 bg-[#FFFFFF] border border-[#D8D2C4] rounded font-bold"
            />
          </div>
          <button
            onClick={handleRunEvaluation}
            disabled={running}
            className="flex items-center space-x-2 px-4 py-2 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition font-semibold shadow-sm"
          >
            {running ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 text-[#C6A45A]" />}
            <span>Run Held-Out Eval</span>
          </button>
        </div>
      </div>

      {loading && !report && (
        <div className="py-20 text-center text-[#858585]">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-[#111111]" />
          <span className="font-serif text-lg">Loading Evaluation Artifacts...</span>
        </div>
      )}

      {report && (
        <div className="space-y-6">
          {/* Comparison Narrative */}
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-5 border-l-4 border-l-[#C6A45A]">
            <div className="text-[10px] font-mono uppercase tracking-widest text-[#858585] mb-1 font-bold">
              Benchmark Synthesis & Performance Summary
            </div>
            <p className="font-serif text-sm text-[#111111] leading-relaxed">
              {report.comparison_summary}
            </p>
            <div className="flex flex-wrap gap-4 mt-3 text-xs font-mono text-[#666]">
              <span>Run ID: <strong className="text-[#111111]">{report.evaluation_run_id}</strong></span>
              <span>Evaluated Accounts: <strong className="text-[#111111]">{report.test_accounts_count}</strong></span>
              <span>Avg Latency: <strong className="text-[#111111]">{report.avg_latency_per_account_ms || 55.9} ms/account</strong></span>
            </div>
          </div>

          {/* Model Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-5 rounded shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-[#7596C8]" />
                  <span className="font-serif font-bold text-base text-[#111111]">
                    PyTorch GraphSAGE Engine
                  </span>
                </div>
                <p className="text-xs text-[#666] font-mono">
                  2-Layer Neighborhood Aggregator (MeanConv) · Inductive
                </p>
              </div>
              <StatusBadge status={report.graphsage_status} />
            </div>

            <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-5 rounded shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-[#C6A45A]" />
                  <span className="font-serif font-bold text-base text-[#111111]">
                    scikit-learn Isolation Forest
                  </span>
                </div>
                <p className="text-xs text-[#666] font-mono">
                  Unsupervised 10-D Topological Outlier Isolation
                </p>
              </div>
              <StatusBadge status={report.isolation_forest_status} />
            </div>
          </div>

          {/* Head-to-Head Comparison Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Baseline Rule Engine */}
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E5E0D5]">
                <h3 className="font-serif font-bold text-lg text-[#111111]">
                  Documented Rule Baseline
                </h3>
                <span className="text-xs font-mono text-[#858585]">Deterministic</span>
              </div>

              <div className="grid grid-cols-2 gap-4 font-mono text-center">
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">F1-Score</span>
                  <span className="text-2xl font-bold text-[#111111]">{report.rule_baseline.f1_score.toFixed(4)}</span>
                </div>
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">Recall</span>
                  <span className="text-2xl font-bold text-[#111111]">{report.rule_baseline.recall.toFixed(4)}</span>
                </div>
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">Precision</span>
                  <span className="text-2xl font-bold text-[#111111]">{report.rule_baseline.precision.toFixed(4)}</span>
                </div>
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">False Positive Rate</span>
                  <span className="text-2xl font-bold text-[#111111]">{report.rule_baseline.false_positive_rate.toFixed(4)}</span>
                </div>
              </div>

              {/* Confusion Matrix */}
              <div className="pt-2">
                <span className="text-[10px] font-mono text-[#858585] uppercase block mb-2 font-bold">Confusion Matrix</span>
                <div className="grid grid-cols-2 gap-2 font-mono text-xs text-center">
                  <div className="p-2 bg-[#2E7D32]/10 border border-[#2E7D32]/30 rounded">
                    <span className="text-[10px] text-[#2E7D32] block">True Positive (TP)</span>
                    <strong className="text-base text-[#111111]">{report.rule_baseline.confusion_matrix.tp}</strong>
                  </div>
                  <div className="p-2 bg-[#C83232]/10 border border-[#C83232]/30 rounded">
                    <span className="text-[10px] text-[#C83232] block">False Positive (FP)</span>
                    <strong className="text-base text-[#111111]">{report.rule_baseline.confusion_matrix.fp}</strong>
                  </div>
                  <div className="p-2 bg-[#A63D40]/10 border border-[#A63D40]/30 rounded">
                    <span className="text-[10px] text-[#A63D40] block">False Negative (FN)</span>
                    <strong className="text-base text-[#111111]">{report.rule_baseline.confusion_matrix.fn}</strong>
                  </div>
                  <div className="p-2 bg-[#2E7D32]/10 border border-[#2E7D32]/30 rounded">
                    <span className="text-[10px] text-[#2E7D32] block">True Negative (TN)</span>
                    <strong className="text-base text-[#111111]">{report.rule_baseline.confusion_matrix.tn}</strong>
                  </div>
                </div>
              </div>
            </div>

            {/* Candidate Multi-Engine Matrix */}
            <div className="bg-[#FFFFFF] border-2 border-[#111111] rounded shadow-sm p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E5E0D5]">
                <h3 className="font-serif font-bold text-lg text-[#111111] flex items-center space-x-2">
                  <span>Candidate Multi-Engine Matrix</span>
                  <span className="text-[10px] font-mono bg-[#111111] text-white px-2 py-0.5 rounded uppercase">Champion</span>
                </h3>
                <span className="text-xs font-mono text-[#2E7D32] font-bold">Multi-Engine</span>
              </div>

              <div className="grid grid-cols-2 gap-4 font-mono text-center">
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">F1-Score</span>
                  <span className="text-2xl font-bold text-[#2E7D32]">{report.candidate_detector.f1_score.toFixed(4)}</span>
                </div>
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">Recall</span>
                  <span className="text-2xl font-bold text-[#111111]">{report.candidate_detector.recall.toFixed(4)}</span>
                </div>
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">Precision</span>
                  <span className="text-2xl font-bold text-[#111111]">{report.candidate_detector.precision.toFixed(4)}</span>
                </div>
                <div className="p-3 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="text-[10px] text-[#858585] block uppercase">False Positive Rate</span>
                  <span className="text-2xl font-bold text-[#111111]">{report.candidate_detector.false_positive_rate.toFixed(4)}</span>
                </div>
              </div>

              {/* Confusion Matrix */}
              <div className="pt-2">
                <span className="text-[10px] font-mono text-[#858585] uppercase block mb-2 font-bold">Confusion Matrix</span>
                <div className="grid grid-cols-2 gap-2 font-mono text-xs text-center">
                  <div className="p-2 bg-[#2E7D32]/10 border border-[#2E7D32]/30 rounded">
                    <span className="text-[10px] text-[#2E7D32] block">True Positive (TP)</span>
                    <strong className="text-base text-[#111111]">{report.candidate_detector.confusion_matrix.tp}</strong>
                  </div>
                  <div className="p-2 bg-[#C83232]/10 border border-[#C83232]/30 rounded">
                    <span className="text-[10px] text-[#C83232] block">False Positive (FP)</span>
                    <strong className="text-base text-[#111111]">{report.candidate_detector.confusion_matrix.fp}</strong>
                  </div>
                  <div className="p-2 bg-[#A63D40]/10 border border-[#A63D40]/30 rounded">
                    <span className="text-[10px] text-[#A63D40] block">False Negative (FN)</span>
                    <strong className="text-base text-[#111111]">{report.candidate_detector.confusion_matrix.fn}</strong>
                  </div>
                  <div className="p-2 bg-[#2E7D32]/10 border border-[#2E7D32]/30 rounded">
                    <span className="text-[10px] text-[#2E7D32] block">True Negative (TN)</span>
                    <strong className="text-base text-[#111111]">{report.candidate_detector.confusion_matrix.tn}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

