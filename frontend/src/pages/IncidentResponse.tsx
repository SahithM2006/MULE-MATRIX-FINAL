import React, { useEffect, useState } from 'react';
import { CaseDetail } from '../types';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { 
  ShieldAlert, 
  FileCheck2, 
  PlusCircle, 
  Send, 
  Clock, 
  UserCheck, 
  ArrowRight,
  RefreshCw,
  Cpu 
} from 'lucide-react';

interface IncidentResponseProps {
  initialCaseId?: string | null;
  onNavigateToVault: (caseId: string) => void;
  onInvestigateAccount: (accountId: string) => void;
}

export const IncidentResponse: React.FC<IncidentResponseProps> = ({
  initialCaseId,
  onNavigateToVault,
  onInvestigateAccount
}) => {
  const [cases, setCases] = useState<CaseDetail[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  
  // Note creation form
  const [newNote, setNewNote] = useState('');
  const [author, setAuthor] = useState('Forensic Analyst');

  // Status transition form
  const [newStatus, setNewStatus] = useState('');
  const [transitionReason, setTransitionReason] = useState('');

  // Export state
  const [exporting, setExporting] = useState(false);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  const loadCases = async () => {
    try {
      setLoading(true);
      const data = await api.getCases(statusFilter || undefined);
      setCases(data);
      if (data.length > 0) {
        if (initialCaseId) {
          const match = data.find((c) => c.id === initialCaseId || c.case_number === initialCaseId);
          setSelectedCase(match || data[0]);
        } else if (!selectedCase) {
          setSelectedCase(data[0]);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [statusFilter]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCase || !newNote.trim()) return;
    try {
      await api.addCaseNote(selectedCase.id, { author, note_text: newNote });
      newNote && setNewNote('');
      const updated = await api.getCaseDetail(selectedCase.id);
      setSelectedCase(updated);
      loadCases();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCase || !newStatus) return;
    try {
      const updated = await api.updateCaseStatus(selectedCase.id, {
        status: newStatus,
        assigned_to: author,
        status_change_reason: transitionReason || undefined
      });
      setSelectedCase(updated);
      setNewStatus('');
      setTransitionReason('');
      loadCases();
    } catch (err) {
      console.error(err);
    }
  };

  const handleExportDossier = async () => {
    if (!selectedCase) return;
    try {
      setExporting(true);
      setExportNotice(null);
      const res = await api.exportEvidenceDossier(selectedCase.id);
      setExportNotice(`Forensic dossier exported successfully (SHA256: ${res.content_hash.slice(0, 16)}...).`);
      loadCases();
      onNavigateToVault(selectedCase.id);
    } catch (err: any) {
      setExportNotice(`Export failed: ${err.message}`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Section 10 · Case Management
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Incident Response Command
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Formal forensic case tracking linked directly to observed transaction flows, algorithmic signals, and immutable audit logs.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#FFFFFF] border border-[#D8D2C4] rounded px-3 py-1.5 text-xs font-mono"
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="IN_REVIEW">In Review</option>
            <option value="ESCALATED">Escalated</option>
            <option value="FROZEN">Frozen</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
      </div>

      {exportNotice && (
        <div className="p-3 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono text-[#111111] flex items-center justify-between">
          <span>{exportNotice}</span>
          <button onClick={() => setExportNotice(null)} className="text-[#858585] hover:text-[#111111]">✕</button>
        </div>
      )}

      {/* Main Dual Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Case List (1 col) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-[#D8D2C4]">
            <h3 className="font-serif font-bold text-sm text-[#111111] uppercase tracking-wider">
              Investigation Cases ({cases.length})
            </h3>
          </div>

          <div className="space-y-2.5 max-h-[700px] overflow-y-auto">
            {cases.length === 0 ? (
              <div className="bg-[#FFFFFF] border border-[#D8D2C4] p-6 rounded text-center text-xs font-mono text-[#858585]">
                No incident cases registered.
              </div>
            ) : (
              cases.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setSelectedCase(c)}
                  className={`p-4 rounded border transition cursor-pointer ${
                    selectedCase?.id === c.id
                      ? 'bg-[#FFFFFF] border-[#111111] shadow-md ring-1 ring-[#111111]'
                      : 'bg-[#FFFFFF] border-[#D8D2C4] hover:bg-[#FAF9F5]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-xs font-bold text-[#111111]">
                      {c.case_number}
                    </span>
                    <StatusBadge status={c.status} type="case" />
                  </div>
                  <h4 className="font-serif font-bold text-sm text-[#111111] line-clamp-1 mb-1">
                    {c.title}
                  </h4>
                  <div className="text-[11px] font-mono text-[#666] flex justify-between">
                    <span>Target: {c.primary_account_number || c.primary_account_id}</span>
                    <span className="text-[#858585]">{new Date(c.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Selected Case Workspace (2 cols) */}
        {selectedCase ? (
          <div className="lg:col-span-2 space-y-6">
            {/* Header Details Card */}
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E5E0D5]">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-[#858585]">{selectedCase.case_number}</span>
                    <StatusBadge status={selectedCase.status} type="case" />
                    <span className="text-xs font-mono text-[#A63D40] font-bold">● {selectedCase.priority} PRIORITY</span>
                  </div>
                  <h2 className="font-serif text-2xl font-bold text-[#111111] mt-1">
                    {selectedCase.title}
                  </h2>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={handleExportDossier}
                    disabled={exporting}
                    className="flex items-center space-x-1.5 px-4 py-2 bg-[#111111] text-white hover:bg-[#333] rounded text-xs font-mono uppercase tracking-wider transition font-semibold"
                  >
                    {exporting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileCheck2 className="w-3.5 h-3.5 text-[#C6A45A]" />}
                    <span>Export Dossier</span>
                  </button>
                </div>
              </div>

              {/* Target Entity Meta */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono bg-[#FAF9F5] p-3.5 rounded border border-[#E5E0D5]">
                <div>
                  <span className="text-[#858585] text-[10px] uppercase block">Primary Account</span>
                  <button
                    onClick={() => onInvestigateAccount(selectedCase.primary_account_id)}
                    className="font-bold text-[#111111] hover:text-[#7596C8] hover:underline"
                  >
                    {selectedCase.primary_account_number || selectedCase.primary_account_id}
                  </button>
                </div>
                <div>
                  <span className="text-[#858585] text-[10px] uppercase block">Holder</span>
                  <span className="text-[#111111]">{selectedCase.primary_holder_name || 'Mule Syndicate Node'}</span>
                </div>
                <div>
                  <span className="text-[#858585] text-[10px] uppercase block">Assigned Lead</span>
                  <span className="text-[#111111]">{selectedCase.assigned_to}</span>
                </div>
                <div>
                  <span className="text-[#858585] text-[10px] uppercase block">Artifacts</span>
                  <span className="text-[#111111]">{selectedCase.artifacts.length} Packages</span>
                </div>
              </div>

              {/* Preliminary Findings Summary */}
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-[#858585] mb-1 block font-bold">
                  Investigative Finding Summary
                </span>
                <p className="text-sm font-serif text-[#222] leading-relaxed bg-[#FFFFFF] p-3 rounded border border-[#ECE8DE]">
                  {selectedCase.findings_summary}
                </p>
              </div>

              {/* Status Transition Control */}
              <form onSubmit={handleUpdateStatus} className="pt-3 border-t border-[#E5E0D5] flex flex-wrap items-center gap-3">
                <span className="text-xs font-mono text-[#858585]">Change State:</span>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="bg-[#FAF9F5] border border-[#D8D2C4] rounded px-3 py-1.5 text-xs font-mono focus:outline-none"
                >
                  <option value="">Select New Status...</option>
                  <option value="NEW">New</option>
                  <option value="IN_REVIEW">In Review</option>
                  <option value="ESCALATED">Escalated</option>
                  <option value="FROZEN">Account Frozen</option>
                  <option value="CLOSED">Closed Resolved</option>
                </select>

                <input
                  type="text"
                  value={transitionReason}
                  onChange={(e) => setTransitionReason(e.target.value)}
                  placeholder="Audit reason for status transition..."
                  className="flex-1 min-w-[200px] px-3 py-1.5 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-mono focus:outline-none"
                />

                <button
                  type="submit"
                  disabled={!newStatus}
                  className="px-3 py-1.5 bg-[#171A1F] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition disabled:opacity-50"
                >
                  Commit Status
                </button>
              </form>
            </div>

            {/* Notes & Chronological Audit Timeline */}
            <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-6 space-y-6">
              <h3 className="font-serif font-bold text-lg text-[#111111] pb-2 border-b border-[#E5E0D5]">
                Investigative Chronology & Notes ({selectedCase.notes.length})
              </h3>

              <div className="space-y-4">
                {selectedCase.notes.map((note) => (
                  <div key={note.id} className="p-3.5 bg-[#FAF9F5] rounded border border-[#E5E0D5] space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="font-bold text-[#111111]">{note.author}</span>
                      <span className="text-[#858585]">{new Date(note.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-xs font-serif text-[#333] leading-relaxed">
                      {note.note_text}
                    </p>
                  </div>
                ))}

                {selectedCase.notes.length === 0 && (
                  <div className="text-center py-6 text-xs font-mono text-[#858585]">
                    No analytical notes recorded for this case.
                  </div>
                )}
              </div>

              {/* Add Note Form */}
              <form onSubmit={handleAddNote} className="pt-4 border-t border-[#E5E0D5] space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-[#858585]">
                  <span>Log Investigative Finding:</span>
                  <input
                    type="text"
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                    className="bg-transparent border-b border-[#D8D2C4] px-1 text-right text-[#111111] font-bold"
                  />
                </div>
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Record transactional evidence, subpoena notes, or off-ramp freeze confirmations..."
                  rows={3}
                  className="w-full p-3 bg-[#FAF9F5] border border-[#D8D2C4] rounded text-xs font-serif focus:outline-none focus:border-[#111111]"
                />
                <button
                  type="submit"
                  disabled={!newNote.trim()}
                  className="flex items-center space-x-1.5 px-4 py-2 bg-[#111111] text-white rounded text-xs font-mono uppercase tracking-wider hover:bg-[#333] transition disabled:opacity-50 ml-auto"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Append Note</span>
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div className="lg:col-span-2 bg-[#FFFFFF] border border-[#D8D2C4] rounded p-12 text-center text-xs font-mono text-[#858585]">
            Select an incident case to review findings, notes, and evidence packages.
          </div>
        )}
      </div>
    </div>
  );
};

