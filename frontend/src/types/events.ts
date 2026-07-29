export interface ScamAnalysis {
  riskScore: number;
  threatLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  manipulationTactics: string[];
  reasons: string[];
  coachingActions: string[];
  callerClaim: string;
  isIdentityVerified: boolean;
  privacyFingerprint: string;
}

export interface TranscriptUtterance {
  id: string;
  speaker: 'Caller' | 'User';
  text: string;
  timestamp: string;
  flaggedTactic?: string;
}