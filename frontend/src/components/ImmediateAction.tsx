import React from 'react';
import { ShieldCheck, PhoneOff, AlertCircle } from 'lucide-react';

interface Props {
  actions: string[];
}

export const ImmediateAction: React.FC<Props> = ({ actions }) => {
  return (
    <div className="bg-red-950/40 border border-red-900/60 rounded-xl p-5 text-white">
      <div className="flex items-center gap-2 mb-3 text-red-400 font-semibold text-sm">
        <AlertCircle className="w-5 h-5" />
        <span>LIVE COACHING & RECOMMENDED ACTIONS</span>
      </div>
      <ul className="space-y-2">
        {actions.map((action, idx) => (
          <li key={idx} className="flex items-start gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-800">
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <span className="text-sm text-slate-200 font-medium">{action}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};