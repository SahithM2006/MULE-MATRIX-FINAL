import React from 'react';
import { PageTab } from '../types';
import { 
  ShieldAlert, 
  GitFork, 
  Cpu, 
  FileText, 
  Sliders, 
  Activity, 
  Search, 
  Database, 
  Radio, 
  FileCheck2, 
  History,
  Lock,
  Layers
} from 'lucide-react';

interface NavbarProps {
  currentTab: PageTab;
  onSelectTab: (tab: PageTab) => void;
  activeAccountId: string | null;
  activeCaseId: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  activeAccountId,
  activeCaseId
}) => {
  const groups: Array<{
    label: string;
    items: Array<{ id: PageTab; label: string; icon: React.FC<{ className?: string }> }>;
  }> = [
    {
      label: 'OBSERVE',
      items: [
        { id: 'sentinel', label: 'Sentinel Command', icon: Radio },
        { id: 'stream', label: 'Threat Stream', icon: Search }
      ]
    },
    {
      label: 'TRACE',
      items: [
        { id: 'graph', label: 'Attack Graph', icon: GitFork },
        { id: 'forensics', label: 'Token Forensics', icon: Layers }
      ]
    },
    {
      label: 'DETECT',
      items: [
        { id: 'detection', label: 'Detection Lab', icon: Cpu },
        { id: 'observatory', label: 'Model Observatory', icon: Activity }
      ]
    },
    {
      label: 'RESPOND',
      items: [
        { id: 'incident', label: 'Incident Response', icon: ShieldAlert },
        { id: 'vault', label: 'Evidence Vault', icon: FileCheck2 },
        { id: 'audit', label: 'Audit Ledger', icon: Lock }
      ]
    },
    {
      label: 'UTILITIES',
      items: [
        { id: 'simulator', label: 'Scenario Simulator', icon: Database },
        { id: 'replay', label: 'Chronological Replay', icon: History },
        { id: 'settings', label: 'Rules & Limits', icon: Sliders },
        { id: 'health', label: 'System Health', icon: FileText }
      ]
    }
  ];

  return (
    <header className="border-b border-[#D8D2C4] bg-[#F4F1E9] sticky top-0 z-50">
      {/* Brand & Active Focus Bar */}
      <div className="max-w-[1728px] mx-auto px-6 py-3 flex items-center justify-between border-b border-[#E5E0D5]">
        <div className="flex items-center space-x-6">
          <div className="flex items-baseline space-x-2">
            <span className="font-display text-xl font-bold tracking-widest text-[#111111]">
              MULE MATRIX
            </span>
            <span className="text-[10px] font-mono uppercase tracking-widest text-[#C6A45A] px-1.5 py-0.5 bg-[#171A1F] rounded">
              v1.0 · CORE
            </span>
          </div>
          <span className="text-xs text-[#858585] hidden md:inline font-serif italic">
            Unified Financial Investigation · Eight Algorithmic Engines
          </span>
        </div>

        {/* Global Entity Context Pill */}
        <div className="flex items-center space-x-4">
          {activeAccountId && (
            <div className="flex items-center space-x-2 text-xs font-mono bg-[#FFFFFF] border border-[#D8D2C4] px-2.5 py-1 rounded shadow-sm">
              <span className="text-[#858585]">TARGET:</span>
              <span className="font-bold text-[#111111]">{activeAccountId}</span>
              <button 
                onClick={() => onSelectTab('detection')} 
                className="text-[10px] text-[#7596C8] hover:underline uppercase"
              >
                Inspect
              </button>
            </div>
          )}

          {activeCaseId && (
            <div className="flex items-center space-x-2 text-xs font-mono bg-[#FFFFFF] border border-[#D8D2C4] px-2.5 py-1 rounded shadow-sm">
              <span className="text-[#858585]">CASE:</span>
              <span className="font-bold text-[#A63D40]">{activeCaseId}</span>
              <button 
                onClick={() => onSelectTab('incident')} 
                className="text-[10px] text-[#A63D40] hover:underline uppercase"
              >
                View
              </button>
            </div>
          )}

          <div className="flex items-center space-x-2 pl-2 border-l border-[#D8D2C4]">
            <span className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
            <span className="text-[11px] font-mono text-[#555] uppercase">Live Matrix</span>
          </div>
        </div>
      </div>

      {/* Swiss Editorial Navigation Categories */}
      <nav className="max-w-[1728px] mx-auto px-6 overflow-x-auto">
        <div className="flex space-x-8 py-2">
          {groups.map((grp) => (
            <div key={grp.label} className="flex items-center space-x-1">
              <span className="text-[10px] font-mono font-bold tracking-wider text-[#A09A8E] mr-2">
                {grp.label}
              </span>
              <div className="flex space-x-1">
                {grp.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => onSelectTab(item.id)}
                      className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-[#111111] text-[#FFFFFF] shadow-sm font-semibold'
                          : 'text-[#444444] hover:bg-[#EAE5D9] hover:text-[#111111]'
                      }`}
                    >
                      <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#C6A45A]' : 'text-[#858585]'}`} />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </nav>
    </header>
  );
};

