import React, { useEffect, useState } from 'react';
import { CaseDetail } from '../types';
import { api } from '../services/api';
import { 
  FileCheck2, 
  Download, 
  ExternalLink, 
  ShieldCheck, 
  Hash, 
  Clock, 
  RefreshCw,
  Eye,
  X 
} from 'lucide-react';

interface EvidenceVaultProps {
  initialCaseId?: string | null;
}

export const EvidenceVault: React.FC<EvidenceVaultProps> = ({ initialCaseId }) => {
  const [cases, setCases] = useState<CaseDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.getCases();
      setCases(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Collect all artifacts across cases
  const artifactsList: Array<{
    case_number: string;
    case_title: string;
    case_id: string;
    artifact_id: string;
    artifact_type: string;
    title: string;
    hash: string;
  }> = [];

  cases.forEach((c) => {
    c.artifacts.forEach((art) => {
      artifactsList.push({
        case_number: c.case_number,
        case_title: c.title,
        case_id: c.id,
        artifact_id: art.id,
        artifact_type: art.type,
        title: art.title,
        hash: art.hash
      });
    });
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Title */}
      <div className="border-b border-[#D8D2C4] pb-4 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#858585] uppercase mb-1">
            Forensic Evidence Repository
          </div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
            Evidence Vault & Dossiers
          </h1>
          <p className="text-sm text-[#666] mt-0.5 max-w-3xl">
            Downloadable standalone HTML dossiers and verified JSON packages containing reconstructed flow paths, SHA-256 audit roots, and model explanations.
          </p>
        </div>

        <div className="text-xs font-mono text-[#858585]">
          {artifactsList.length} Authenticated Artifacts
        </div>
      </div>

      {loading && (
        <div className="py-20 text-center text-[#858585]">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-[#111111]" />
          <span className="font-serif text-lg">Polling Evidence Vault...</span>
        </div>
      )}

      {!loading && artifactsList.length === 0 && (
        <div className="bg-[#FFFFFF] border border-[#D8D2C4] rounded p-12 text-center text-xs font-mono text-[#858585]">
          No forensic dossiers exported yet. Open a case in Incident Response and click "Export Dossier".
        </div>
      )}

      {/* Artifacts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {artifactsList.map((art) => {
          const downloadUrl = `/api/v1/respond/evidence/${art.artifact_id}/download`;

          return (
            <div key={art.artifact_id} className="bg-[#FFFFFF] border border-[#D8D2C4] rounded shadow-sm p-5 space-y-4">
              <div className="flex items-start justify-between gap-4 pb-3 border-b border-[#E5E0D5]">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-[#858585]">{art.case_number}</span>
                    <span className="text-[10px] font-mono bg-[#EAE6DC] text-[#333] px-2 py-0.5 rounded font-bold uppercase">
                      {art.artifact_type}
                    </span>
                  </div>
                  <h3 className="font-serif font-bold text-base text-[#111111]">
                    {art.title}
                  </h3>
                  <div className="text-xs text-[#666]">{art.case_title}</div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={() => setPreviewUrl(downloadUrl)}
                    title="Preview Dossier"
                    className="p-2 border border-[#D8D2C4] hover:bg-[#FAF9F5] rounded text-[#111111] transition"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <a
                    href={downloadUrl}
                    download
                    title="Download Evidence File"
                    className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#111111] text-white hover:bg-[#333] rounded text-xs font-mono uppercase tracking-wider transition font-medium"
                  >
                    <Download className="w-3.5 h-3.5 text-[#C6A45A]" />
                    <span>Download</span>
                  </a>
                </div>
              </div>

              {/* SHA-256 Digest */}
              <div className="text-xs font-mono bg-[#FAF9F5] p-2.5 rounded border border-[#E5E0D5] space-y-1">
                <span className="text-[10px] text-[#858585] uppercase block flex items-center space-x-1 font-bold">
                  <Hash className="w-3 h-3" />
                  <span>SHA-256 Content Authentication Digest</span>
                </span>
                <span className="text-[#111111] break-all block text-[11px]">
                  {art.hash}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Standalone HTML Dossier Preview Modal */}
      {previewUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#FFFFFF] w-full max-w-5xl h-[85vh] rounded-md shadow-2xl flex flex-col overflow-hidden border border-[#D8D2C4]">
            <div className="p-4 bg-[#111111] text-white flex items-center justify-between">
              <span className="font-serif font-bold text-base">
                Forensic Evidence Dossier Live Preview
              </span>
              <button
                onClick={() => setPreviewUrl(null)}
                className="p-1 hover:bg-[#333] rounded text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <iframe
              src={previewUrl}
              title="Forensic Evidence Dossier"
              className="w-full flex-1 border-0"
            />
          </div>
        </div>
      )}
    </div>
  );
};

