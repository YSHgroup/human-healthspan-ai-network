# Decisions

Status values: DECIDED (owner-approved), PROPOSED, OPEN.

## D1. Target audience and launch community - DECIDED
Open to everyone interested in healthspan: connecting and discussing longevity, youth, healthcare,
biotech, DNA and genomics, proteins, brain capability, appearance, human performance, healing and
related topics. There is no single launch community; the product launches to the general public.
- Social Portal and Personal Portal are open to every member.
- Researcher Portal spaces are gated by verification and permissions, not by audience.
- Consequences: needs strong moderation, evidence-aware discussion, seeded communities across the
  main topics, and clear scope control for the MVP.

## D2. Geographic scope - DECIDED (compliance review required)
Available to everyone with no regional restriction or geoblocking. Users can apply their own
filters (language, region, topic, evidence class, and similar) to shape what they see; filters are
personal preferences, never access restrictions.
- Legal obligations still follow users wherever they are. A privacy and regulatory baseline
  (GDPR-class) applies to all users, including health and genetic data rules, minors, consent,
  data export and deletion, and cross-border transfer. Legal review is required before launch.
- Localization (language, time zone) is planned; region-specific legal variants are handled in
  policy and configuration, not by excluding people.

## D3. MVP boundary - DECIDED
The MVP is basic but working across the main areas; depth comes later.
- Included: shared identity, Social Portal (feed, posts, comments, reactions, communities,
  events), Personal Portal (profile, privacy settings), text messaging, a basic Researcher Portal,
  Admin essentials, and AI chat (see D4).
- Messaging is IN the MVP: direct and group text messaging. Audio, video and rich media follow later.
- Not in the MVP: full AI Scientist capabilities, Organization-Specialized AI, payments, advanced
  health records, global ecosystem features.

## D4. AI scope for the MVP - DECIDED
Build the AI infrastructure first and ship a ChatGPT-style chat feature on top of it.
- Provider-independent gateway with adapters for OpenAI, Anthropic (Claude) and other providers.
- General Platform AI chat for all members (public and common knowledge only).
- Restricted Private AI Scientist prototype for approved researchers only.
- Organization-Specialized AI is not in the MVP.
- API keys stay on the server; frontends never call providers directly.

## D5. AI learning and data capture - DECIDED
Training the AI is a core mission. The platform records all AI interactions and maximizes the data
that can legitimately be used, within the consent and governance rules of the Idea Blueprint.
- Recorded for every AI interaction: prompts, responses, provider, model, prompt version, sources,
  token usage, cost, latency, feedback and outcomes.
- Onboarding asks members for an affirmative, plain-language, revocable consent to "help improve
  the AI" covering their conversations, posts, feedback and usage. Consent is versioned.
- Public content may enter the learning corpus after rights, provenance and quality review.
- Personal health and genomic data requires a separate explicit consent and governance process.
- Private messages, confidential research and organization data are used only with the owner's
  explicit consent.
- Data entering evaluation sets, corpora or training pipelines is reviewed, versioned and, where
  possible, de-identified. Source, rights, consent, sensitivity, intended use and retention are
  recorded.
- Sequence: prompts and retrieval first, evaluation sets from the MVP, fine-tuning when evaluation
  shows it helps. The training start gate may be moved earlier by the owner.
- For the AI biotech scientist, the AI trains itself automatically with all data while making specific, detailed logs. The AI scientist has two layers -superadmin role(this can be used by admin, not for researcher and others) and researcher-support layer.

## Still OPEN
- Exact membership and professional verification criteria (needed by M2)
- Community moderation and publication rules (M2)
- Organization onboarding and tenant model (M3)
- Which providers and deployment options are used at launch (M4)
- Data ownership, licensing and IP policy (M4)
- Legal review outcome for global launch (M1 to M4)