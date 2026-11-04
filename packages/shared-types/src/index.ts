/** Contracts shared by every portal. Source: Idea Blueprint sections 4, 7 and 8; Architecture sections 3, 12 and 13. */

export type PortalId = "social" | "personal" | "researcher" | "admin";

/** What a member can reach in the Researcher Portal. Portal access never grants resource access. */
export type ResearcherPortalState =
  | "general_user"
  | "research_community_member"
  | "approved_researcher"
  | "project_member"
  | "organization_member"
  | "research_administrator";

/** Per-resource visibility. A public summary must never expose private attachments or results. */
export type Visibility = "private" | "team" | "invited" | "community" | "public";

/** Evidence classes. Popularity is not evidence; AI hypotheses are proposals, not findings. */
export type EvidenceClass =
  | "peer_reviewed"
  | "clinical_trial"
  | "human_observational"
  | "animal"
  | "cellular_in_vitro"
  | "computational"
  | "preprint"
  | "expert_opinion"
  | "community_experience"
  | "ai_generated_hypothesis"
  | "speculation";

export interface SourceReference {
  id: string;
  title: string;
  url?: string;
  evidenceClass?: EvidenceClass;
  publishedAt?: string;
}

/** The three logically separated AI environments. They never share an authorization boundary. */
export type AiEnvironment = "general_platform" | "private_scientist" | "organization_specialized";

/** Professional verification: green is verified, yellow is unverified. */
export type VerificationState = "verified" | "unverified";

export type OrganizationRole =
  | "founder"
  | "owner"
  | "administrator"
  | "research_leader"
  | "researcher"
  | "contributor"
  | "member";

/** Premium features controlled by the backend entitlement system (never by the frontend). */
export type PremiumFeature =
  | "create_organization"
  | "create_event"
  | "organization_contributor_badge"
  | "organization_ai";

export interface ApiProblem {
  code: string;
  message: string;
  requestId?: string;
}
