import React from 'react';

interface RiskGaugeProps {
  score: number;
  tier: string;
  size?: number;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, tier, size = 160 }) => {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;

  let color = '#2E7D32'; // Green
  if (score >= 75) color = '#C83232'; // Critical Red
  else if (score >= 50) color = '#A63D40'; // High Burgundy
  else if (score >= 25) color = '#C6A45A'; // Medium Gold

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E0D5"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="font-serif text-3xl font-bold tracking-tight text-[#111111]">
          {score.toFixed(1)}
        </span>
        <span className="font-mono text-[10px] tracking-widest text-[#858585] uppercase mt-0.5">
          {tier} RISK
        </span>
      </div>
    </div>
  );
};

