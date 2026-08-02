import React from 'react';
import { ShieldAlert, AlertTriangle } from 'lucide-react';

interface Props {
  score: number;
  threatLevel: string;
}

export const RiskHero: React.FC<Props> = ({ score, threatLevel }) => {
  const getBadgeColor = () => {
    if (score >= 80) return 'bg-red-500/20 text-red-400 border-red-500/50';
    if (score >= 50) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
    return 'bg-green-500/20 text-green-400 border-green-500/50';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-white shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" />
          <h2 className="text-xl font-bold tracking-wide">Scam Threat Assessment</h2>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getBadgeColor()}`}>
          {threatLevel} RISK
        </span>
      </div>

      <div className="flex items-center gap-6 mt-4">
        <div className="text-5xl font-extrabold text-red-500">
          {score}<span className="text-2xl text-slate-400">%</span>
        </div>
        <div className="flex-1">
          <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-yellow-500 to-red-600 h-full transition-all duration-500"
              style={{ width: `${score}%` }}
            />
          </div>
          <p className="text-xs text-slate-400 mt-2">
            High confidence psychological manipulation detected in live speech stream.
          </p>
        </div>
      </div>
    </div>
  );
};