import type { PostOut } from "../api";

export interface FeedPost extends PostOut {
  author_name: string;
  role: string;
  posted_at: string;
}

export interface Community {
  id: string;
  name: string;
  description: string;
  members: number;
  topic: string;
}

export interface ResearchProject {
  id: string;
  title: string;
  description: string;
  focus: string;
  status: string;
}

export const feedPosts: FeedPost[] = [
  {
    id: "post-healthy-aging",
    author_id: "member-maya",
    author_name: "Maya Chen",
    role: "Community member",
    posted_at: "Today",
    body: "What small, sustainable habits have made the biggest difference to your energy over the past year?",
  },
  {
    id: "post-strength",
    author_id: "member-james",
    author_name: "James Okafor",
    role: "Strength coach",
    posted_at: "Yesterday",
    body: "I’m interested in how people balance progressive strength training with recovery as they get older. What signals help you adjust your training?",
  },
  {
    id: "post-evidence",
    author_id: "member-elena",
    author_name: "Elena Rivera",
    role: "Researcher",
    posted_at: "2 days ago",
    body: "A reminder to distinguish promising early findings from established evidence. What would make research summaries more useful to this community?",
  },
];

export const communities: Community[] = [
  {
    id: "healthy-aging",
    name: "Healthy Aging",
    description: "Share practical ideas and questions about aging well across the lifespan.",
    members: 1240,
    topic: "Healthspan",
  },
  {
    id: "fitness-strength",
    name: "Fitness & Strength",
    description: "Discuss movement, strength, mobility, and sustainable training.",
    members: 986,
    topic: "Movement",
  },
  {
    id: "nutrition",
    name: "Nutrition",
    description: "Explore nutrition research, everyday choices, and open questions.",
    members: 842,
    topic: "Nutrition",
  },
  {
    id: "skin-appearance",
    name: "Skin & Appearance",
    description: "Discuss skin health, appearance, and evidence-informed care.",
    members: 517,
    topic: "Wellbeing",
  },
  {
    id: "brain-cognition",
    name: "Brain & Cognition",
    description: "Connect around cognition, brain health, and lifelong learning.",
    members: 763,
    topic: "Cognition",
  },
  {
    id: "biomedical-research",
    name: "Biomedical Research",
    description: "Connect people interested in biomedical research and collaboration.",
    members: 428,
    topic: "Research",
  },
];

export const researchProjects: ResearchProject[] = [
  {
    id: "project-healthy-aging",
    title: "Healthy aging measures",
    description: "Explore meaningful, practical ways to measure healthspan over time.",
    focus: "Healthspan",
    status: "Scoping",
  },
  {
    id: "project-strength-recovery",
    title: "Strength and recovery",
    description: "Review questions around strength training, recovery, and healthy aging.",
    focus: "Movement",
    status: "Open questions",
  },
  {
    id: "project-evidence-literacy",
    title: "Making health evidence usable",
    description: "Investigate how research findings can be communicated with context.",
    focus: "Evidence",
    status: "Scoping",
  },
];
