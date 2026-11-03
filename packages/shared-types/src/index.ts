/** Types mirroring the Architecture v1.2 User API responses (apps/api/app/schemas/platform.py). */
export type AISystem = "general" | "scientist" | "organization";
export type OrgRole = "founder" | "owner" | "administrator" | "research_leader" | "researcher" | "contributor" | "member";
export type VerificationStatus = "verified" | "unverified";

export interface AISource {
  index: number;
  id: string;
  kind: string;
  title: string;
  snippet: string;
  evidence_class: string;
  evidence_label: string;
  source_url: string | null;
  project_id: string | null;
  organization_id: string | null;
}

export interface AIAnswer {
  system: AISystem;
  status: "answered" | "insufficient_evidence";
  answer: string;
  sources: AISource[];
  evidence_summary: Record<string, number>;
  uncertainty: string;
  disclaimer: string;
  run_id: string;
  conversation_id: string;
  provider: string;
  model_version: string;
  ai_generated: true;
}

export interface Organization {
  id: string;
  slug: string;
  name: string;
  description: string;
  website: string | null;
  verification_status: "unverified" | "verified" | "rejected";
  created_at: string;
  my_role?: OrgRole | null;
  member_count?: number;
}

export interface OrganizationMember { user_id: string; display_name: string; role: OrgRole }
export interface Invitation { id: string; organization_id: string; organization_name: string | null; role: OrgRole; status: string; created_at: string }
export interface Badge { id: string; slug: string; name: string; description: string; kind: string; organization_id: string | null; is_active: boolean }

export interface ProfessionalRecord {
  id: string;
  user_id: string;
  kind: string;
  title: string;
  institution: string | null;
  start_year: number | null;
  end_year: number | null;
  description: string | null;
  is_public: boolean;
  verification_status: VerificationStatus;
  verification_color: "green" | "yellow";
  verified_at: string | null;
}

export interface WorkHistoryEntry {
  id: string;
  organization_id: string | null;
  project_id: string | null;
  kind: string;
  summary: string;
  verification_status: VerificationStatus;
  supersedes_id: string | null;
  created_at: string;
}

export interface ResearchTask {
  id: string;
  project_id: string;
  assignee_id: string | null;
  title: string;
  description: string;
  status: "todo" | "in_progress" | "done";
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface ResearchMembershipState {
  has_research_access: boolean;
  status: "none" | "staff" | "pending" | "approved" | "rejected" | "revoked";
}

export type HealthCategory =
  | "medical_record" | "measurement" | "laboratory" | "observation" | "nutrition"
  | "fitness" | "performance" | "sleep_activity" | "other";

export interface HealthRecord {
  id: string;
  category: HealthCategory;
  title: string;
  metric: string | null;
  value_number: number | null;
  value_text: string | null;
  unit: string | null;
  source: string;
  recorded_at: string;
  created_at: string;
}

export interface HealthShare {
  id: string;
  grantee_user_id: string | null;
  grantee_organization_id: string | null;
  is_link: boolean;
  categories: HealthCategory[];
  label: string | null;
  expires_at: string | null;
  revoked_at: string | null;
  created_at: string;
  link_token?: string | null;
}

export interface Consent { purpose: string; granted: boolean; updated_at: string | null }
export interface EventItem {
  id: string;
  organizer_id: string;
  title: string;
  description: string;
  kind: string;
  visibility: string;
  starts_at: string;
  ends_at: string | null;
  location: string | null;
  online_url: string | null;
  capacity: number | null;
  status: string;
  discussion_post_id: string | null;
  registered_count: number;
  is_registered: boolean;
}
export interface NotificationItem { id: string; kind: string; title: string; body: string | null; resource_type: string | null; resource_id: string | null; read_at: string | null; created_at: string }
export interface Conversation { id: string; participant_ids: string[]; participant_names: string[]; last_message_at: string | null; unread_count: number }
export interface Message { id: string; conversation_id: string; sender_id: string; kind: string; body: string; media_url: string | null; created_at: string }
export interface Entitlement { id: string; subject_type: string; feature: string; quantity_total: number; quantity_used: number; source: string; expires_at: string | null; revoked_at: string | null }
export interface OrgAIInstance { id: string; organization_id: string; name: string; instructions: string; status: string }
export interface OrgDocument { id: string; organization_id: string; title: string; source_label: string | null; created_at: string }
export interface ActivityItem { type: string; id: string; summary: string; created_at: string }
