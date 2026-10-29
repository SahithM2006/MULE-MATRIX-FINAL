import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Activity, 
  Database, 
  Cpu, 
  CheckCircle2, 
  RefreshCw, 
  Server, 
  HardDrive 
} from 'lucide-react';

export const SystemHealth: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);

  const loadHealth = async () => {
    try {
      setLoading(true);
      const data = await api.getSystemHealth();
      setHealth(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSeed = async () => {
    try {
      setSeeding(true);
      await api.seedDataset();
      loadHealth();
    } catch (err) {
      console.error(err);
    } finally {
      setSeeding(false);
    }
  };

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Section 10 · Core Infrastructure
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            System Health & Infrastructure
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Live operational status of backend services, SQLite application database, and the eight algorithmic engines.
          </p>
        </div>

        <button
          onClick={loadHealth}
          className="flex items-center space-x-2 px-4 py-2 border border-[#D8D2C4] bg-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#FAF9F5]"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Status</span>
        </button>
      </div>

      {loading && !health && (
        <div className="py-20 text-center text-[#858585]">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-[#111111]" />
          <span className="font-serif text-lg">Probing System Telemetry...</span>
        </div>
      )}

      {health && (
        <div className="space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-5 rounded shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-[#858585] uppercase">FastAPI Backend</span>
                <div className="font-serif text-xl font-bold text-[#111111]">
                  Operational Online
                </div>
                <span className="text-xs font-mono text-[#2E7D32]">● Uvicorn v0.54</span>
              </div>
              <Server className="w-8 h-8 text-[#7596C8]" />
            </div>

            <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-5 rounded shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-[#858585] uppercase">Database Engine</span>
                <div className="font-serif text-xl font-bold text-[#111111]">
                  SQLite 3 (WAL Mode)
                </div>
                <span className="text-xs font-mono text-[#555]">
                  {health.database.accounts_count} Accounts · {health.database.transactions_count} Txs
                </span>
              </div>
              <HardDrive className="w-8 h-8 text-[#C6A45A]" />
            </div>

            <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-5 rounded shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-[#858585] uppercase">Algorithmic Matrix</span>
                <div className="font-serif text-xl font-bold text-[#111111]">
                  8 / 8 Active Engines
                </div>
                <span className="text-xs font-mono text-[#2E7D32]">
                  ● All Engines Ready
                </span>
              </div>
              <Cpu className="w-8 h-8 text-[#2E7D32]" />
            </div>
          </div>

          {/* Engine Status Matrix */}
          <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
            <h3 className="font-serif font-bold text-lg text-[#111111] pb-2 border-b border-[#E5E0D5]">
              Algorithmic Engines Telemetry
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              {Object.entries(health.engines).map(([name, status]) => (
                <div key={name} className="flex items-center justify-between p-3.5 bg-[#FAF9F5] rounded border border-[#E5E0D5]">
                  <span className="font-bold text-[#111111]">
                    {name.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <StatusBadge status={String(status)} />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

