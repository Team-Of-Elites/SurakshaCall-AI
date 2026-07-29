import React from 'react';
import { Lock, EyeOff, Cpu } from 'lucide-react';

interface Props {
  fingerprint: string;
}

export const PrivacyPanel: React.FC<Props> = ({ fingerprint }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-slate-300">
      <div className="flex items-center gap-2 text-emerald-400 font-medium text-sm mb-3">
        <Lock className="w-4 h-4" />
        <span>Privacy-First Multi-Agent Architecture</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span>Local Whisper STT</span>
        </div>
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center gap-2">
          <EyeOff className="w-4 h-4 text-purple-400" />
          <span>Zero Audio Uploaded</span>
        </div>
      </div>
      <div className="mt-3 text-[11px] text-slate-500 font-mono">
        Behavioral Fingerprint: {fingerprint}
      </div>
    </div>
  );
};