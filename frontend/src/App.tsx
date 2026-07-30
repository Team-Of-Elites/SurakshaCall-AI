import React, { useState, useEffect } from 'react';
import './index.css';

// ======================== ICONS ========================
const ShieldIcon = ({ size = 24, color = 'currentColor', fill = 'none' }: { size?: number; color?: string; fill?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

const PhoneOffIcon = ({ size = 18 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7 2 2 0 0 1 1.72 2v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A2 2 0 0 1 10.68 13.31z" />
    <line x1="23" y1="1" x2="1" y2="23" />
    <path d="M10.68 13.31a16 16 0 0 1-2.6-3.41L6.81 11.17a2 2 0 0 1-2.11.45 12.84 12.84 0 0 0-2.81-.7A2 2 0 0 1 0 8.92V6a2 2 0 0 1 2.18-2A19.79 19.79 0 0 1 10.68 13.31z" />
  </svg>
);

const AlertTriangleIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

const CheckIcon = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const ArrowRightIcon = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

const MicIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
);

const SpeakerIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
  </svg>
);

const UserIcon = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const LockIcon = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

const ZapIcon = ({ size = 18 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);

const EyeIcon = ({ size = 18 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const BrainIcon = ({ size = 18 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-1.07-4.82A3 3 0 0 1 5.5 10c0-.33.05-.65.14-.95A2.5 2.5 0 0 1 7 5a2.5 2.5 0 0 1 2.5-3z" />
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 1.07-4.82A3 3 0 0 0 18.5 10c0-.33-.05-.65-.14-.95A2.5 2.5 0 0 0 17 5a2.5 2.5 0 0 0-2.5-3z" />
  </svg>
);

const ClockIcon = ({ size = 18 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

const ExternalLinkIcon = ({ size = 12 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <polyline points="15 3 21 3 21 9" />
    <line x1="10" y1="14" x2="21" y2="3" />
  </svg>
);

const InfoIcon = ({ size = 13 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
);

// ======================== NAVBAR ========================
interface NavbarProps {
  currentPage: 'home' | 'dashboard';
  onNavigate: (page: 'home' | 'dashboard') => void;
}

const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate }) => {
  return (
    <nav className="navbar">
      <div className="container">
        <div className="navbar-inner">
          {/* Logo */}
          <a className="logo" href="#" onClick={(e) => { e.preventDefault(); onNavigate('home'); }}>
            <div className="logo-icon">
              <ShieldIcon size={18} color="white" fill="rgba(255,255,255,0.15)" />
            </div>
            <div className="logo-text">
              <span className="black">Suraksha</span><span className="teal">Call AI</span>
            </div>
          </a>

          {/* Center nav pill */}
          <div className="nav-pill">
            <a
              className={currentPage === 'home' ? 'active' : ''}
              href="#"
              onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
            >
              Home
            </a>
            <a
              href="#how-it-works"
              onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
            >
              How It Works
            </a>
            <a href="#features" onClick={(e) => { e.preventDefault(); onNavigate('home'); }}>
              Features
            </a>
            <a
              className={currentPage === 'dashboard' ? 'active' : ''}
              href="#"
              onClick={(e) => { e.preventDefault(); onNavigate('dashboard'); }}
            >
              Live Demo
            </a>
          </div>

          {/* CTA button */}
          <button className="btn-demo" id="try-live-demo-btn" onClick={() => onNavigate('dashboard')}>
            Try Live Demo <ArrowRightIcon size={13} />
          </button>
        </div>
      </div>
    </nav>
  );
};

// ======================== PHONE MOCKUP ========================
const PhoneMockup: React.FC = () => {
  const [waveHeights, setWaveHeights] = useState<number[]>([8, 24, 14, 32, 18, 28, 10, 36, 16]);

  useEffect(() => {
    const interval = setInterval(() => {
      setWaveHeights(Array.from({ length: 9 }, () => Math.floor(Math.random() * 30) + 6));
    }, 200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="phone-mockup">
      <div className="phone-screen">
        {/* Notch */}
        <div className="phone-notch">
          <div className="notch-pill" />
        </div>

        {/* Status bar */}
        <div className="phone-status">
          <span style={{ fontSize: 9 }}>9:41</span>
          <span style={{ fontSize: 9 }}>▲▲▲ ◼◼</span>
        </div>

        {/* Call header */}
        <div className="phone-call-header">
          <div className="call-timer">● 02:47</div>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 8 }}>
            <div style={{
              width: 52, height: 52, background: 'rgba(255,255,255,0.08)',
              borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
              border: '2px solid rgba(255,255,255,0.12)', fontSize: 22
            }}>
              👤
            </div>
          </div>
          <div className="caller-name">+91 98765 43210</div>
          <div className="caller-label">Unknown · India</div>
        </div>

        {/* Warning banner */}
        <div className="warning-banner">
          <div className="warning-top">
            <span className="caution-badge">⚠ Caution</span>
          </div>
          <div className="warning-text">
            This call may be requesting sensitive information
          </div>
        </div>

        {/* Waveform */}
        <div className="waveform-container">
          {waveHeights.map((h, i) => (
            <div
              key={i}
              className="wave-bar"
              style={{
                height: `${h}px`,
                background: i % 3 === 0
                  ? '#3FA9A0'
                  : i % 3 === 1
                    ? '#5BC4BB'
                    : 'rgba(63,169,160,0.4)',
                transition: 'height 0.18s ease'
              }}
            />
          ))}
        </div>

        {/* Action buttons */}
        <div className="phone-actions">
          <div className="action-btn btn-mic" style={{ color: 'rgba(255,255,255,0.7)' }}>
            <MicIcon size={17} />
          </div>
          <div className="action-btn btn-end" style={{ color: 'white' }}>
            <PhoneOffIcon size={18} />
          </div>
          <div className="action-btn btn-speaker" style={{ color: 'rgba(255,255,255,0.7)' }}>
            <SpeakerIcon size={17} />
          </div>
        </div>
      </div>
    </div>
  );
};

// ======================== RISK GAUGE ========================
const RiskGauge: React.FC<{ score: number }> = ({ score }) => {
  const radius = 38;
  const circumference = Math.PI * radius; // semicircle
  const fillRatio = score / 100;
  const dashOffset = circumference * (1 - fillRatio);

  const getColor = (s: number) => {
    if (s < 40) return '#22C55E';
    if (s < 70) return '#F59E0B';
    return '#EF4444';
  };

  const color = getColor(score);

  return (
    <div className="gauge-wrapper">
      <svg width="90" height="52" viewBox="-5 -5 100 56" className="gauge-svg">
        {/* Background arc */}
        <path
          d="M 5 47 A 38 38 0 0 1 81 47"
          fill="none"
          stroke="#E4EEF0"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {/* Filled arc */}
        <path
          d="M 5 47 A 38 38 0 0 1 81 47"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: 'stroke-dashoffset 1s ease, stroke 0.5s ease' }}
        />
        {/* Score label */}
        <text x="43" y="42" textAnchor="middle" fill="#0F1923" fontSize="18" fontWeight="900" fontFamily="Inter">
          {score}
        </text>
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', width: '90px', fontSize: 9, color: '#9AAAB8', marginTop: -4 }}>
        <span>Safe</span><span>Critical</span>
      </div>
    </div>
  );
};

// ======================== HOME PAGE ========================
interface HomePageProps {
  onNavigate: (page: 'home' | 'dashboard') => void;
}

const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  return (
    <div className="page">
      {/* -------- HERO -------- */}
      <section className="hero">
        {/* Decorative shield icons */}
        <div className="shield-deco shield-deco-1" aria-hidden="true">🛡</div>
        <div className="shield-deco shield-deco-2" aria-hidden="true">✚</div>

        <div className="container">
          <div className="hero-content">
            {/* Badge */}
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <div className="hero-badge">
                <span className="badge-new">New</span>
                Protecting 10,000+ calls from fraud
              </div>
            </div>

            {/* Heading */}
            <h1 className="hero-title">
              Stay Safe On Every Call,<br />
              Stay <span className="teal-word">Protected</span>
            </h1>

            {/* Subheading */}
            <p className="hero-subtitle">
              SurakshaCall AI listens for scam patterns in real time, verifies caller identity,
              and warns you before you share anything sensitive.
            </p>

            {/* Phone section with floating cards */}
            <div className="phone-section">
              {/* Left floating card — Risk Index */}
              <div className="floating-card-left">
                <div className="float-card">
                  <div className="float-card-title">Risk Index</div>
                  <RiskGauge score={62} />
                  <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('dashboard'); }} className="float-card-link">
                    View Details <ArrowRightIcon size={11} />
                  </a>
                </div>
              </div>

              {/* Phone mockup */}
              <div className="phone-wrapper">
                <PhoneMockup />
              </div>

              {/* Right floating card — Identity Check */}
              <div className="floating-card-right">
                <div className="float-card identity-card">
                  <div className="float-card-title">Identity Check</div>
                  <div className="status-tag status-unverified">
                    ⚠ Unverified
                  </div>
                  <p className="caller-claim">
                    Caller claims:<br />
                    <strong>State Bank of India</strong>
                  </p>
                  <button className="btn-verify" id="verify-now-btn" onClick={() => onNavigate('dashboard')}>
                    Verify Now <ArrowRightIcon size={10} />
                  </button>
                </div>
              </div>
            </div>

            {/* App store buttons */}
            <div className="store-buttons">
              <a href="#" className="store-btn" id="appstore-btn">
                <span className="store-btn-icon">🍎</span>
                <div className="store-btn-text">
                  <small>Download on the</small>
                  <strong>App Store</strong>
                </div>
              </a>
              <a href="#" className="store-btn" id="playstore-btn">
                <span className="store-btn-icon">▶</span>
                <div className="store-btn-text">
                  <small>Get it on</small>
                  <strong>Google Play</strong>
                </div>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* -------- STATS BAR -------- */}
      <section className="stats-bar">
        <div className="container">
          <div className="stats-inner">
            <div className="stat-block">
              <div className="stat-icon">🛡️</div>
              <div className="stat-text">
                <strong>10,000+</strong>
                <span>Calls Protected</span>
              </div>
            </div>
            <div className="stat-block">
              <div className="stat-icon">🔍</div>
              <div className="stat-text">
                <strong>500+</strong>
                <span>Scam Patterns Detected</span>
              </div>
            </div>
            <div className="stat-block">
              <div className="stat-icon">⚡</div>
              <div className="stat-text">
                <strong>24/7</strong>
                <span>Real-Time Monitoring</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* -------- HOW IT WORKS -------- */}
      <section className="section" id="how-it-works" style={{ background: 'white' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
            <div>
              <div className="section-label">
                ✦ How It Works
              </div>
              <h2 className="section-title">Real-time protection<br />in three steps</h2>
              <p className="section-sub">
                SurakshaCall AI works silently in the background, analyzing every call so you don't have to worry.
              </p>

              <div style={{ marginTop: 36, display: 'flex', flexDirection: 'column', gap: 20 }}>
                {[
                  {
                    num: '01',
                    icon: '🎙️',
                    title: 'Live Audio Analysis',
                    desc: 'Our AI listens and transcribes the call in real-time using advanced speech recognition.'
                  },
                  {
                    num: '02',
                    icon: '🧠',
                    title: 'Pattern Detection',
                    desc: 'ML models scan for 500+ known scam patterns, urgency tactics, and social engineering cues.'
                  },
                  {
                    num: '03',
                    icon: '🛡️',
                    title: 'Instant Warning',
                    desc: 'You receive a real-time alert with risk level and a recommended action before any harm is done.'
                  }
                ].map((step) => (
                  <div key={step.num} style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                    <div style={{
                      width: 44, height: 44, borderRadius: 12, background: 'var(--teal-pale)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 18, flexShrink: 0
                    }}>
                      {step.icon}
                    </div>
                    <div>
                      <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--teal)', marginBottom: 3, letterSpacing: '0.5px' }}>
                        STEP {step.num}
                      </div>
                      <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>{step.title}</div>
                      <div style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{step.desc}</div>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: 32 }}>
                <button className="btn-teal" id="see-live-demo-btn" onClick={() => onNavigate('dashboard')}>
                  See Live Demo <ArrowRightIcon size={14} />
                </button>
              </div>
            </div>

            {/* Visual side */}
            <div style={{ position: 'relative' }}>
              <div style={{
                background: 'linear-gradient(135deg, var(--teal-pale), #F0F9FF)',
                borderRadius: 24, padding: 32,
                border: '1px solid var(--teal-pale2)',
                position: 'relative', overflow: 'hidden'
              }}>
                {/* Mini transcript preview */}
                <div style={{ marginBottom: 16, fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.6px' }}>
                  Live Transcript Preview
                </div>

                {[
                  { speaker: 'Caller', text: 'This is CBI Officer Mehta. Your account shows suspicious transactions...', flagged: true },
                  { speaker: 'You', text: "I didn't do anything suspicious." },
                  { speaker: 'Caller', text: 'You must share your OTP immediately to avoid arrest.', flagged: true }
                ].map((msg, i) => (
                  <div key={i} style={{
                    marginBottom: 10,
                    animation: `transcript-in 0.4s ease ${i * 0.15}s both`
                  }}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: msg.speaker === 'Caller' ? '#DC2626' : 'var(--teal-dark)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.3px' }}>
                      {msg.speaker}
                    </div>
                    <div style={{
                      background: msg.speaker === 'Caller' ? 'rgba(254,242,242,0.8)' : 'white',
                      border: `1px solid ${msg.speaker === 'Caller' ? 'rgba(239,68,68,0.15)' : 'var(--border)'}`,
                      borderRadius: 12, padding: '10px 12px',
                      fontSize: 12.5, color: 'var(--text-primary)', lineHeight: 1.5
                    }}>
                      {msg.text}
                    </div>
                    {msg.flagged && (
                      <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: 4,
                        background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)',
                        color: '#DC2626', fontSize: 10, fontWeight: 700,
                        padding: '3px 8px', borderRadius: 6, marginTop: 5
                      }}>
                        <AlertTriangleIcon size={10} /> Scam Tactic Detected
                      </div>
                    )}
                  </div>
                ))}

                {/* AI badge */}
                <div style={{
                  marginTop: 16, padding: '10px 14px',
                  background: 'linear-gradient(135deg, var(--teal), var(--teal-dark))',
                  borderRadius: 12, color: 'white', fontSize: 12, fontWeight: 600,
                  display: 'flex', alignItems: 'center', gap: 8
                }}>
                  <span>🛡️</span>
                  <span>SurakshaCall AI: <strong>HIGH RISK DETECTED</strong> — Do not share OTP</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* -------- FEATURES -------- */}
      <section className="section" id="features" style={{ background: 'var(--bg)' }}>
        <div className="container">
          <div className="text-center" style={{ maxWidth: 540, margin: '0 auto 48px' }}>
            <div className="section-label" style={{ justifyContent: 'center' }}>✦ Features</div>
            <h2 className="section-title">Everything you need to<br />stay scam-free</h2>
            <p className="section-sub" style={{ margin: '0 auto' }}>
              Powerful features working together to give you complete call protection.
            </p>
          </div>

          <div className="features-grid">
            {[
              {
                icon: <ZapIcon size={20} />, title: 'Real-Time Detection',
                desc: 'Instant analysis as the conversation unfolds — no delay, no waiting. Get warned in under 2 seconds.'
              },
              {
                icon: <EyIcon size={20} />, title: 'Identity Verification',
                desc: 'Cross-references caller ID against known institutions and flags unverified or spoofed numbers.'
              },
              {
                icon: <BrainIcon size={20} />, title: 'AI Pattern Matching',
                desc: 'Trained on 500+ documented scam patterns including impersonation, urgency tactics, and social engineering.'
              },
              {
                icon: <LockIcon size={20} />, title: 'Data Redaction',
                desc: 'Automatically blurs and redacts sensitive data like OTPs and account numbers in the live transcript.'
              },
              {
                icon: <ClockIcon size={20} />, title: '24/7 Monitoring',
                desc: 'Always-on protection across all incoming calls, even when your phone is in your pocket.'
              },
              {
                icon: <ShieldIcon size={20} />, title: 'Instant Intervention',
                desc: 'One-tap emergency options to end the call, block the number, or deploy an AI counter-agent.'
              }
            ].map((f, i) => (
              <div key={i} className="feature-card">
                <div className="feature-icon">
                  <span style={{ color: 'var(--teal)' }}>{f.icon}</span>
                </div>
                <div className="feature-title">{f.title}</div>
                <div className="feature-desc">{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* -------- CTA FOOTER -------- */}
      <section className="footer-cta" id="contact">
        <div className="container">
          <div className="footer-cta-inner">
            <div>
              <h3>Ready to protect your calls?</h3>
              <p>Join 10,000+ users who trust SurakshaCall AI every day.</p>
            </div>
            <button className="btn-cta-white" id="home-cta-btn" onClick={() => onNavigate('dashboard')}>
              Try Live Demo <ArrowRightIcon size={14} />
            </button>
          </div>
        </div>
      </section>

      {/* Bottom footer */}
      <div className="footer-bottom">
        <div className="container">
          <div className="footer-bottom-inner">
            <div className="footer-stats">
              <div className="footer-stat"><strong>10,000+</strong> Calls Protected</div>
              <div className="footer-stat"><strong>500+</strong> Patterns Detected</div>
              <div className="footer-stat"><strong>24/7</strong> Live Monitoring</div>
            </div>
            <div className="footer-copy">© 2024 SurakshaCall AI · Built for safety.</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Alias to avoid naming conflict
const EyIcon = EyeIcon;

// ======================== DASHBOARD PAGE ========================
interface TranscriptEntry {
  id: number;
  speaker: 'Caller' | 'You';
  time: string;
  text: React.ReactNode;
  tactic?: string;
  insight?: string;
  delay: number;
}

const transcriptData: TranscriptEntry[] = [
  {
    id: 1,
    speaker: 'Caller',
    time: '12:01:05',
    text: 'Namaste, this is Officer Sharma calling from the National Cyber Crime Cell, Mumbai. Your Aadhaar number has been linked to three illegal transactions.',
    tactic: 'Fake Authority',
    insight: 'Impersonating a government/law enforcement officer to bypass the victim\'s critical thinking and create immediate compliance.',
    delay: 0
  },
  {
    id: 2,
    speaker: 'You',
    time: '12:01:18',
    text: "I haven't done any transactions. What are you talking about?",
    delay: 0.1
  },
  {
    id: 3,
    speaker: 'Caller',
    time: '12:01:28',
    text: <>
      You must verify your identity immediately. Please share your bank OTP —{' '}
      <span className="redacted-chip">
        <LockIcon size={9} /> CODE REDACTED
      </span>
      {' '}— or your account will be frozen within 10 minutes.
    </>,
    tactic: 'Urgency + OTP Request',
    insight: 'Creating an artificial time deadline forces panic. Requesting OTPs is NEVER a legitimate bank/government practice.',
    delay: 0.2
  },
  {
    id: 4,
    speaker: 'You',
    time: '12:01:45',
    text: "Wait, I don't think banks ask for OTPs over the phone...",
    delay: 0.3
  },
  {
    id: 5,
    speaker: 'Caller',
    time: '12:01:52',
    text: 'Do not inform anyone about this call. This is a confidential investigation. If you tell anyone, you will be arrested under Section 66C of the IT Act.',
    tactic: 'Isolation + Legal Threat',
    insight: 'Isolation prevents the victim from seeking advice. Legal threats create fear. Legitimate investigations are never conducted by phone.',
    delay: 0.4
  }
];

interface DashboardPageProps {
  onNavigate: (page: 'home' | 'dashboard') => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [expandedTactic, setExpandedTactic] = useState<number | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [callTime, setCallTime] = useState(167); // 2:47

  useEffect(() => {
    const timer = setInterval(() => {
      setCallTime(t => t + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
  };

  return (
    <div className="dashboard-page">
      <div className="container">
        {/* -------- PAGE HEADER -------- */}
        <div className="dashboard-header">
          <div className="page-header">
            <div className="page-title-group">
              <div className="live-badge">
                <div className="live-dot" />
                Live Session Active
              </div>
              <h1 className="page-title">Live Call Protection</h1>
              <p className="page-subtitle">
                SurakshaCall AI is actively monitoring this conversation for threats.
              </p>
            </div>

            {/* Call info chip */}
            <div className="call-info-chip">
              <div>
                <div className="label">Caller Number</div>
                <div className="value">+91 98765 43210</div>
              </div>
              <div className="separator" />
              <div>
                <div className="label">Duration</div>
                <div className="value" style={{ fontVariantNumeric: 'tabular-nums' }}>{formatTime(callTime)}</div>
              </div>
              <div className="separator" />
              <div>
                <div className="label">Location</div>
                <div className="value">Mumbai, IN</div>
              </div>
            </div>
          </div>
        </div>

        {/* -------- ACTION NOTIFICATION -------- */}
        {actionMsg && (
          <div style={{
            background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: 14,
            padding: '14px 18px', marginBottom: 20,
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            animation: 'fade-in-up 0.3s ease both'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13.5, color: '#16A34A', fontWeight: 600 }}>
              <span>✅</span> {actionMsg}
            </div>
            <button
              onClick={() => setActionMsg(null)}
              style={{ fontSize: 12, color: '#16A34A', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}
            >
              Dismiss
            </button>
          </div>
        )}

        {/* -------- MAIN GRID -------- */}
        <div className="dashboard-grid">

          {/* ---- LEFT: TRANSCRIPT ---- */}
          <div className="transcript-panel">
            <div className="panel-header">
              <div className="panel-title">
                <div className="panel-icon">🎙️</div>
                Live Transcript Feed
              </div>
              <div className="panel-status">
                <div className="live-dot" style={{ width: 7, height: 7, background: '#EF4444', borderRadius: '50%', animation: 'blink 1s ease-in-out infinite' }} />
                Whisper STT · Real-Time
              </div>
            </div>

            <div className="transcript-feed">
              {transcriptData.map((entry) => (
                <div
                  key={entry.id}
                  className={`transcript-bubble bubble-${entry.speaker.toLowerCase()}`}
                  style={{ animationDelay: `${entry.delay}s` }}
                >
                  {/* Meta row */}
                  <div className="bubble-meta">
                    <span className={`speaker-badge speaker-${entry.speaker === 'Caller' ? 'caller' : 'user'}`}>
                      {entry.speaker}
                    </span>
                    <span>{entry.time}</span>
                  </div>

                  {/* Bubble text */}
                  <div className="bubble-text">
                    {entry.text}
                  </div>

                  {/* Tactic flag */}
                  {entry.tactic && (
                    <button
                      className="tactic-flag"
                      onClick={() => setExpandedTactic(expandedTactic === entry.id ? null : entry.id)}
                      style={{ background: 'rgba(239,68,68,0.08)', cursor: 'pointer', border: '1px solid rgba(239,68,68,0.2)' }}
                    >
                      <AlertTriangleIcon size={11} />
                      Flagged: {entry.tactic}
                      <InfoIcon size={11} />
                    </button>
                  )}

                  {/* Expandable AI insight */}
                  {expandedTactic === entry.id && entry.insight && (
                    <div className="ai-insight" style={{ animation: 'fade-in-up 0.25s ease both' }}>
                      <strong>🧠 AI Insight:</strong> {entry.insight}
                    </div>
                  )}
                </div>
              ))}

              {/* Typing indicator */}
              <div className="transcript-bubble" style={{ animation: 'transcript-in 0.4s ease 0.5s both' }}>
                <div className="bubble-meta">
                  <span className="speaker-badge speaker-caller">Caller</span>
                  <span>12:02:10</span>
                </div>
                <div className="bubble-text" style={{ background: 'rgba(254,242,242,0.7)', borderColor: 'rgba(239,68,68,0.12)' }}>
                  <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
                    {[0, 0.2, 0.4].map((d, i) => (
                      <div key={i} style={{
                        width: 7, height: 7, borderRadius: '50%',
                        background: '#DC2626', opacity: 0.5,
                        animation: `blink 1s ease-in-out ${d}s infinite`
                      }} />
                    ))}
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 4 }}>Caller is speaking...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ---- RIGHT: SUMMARY PANEL ---- */}
          <div className="summary-panel">

            {/* Risk Level Card */}
            <div className="card risk-card">
              <div className="card-header">
                <div className="card-icon icon-danger">🚨</div>
                <div>
                  <div className="card-title">Threat Assessment</div>
                  <div className="card-sub">Updated in real-time</div>
                </div>
              </div>

              <div className="risk-level-badge">
                ⚠ Risk Level: HIGH
              </div>

              <div className="risk-score-row">
                <div className="risk-score-num">94</div>
                <div className="risk-score-label">/ 100<br />Threat Score</div>
              </div>

              <div className="risk-bar-bg">
                <div className="risk-bar-fill" style={{ width: '94%' }} />
              </div>

              <div className="risk-reason">
                <strong>Primary reason:</strong> Caller requested a confidential OTP while impersonating a CBI officer and issuing legal threats — 3 scam tactics simultaneously detected.
              </div>

              <button
                className="btn-primary"
                id="end-call-btn"
                onClick={() => setActionMsg('Call ended and number blocked. A report has been filed automatically.')}
              >
                <PhoneOffIcon size={16} /> End Call & Block
              </button>
              <button
                className="btn-secondary"
                id="verify-officially-btn"
                onClick={() => setActionMsg('Opening official SBI helpline verification portal...')}
              >
                <ExternalLinkIcon size={14} /> Verify Officially
              </button>
            </div>

            {/* Identity Check Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-icon icon-warning">🪪</div>
                <div>
                  <div className="card-title">Identity Check</div>
                  <div className="card-sub">Caller verification status</div>
                </div>
              </div>

              <div>
                {[
                  { label: 'Caller ID', value: '+91 98765 43210', className: '' },
                  { label: 'Claimed Identity', value: 'CBI / State Bank of India', className: 'danger' },
                  { label: 'Verification', value: '✗ Unverified', className: 'danger' },
                  { label: 'Caller Location', value: 'Mumbai, IN', className: '' },
                  { label: 'Number Age', value: '< 30 days (Suspicious)', className: 'danger' },
                  { label: 'Spam Reports', value: '47 reports filed', className: 'danger' }
                ].map((row, i) => (
                  <div key={i} className="identity-row">
                    <span className="identity-label">{row.label}</span>
                    <span className={`identity-value ${row.className}`}>{row.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Coaching Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-icon icon-teal">🛡️</div>
                <div>
                  <div className="card-title">Live Coaching</div>
                  <div className="card-sub">AI-recommended actions</div>
                </div>
              </div>

              <div className="coaching-list">
                {[
                  { dot: 'teal', icon: '🚫', text: 'Do NOT share any OTP, PIN, or password on this call.' },
                  { dot: 'teal', icon: '📵', text: 'No real government agency contacts you to collect OTPs by phone.' },
                  { dot: 'warning', icon: '📞', text: 'Call back SBI directly using 1800-11-2211 to verify.' },
                  { dot: 'teal', icon: '📋', text: 'You can report this number to TRAI at www.sancharsaathi.gov.in.' }
                ].map((item, i) => (
                  <div key={i} className="coaching-item">
                    <div className={`coaching-dot dot-${item.dot}`}>{item.icon}</div>
                    <span>{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* -------- CTA FOOTER -------- */}
      <section className="footer-cta">
        <div className="container">
          <div className="footer-cta-inner">
            <div>
              <h3>Protected by SurakshaCall AI</h3>
              <p>10,000+ calls shielded · 500+ scam patterns · Always-on monitoring</p>
            </div>
            <button className="btn-cta-white" id="dashboard-home-btn" onClick={() => onNavigate('home')}>
              ← Back to Home
            </button>
          </div>
        </div>
      </section>

      <div className="footer-bottom">
        <div className="container">
          <div className="footer-bottom-inner">
            <div className="footer-stats">
              <div className="footer-stat"><strong>10,000+</strong> Calls Protected</div>
              <div className="footer-stat"><strong>500+</strong> Patterns Detected</div>
              <div className="footer-stat"><strong>24/7</strong> Live Monitoring</div>
            </div>
            <div className="footer-copy">© 2024 SurakshaCall AI · Built for safety.</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ======================== APP ROOT ========================
export default function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'dashboard'>('home');

  const handleNavigate = (page: 'home' | 'dashboard') => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <>
      <Navbar currentPage={currentPage} onNavigate={handleNavigate} />
      {currentPage === 'home'
        ? <HomePage onNavigate={handleNavigate} />
        : <DashboardPage onNavigate={handleNavigate} />
      }
    </>
  );
}