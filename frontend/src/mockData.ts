import type { ScamAnalysis, TranscriptUtterance } from './types/events';

export const mockScamAnalysis: ScamAnalysis = {
  riskScore: 94,
  threatLevel: 'CRITICAL',
  manipulationTactics: [
    'Fake Authority',
    'Artificial Urgency',
    'Fear Induction',
    'Isolation'
  ],
  reasons: [
    'Claims to be Cyber Crime Department official',
    'Demands immediate transfer within 10 minutes',
    'Threatens account freezing',
    'Instructs user not to disclose call details'
  ],
  coachingActions: [
    'Do NOT transfer money during this call.',
    'Ask the caller for their official Employee ID.',
    'Hang up and dial official customer care directly.'
  ],
  callerClaim: 'Cyber Crime Officer',
  isIdentityVerified: false,
  privacyFingerprint: 'fp_982a_psych_manipulation'
};

export const mockTranscript: TranscriptUtterance[] = [
  {
    id: '1',
    speaker: 'Caller',
    text: 'This is Officer Sharma from the National Cyber Crime Cell. Your bank account has been flagged for illicit activity.',
    timestamp: '12:01:05 PM',
    flaggedTactic: 'Fake Authority'
  },
  {
    id: '2',
    speaker: 'User',
    text: 'Wait, which account? I haven\'t received any email or official notice.',
    timestamp: '12:01:12 PM'
  },
  {
    id: '3',
    speaker: 'Caller',
    text: 'Do not interrupt. You must transfer the balance to a secure verification node within 10 minutes or your account will be frozen permanently. Do not inform anyone.',
    timestamp: '12:01:22 PM',
    flaggedTactic: 'Artificial Urgency / Isolation'
  }
];