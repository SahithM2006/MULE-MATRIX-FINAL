import React, { useState } from 'react';
import { PageTab } from './types';
import { Navbar } from './components/Navbar';
import { SentinelCommand } from './pages/SentinelCommand';
import { ThreatStream } from './pages/ThreatStream';
import { AttackGraph } from './pages/AttackGraph';
import { TokenForensics } from './pages/TokenForensics';
import { DetectionLab } from './pages/DetectionLab';
import { ModelObservatory } from './pages/ModelObservatory';
import { IncidentResponse } from './pages/IncidentResponse';
import { EvidenceVault } from './pages/EvidenceVault';
import { AuditLedger } from './pages/AuditLedger';
import { ScenarioSimulator } from './pages/ScenarioSimulator';
import { InvestigationReplay } from './pages/InvestigationReplay';
import { SettingsRules } from './pages/SettingsRules';
import { SystemHealth } from './pages/SystemHealth';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<PageTab>('sentinel');
  const [activeAccountId, setActiveAccountId] = useState<string | null>('acc_mule_001');
  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);
  const [activeTokenId, setActiveTokenId] = useState<string>('eINR_TOKEN_101_9921');

  // Cross-page navigation handlers
  const handleInvestigateAccount = (accountId: string) => {
    setActiveAccountId(accountId);
    setCurrentTab('detection');
  };

  const handleTraceFlow = (accountId: string) => {
    setActiveAccountId(accountId);
    setCurrentTab('graph');
  };

  const handleInspectToken = (tokenId: string) => {
    setActiveTokenId(tokenId);
    setCurrentTab('forensics');
  };

  const handleOpenCase = (accountId: string, summary: string) => {
    setActiveAccountId(accountId);
    setCurrentTab('incident');
  };

  const handleNavigateToVault = (caseId: string) => {
    setActiveCaseId(caseId);
    setCurrentTab('vault');
  };

  const handleInvestigateScenario = (scenarioId: string) => {
    setCurrentTab('stream');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F4F1E9] text-[#111111]">
      {/* Swiss Editorial Navigation Shell */}
      <Navbar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        activeAccountId={activeAccountId}
        activeCaseId={activeCaseId}
      />

      {/* Main Workspace Canvas */}
      <main className="flex-1 max-w-[1728px] w-full mx-auto p-6 md:p-8">
        {currentTab === 'sentinel' && (
          <SentinelCommand
            onInvestigateAccount={handleInvestigateAccount}
            onNavigateToSimulator={() => setCurrentTab('simulator')}
            onNavigateToStream={() => setCurrentTab('stream')}
          />
        )}

        {currentTab === 'stream' && (
          <ThreatStream
            onInvestigateAccount={handleInvestigateAccount}
            onTraceFlow={handleTraceFlow}
            onInspectToken={handleInspectToken}
          />
        )}

        {currentTab === 'graph' && (
          <AttackGraph
            initialAccountId={activeAccountId || 'acc_mule_001'}
            onNavigateToDetect={handleInvestigateAccount}
            onNavigateToCase={(accId) => handleOpenCase(accId, 'Attack graph investigation escalation.')}
            onNavigateToLineage={handleInspectToken}
          />
        )}

        {currentTab === 'forensics' && (
          <TokenForensics
            initialTokenId={activeTokenId}
            onInvestigateAccount={handleInvestigateAccount}
          />
        )}

        {currentTab === 'detection' && (
          <DetectionLab
            initialAccountId={activeAccountId || 'acc_mule_001'}
            onNavigateToTrace={handleTraceFlow}
            onNavigateToCase={handleOpenCase}
          />
        )}

        {currentTab === 'observatory' && <ModelObservatory />}

        {currentTab === 'incident' && (
          <IncidentResponse
            initialCaseId={activeCaseId}
            onNavigateToVault={handleNavigateToVault}
            onInvestigateAccount={handleInvestigateAccount}
          />
        )}

        {currentTab === 'vault' && (
          <EvidenceVault initialCaseId={activeCaseId} />
        )}

        {currentTab === 'audit' && <AuditLedger />}

        {currentTab === 'simulator' && (
          <ScenarioSimulator onInvestigateScenario={handleInvestigateScenario} />
        )}

        {currentTab === 'replay' && (
          <InvestigationReplay onInvestigateAccount={handleInvestigateAccount} />
        )}

        {currentTab === 'settings' && <SettingsRules />}

        {currentTab === 'health' && <SystemHealth />}
      </main>

      {/* Swiss Editorial Colophon / Footer */}
      <footer className="border-t border-[#D8D2C4] bg-[#EFECE3] py-6 px-6 text-xs font-mono text-[#858585]">
        <div className="max-w-[1728px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <span className="font-display font-bold text-[#111111]">MULE MATRIX</span>
            <span>·</span>
            <span>Independent Forensic Financial Investigation System</span>
          </div>
          <div className="flex items-center space-x-6">
            <span>FastAPI · React · PyTorch GraphSAGE · Cytoscape.js</span>
            <span className="text-[#111111] font-bold">SHA-256 Verified Ledger</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
