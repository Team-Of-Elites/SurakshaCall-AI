import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  PhoneOff, 
  Bot, 
  AlertTriangle, 
  Mic, 
  UserCheck, 
  Info, 
  Bell, 
  RotateCcw,
  Volume2
} from 'lucide-react';

interface TranscriptItem {
  id: string;
  speaker: 'Caller' | 'User';
  time: string;
  text: string;
  tactic?: string;
  explanation?: string;
}

const SCAM_FEEDS: TranscriptItem[] = [
  {
    id: '1',
    speaker: 'Caller',
    time: '12:01:05 PM',
    text: 'This is Officer Sharma from the National Cyber Crime Cell. Your bank account has been flagged for illicit activity.',
    tactic: 'Fake Authority',
    explanation: 'Impersonating law enforcement or government institutions to bypass critical thinking.'
  },
  {
    id: '2',
    speaker: 'User',
    time: '12:01:12 PM',
    text: "Wait, which account? I haven't received any email or official notice."
  },
  {
    id: '3',
    speaker: 'Caller',
    time: '12:01:22 PM',
    text: 'Do not interrupt. You must transfer the balance to a secure verification node within 10 minutes or your account will be frozen permanently. Do not inform anyone.',
    tactic: 'Artificial Urgency & Isolation',
    explanation: 'Creating high-stress time constraints and isolating the victim to prevent seeking help.'
  }
];

const SAFE_FEEDS: TranscriptItem[] = [
  {
    id: '1',
    speaker: 'Caller',
    time: '12:01:05 PM',
    text: 'Hello, this is HDFC Customer Care regarding your recent inquiry about a home loan interest rate update.'
  },
  {
    id: '2',
    speaker: 'User',
    time: '12:01:15 PM',
    text: 'Yes, I requested an callback online yesterday.'
  },
  {
    id: '3',
    speaker: 'Caller',
    time: '12:01:25 PM',
    text: 'Great! I can explain the new rates. We will never ask for your passwords or OTP over the phone.'
  }
];

export default function App() {
  const [scenario, setScenario] = useState<'scam' | 'safe' | 'reset'>('scam');
  const [selectedTactic, setSelectedTactic] = useState<TranscriptItem | null>(null);
  const [actionTriggered, setActionTriggered] = useState<string | null>(null);
  const [waveHeight, setWaveHeight] = useState<number[]>([40, 70, 30, 90, 50, 80, 20]);

  // Animate waveform sound bars
  useEffect(() => {
    if (scenario === 'reset') return;
    const interval = setInterval(() => {
      setWaveHeight(Array.from({ length: 7 }, () => Math.floor(Math.random() * 80) + 10));
    }, 200);
    return () => clearInterval(interval);
  }, [scenario]);

  const riskScore = scenario === 'scam' ? 94 : scenario === 'safe' ? 8 : 0;
  const currentFeed = scenario === 'scam' ? SCAM_FEEDS : scenario === 'safe' ? SAFE_FEEDS : [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">

        {/* TOP DEMO CONTROLS (PHASE 1) */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-xl">
          <div className="flex items-center gap-3">
            <Bot className="w-6 h-6 text-indigo-400" />
            <span className="font-semibold text-sm text-slate-300">Live Demo Simulation Controls:</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => { setScenario('scam'); setSelectedTactic(null); setActionTriggered(null); }}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
                scenario === 'scam' ? 'bg-red-600 text-white shadow-lg shadow-red-500/30' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
              }`}
            >
              Simulate Scam Call
            </button>
            <button
              onClick={() => { setScenario('safe'); setSelectedTactic(null); setActionTriggered(null); }}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
                scenario === 'safe' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/30' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
              }`}
            >
              Simulate Safe Call
            </button>
            <button
              onClick={() => { setScenario('reset'); setSelectedTactic(null); setActionTriggered(null); }}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg text-xs font-bold transition flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset
            </button>
          </div>
        </div>

        {/* HEADER BAR */}
        <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-3">
              <ShieldAlert className={`w-8 h-8 ${scenario === 'scam' ? 'text-red-500' : 'text-emerald-400'}`} />
              <h1 className="text-2xl font-bold tracking-tight">AI Scam Interceptor</h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">Psychology & Behavioral Analysis Engine • Real-time Protection</p>
          </div>

          {/* AUDIO WAVEFORM & STT STATUS (PHASE 2) */}
          <div className="flex items-center gap-4 bg-slate-900 px-4 py-2 rounded-full border border-slate-800">
            {scenario !== 'reset' && (
              <div className="flex items-end gap-1 h-5">
                {waveHeight.map((h, i) => (
                  <div
                    key={i}
                    className={`w-1 rounded-full transition-all duration-150 ${scenario === 'scam' ? 'bg-red-500' : 'bg-emerald-500'}`}
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${scenario === 'scam' ? 'bg-red-400' : 'bg-emerald-400'}`}></span>
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${scenario === 'scam' ? 'bg-red-500' : 'bg-emerald-500'}`}></span>
              </span>
              <span className="text-xs font-semibold text-slate-300">
                {scenario === 'reset' ? 'Idle' : 'Live Speech STT Active'}
              </span>
            </div>
          </div>
        </header>

        {/* ACTION TRIGGER NOTIFICATION BANNER */}
        {actionTriggered && (
          <div className="bg-indigo-950 border border-indigo-500 text-indigo-200 p-4 rounded-xl flex items-center justify-between animate-fade-in">
            <div className="flex items-center gap-3">
              <Bot className="w-5 h-5 text-indigo-400" />
              <span className="text-sm font-medium">{actionTriggered}</span>
            </div>
            <button onClick={() => setActionTriggered(null)} className="text-xs underline text-indigo-300">Dismiss</button>
          </div>
        )}

        {/* MAIN DASHBOARD GRID */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* THREAT ASSESSMENT CARD */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold flex items-center gap-2">
                  <AlertTriangle className={scenario === 'scam' ? 'text-red-500' : 'text-emerald-400'} />
                  Scam Threat Assessment
                </h2>
                <span className={`px-3 py-1 rounded-full text-xs font-black tracking-wider uppercase ${
                  scenario === 'scam' ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 
                  scenario === 'safe' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-slate-800 text-slate-400'
                }`}>
                  {scenario === 'scam' ? 'Critical Risk' : scenario === 'safe' ? 'Low Risk' : 'Standby'}
                </span>
              </div>

              <div className="mt-6 flex items-baseline gap-2">
                <span className={`text-6xl font-black ${scenario === 'scam' ? 'text-red-500' : scenario === 'safe' ? 'text-emerald-400' : 'text-slate-600'}`}>
                  {riskScore}%
                </span>
                <span className="text-xs text-slate-400">Threat Score</span>
              </div>

              {/* RISK BAR */}
              <div className="w-full bg-slate-800 h-3 rounded-full mt-4 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-700 ${scenario === 'scam' ? 'bg-gradient-to-r from-orange-500 to-red-600' : 'bg-emerald-500'}`}
                  style={{ width: `${riskScore}%` }}
                />
              </div>

              <p className="text-xs text-slate-400 mt-4 leading-relaxed">
                {scenario === 'scam' 
                  ? 'High confidence psychological manipulation detected in live speech stream. Immediate intervention advised.'
                  : scenario === 'safe' 
                  ? 'Standard verification dialogue detected. No malicious persuasion or coercive tactics found.'
                  : 'Awaiting incoming call stream audio for behavioral evaluation.'}
              </p>
            </div>
          </div>

          {/* LIVE COACHING & ACTION BUTTONS (PHASE 4) */}
          <div className="bg-red-950/20 border border-red-900/40 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-bold text-red-400 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" /> Live Coaching & Interceptions
              </h2>
              
              <ul className="mt-4 space-y-3">
                <li className="flex items-start gap-3 bg-slate-900/90 p-3 rounded-xl border border-slate-800">
                  <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="text-xs text-slate-200">Do <strong>NOT</strong> transfer funds or share OTPs during this call.</span>
                </li>
                <li className="flex items-start gap-3 bg-slate-900/90 p-3 rounded-xl border border-slate-800">
                  <UserCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                  <span className="text-xs text-slate-200">Ask the caller for their official Employee ID and department ticket.</span>
                </li>
              </ul>
            </div>

            {/* ACTION INTERCEPTION BUTTONS */}
            <div className="mt-6 pt-4 border-t border-slate-800/80 space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Emergency Interception Options:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button 
                  onClick={() => setActionTriggered('Emergency Call Termination Initiated: Phone connection closed and caller number blocked.')}
                  className="w-full py-2.5 px-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-red-600/20"
                >
                  <PhoneOff className="w-4 h-4" /> Hang Up & Block
                </button>
                <button 
                  onClick={() => setActionTriggered('AI Defense Agent Deployed: An automated counter-bot is now handling the call on your behalf.')}
                  className="w-full py-2.5 px-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20"
                >
                  <Bot className="w-4 h-4" /> Deploy AI Counter-Bot
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* LIVE TRANSCRIPT FEED WITH EXPANDABLE TACTICS (PHASE 3) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <Volume2 className="w-5 h-5 text-indigo-400" />
              Live Conversation Feed
            </h2>
            <span className="text-xs text-slate-500 font-mono">Whisper Real-Time STT</span>
          </div>

          <div className="space-y-3">
            {currentFeed.length === 0 ? (
              <p className="text-xs text-slate-500 italic py-6 text-center">No active audio stream.</p>
            ) : (
              currentFeed.map((item) => (
                <div key={item.id} className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="font-semibold text-slate-300">{item.speaker}</span>
                    <span className="font-mono text-[10px]">{item.time}</span>
                  </div>
                  <p className="text-sm text-slate-200 leading-relaxed">{item.text}</p>
                  
                  {/* FLAGGED TACTIC BADGE */}
                  {item.tactic && (
                    <div className="pt-2 flex flex-wrap items-center gap-2">
                      <button 
                        onClick={() => setSelectedTactic(selectedTactic?.id === item.id ? null : item)}
                        className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/40 px-2.5 py-1 rounded-md text-xs font-bold flex items-center gap-1.5 transition"
                      >
                        <AlertTriangle className="w-3.5 h-3.5" />
                        Flagged: {item.tactic}
                        <Info className="w-3 h-3 text-red-300 ml-1" />
                      </button>
                    </div>
                  )}

                  {/* EXPANDABLE PSYCHOLOGICAL TOOLTIP DETAIL */}
                  {selectedTactic?.id === item.id && (
                    <div className="mt-2 p-3 bg-red-950/40 border border-red-800/60 rounded-lg text-xs text-red-200 animate-fade-in">
                      <strong className="block text-red-300 mb-1">Psychological Tactic Analysis:</strong>
                      {item.explanation}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}