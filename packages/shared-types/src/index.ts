export type PortalId = "social" | "personal" | "researcher" | "admin";

export type EvidenceCategory =
  | "peer_reviewed"
  | "clinical_trial"
  | "observational"
  | "preprint"
  | "expert_opinion"
  | "community_experience"
  | "ai_hypothesis"
  | "speculation";

export interface SourceReference {
  id: string;
  title: string;
  url?: string;
  evidenceCategory?: EvidenceCategory;
  publishedAt?: string;
}

export interface ApiProblem {
  code: string;
  message: string;
  requestId?: string;
}
