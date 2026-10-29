import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'risk' | 'case' | 'lineage' | 'alert';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'risk' }) => {
  let bg = 'bg-[#ECEAE2] text-[#555] border-[#D8D4C8]';

  const s = status.toUpperCase();

  if (s === 'CRITICAL' || s === 'URGENT' || s === 'INTEGRITY_COMPROMISED') {
    bg = 'bg-[#C83232]/10 text-[#C83232] border-[#C83232]/30';
  } else if (s === 'HIGH' || s === 'SUSPICIOUS' || s === 'ESCALATED') {
    bg = 'bg-[#A63D40]/10 text-[#A63D40] border-[#A63D40]/30';
  } else if (s === 'MEDIUM' || s === 'WARNING' || s === 'IN_REVIEW') {
    bg = 'bg-[#C6A45A]/15 text-[#9C7A28] border-[#C6A45A]/30';
  } else if (s === 'LOW' || s === 'BENIGN' || s === 'VERIFIED_INTACT' || s === 'READY' || s === 'ONLINE' || s === 'SETTLED' || s === 'CLOSED') {
    bg = 'bg-[#2E7D32]/10 text-[#2E7D32] border-[#2E7D32]/30';
  } else if (s === 'NOT_TRAINED' || s === 'UNAVAILABLE') {
    bg = 'bg-[#858585]/10 text-[#858585] border-[#858585]/30';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono tracking-wider border font-medium uppercase ${bg}`}>
      {status}
    </span>
  );
};

