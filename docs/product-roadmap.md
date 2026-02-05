# Seedcraft — Product Roadmap

> Living document. Last updated: February 2026.

---

## Vision

Seedcraft is an enterprise decision compression platform that collapses the sequential, multi-month product approval process in large regulated organisations into concurrent, AI-assisted alignment — across business lines, governance functions, and technology teams.

## Roadmap Principles

1. **Each phase is independently valuable.** Don't build Phase 3 features hoping Phase 4 will make them useful. Every release must solve a problem users have today.
2. **Validate before building.** Each phase has a clear validation gate. Don't invest in the next phase until the current one proves out.
3. **Revenue follows value.** Charge when the product demonstrably saves time. Don't wait until everything is built.
4. **Depth over breadth.** Nail one section of the inception pack (e.g., architecture review) before making all seven sections enterprise-grade.
5. **The wedge is a conversation starter, not the product.** Phase 1 gets you in the room. Phases 2-4 are the product.

---

## Current State (Phase 0 — Shipped)

| Capability | Status |
|---|---|
| 6-agent AI inception pack generation | Done |
| 7-tab read-only viewer | Done |
| Google SSO auth (Supabase) | Done |
| Session history (view, re-open, delete) | Done |
| JSON export | Done |
| Real-time progress tracking | Done |
| Quality scoring with revision loop | Done |

**What's missing for any enterprise conversation:** Editable output, PDF export, enterprise positioning, org-specific context, collaboration, and the output quality is generic (not grounded in any organisation's standards).

---

## Phase 1 — Enterprise Wedge

> **Objective:** Make the current tool credible enough for a design partner conversation. Get 3-5 enterprise design partners using it on real initiatives.

### Why this phase matters
No enterprise will pilot a tool that exports JSON only, can't be edited, and positions itself as "100% free for startups." Phase 1 is the minimum to not embarrass yourself in a meeting with a Head of Architecture.

### Features

**1.1 — Reposition for Enterprise**
- Rewrite landing page copy for regulated enterprise audience
- Remove "100% free" / startup language
- Add enterprise value propositions: compliance, cross-divisional alignment, time-to-market
- Add "Request a Demo" / "Talk to Us" CTA alongside self-serve

**1.2 — Export That Enterprises Accept**
- PDF export with proper formatting, section headers, and branding
- Word/DOCX export (this is what gets circulated in enterprises — not JSON, not PDFs)
- Per-section export (architect downloads just the architecture section)

**1.3 — Editable Output**
- Inline editing of any section (rich text)
- Regenerate a single section with updated constraints without re-running the full pipeline
- Preserve edit history (what was AI-generated vs. human-modified)

**1.4 — Section-Level Interaction**
- "Ask about this section" button on each tab — opens a contextual chat panel
- User can ask follow-up questions, request deeper analysis, or challenge assumptions
- Responses grounded in the full inception pack context (not just that section in isolation)
- This is the "hybrid" interaction model — generation + conversation

**1.5 — Operational Stability**
- Fix backend deployment reliability (health check failures)
- Proper error boundaries in frontend (no blank pages)
- Rate limiting and graceful degradation under load

### Validation Criteria
- 3-5 enterprise design partners (unpaid) agree to run real product ideas through the tool
- At least one architecture or product lead says "I would use this in my review process"
- Reviewers keep 50%+ of generated content (vs. rewriting from scratch)

### Business Milestone
- Design partner agreements signed (no revenue yet — this is learning)
- Waitlist or inbound interest from enterprise landing page

### Key Risks
- Enterprise contacts won't take the meeting — need warm intros or advisor network
- Output quality on real enterprise initiatives may be significantly worse than on startup ideas (more complex domains, more constraints)

---

## Phase 2 — Organisation Context

> **Objective:** Make Seedcraft generate output that sounds like it was written by someone inside the organisation, not by a generic AI. Convert design partners to first paid pilot.

### Why this phase matters
This is the single most important phase. It's the difference between "a nicer ChatGPT wrapper" and "a tool that knows our architecture standards, our regulatory obligations, and our technology radar." Without org context, the output is 50% useful. With it, the output is 80% useful. That delta is the entire business.

### Features

**2.1 — Organisation Profile**
- Onboarding wizard: industry, sub-sector, size, regulatory jurisdictions, key compliance frameworks (PCI-DSS, SOX, HIPAA, GDPR, APRA, etc.)
- Technology preferences: cloud provider, preferred languages/frameworks, CI/CD tooling
- Organisational constraints: change freeze periods, release cadences, approval bodies

**2.2 — Knowledge Base (Document Upload)**
- Upload internal documents: architecture standards, technology radar, security policies, data classification guidelines, API design guides, compliance handbooks
- Supported formats: PDF, DOCX, Markdown, plain text, Confluence export
- Document management: view, replace, delete uploaded docs
- Per-document metadata: type (policy / standard / guideline), domain (architecture / security / legal / data), last reviewed date

**2.3 — RAG Pipeline**
- Document chunking and embedding (vector store — Supabase pgvector or dedicated vector DB)
- Context-aware retrieval: each agent queries the knowledge base for relevant org standards before generating
- Citation: generated output references specific internal documents ("Per your Architecture Decision Record ADR-047...")
- Grounding indicator: sections show which internal docs influenced the output

**2.4 — Context-Aware Generation**
- Architecture section aligns with org's approved technology radar
- Legal section maps to org's specific regulatory obligations (not generic GDPR boilerplate)
- Security section references org's data classification framework
- PRD follows org's story format and acceptance criteria conventions
- Business case uses org's financial templates and approval thresholds

**2.5 — Template Management**
- Org-specific section templates (override default structure)
- Custom fields per section (e.g., org requires a "Data Sovereignty" section)
- Template versioning as org standards evolve

### Validation Criteria
- Design partners confirm: "This output reflects our standards, not generic boilerplate"
- Content retention rate jumps from ~50% to ~70-80% with org context
- Time-to-first-draft for a real initiative drops from "weeks" to "hours" (measured)
- At least one design partner converts to paid pilot

### Business Milestone
- First paid pilot: $50-100K (6-12 month engagement)
- Pricing model validated (per-team or per-initiative)

### Key Risks
- RAG quality: if retrieval pulls irrelevant chunks, output quality degrades rather than improves — needs careful tuning
- Document sensitivity: enterprises will be cautious about uploading internal policies — need clear data handling story and eventually VPC options
- Onboarding friction: if setup takes weeks, enterprises lose patience — keep the org profile lean and iterate

---

## Phase 3 — Collaborative Review

> **Objective:** Expand from single-user tool to multi-stakeholder platform. Enable concurrent cross-divisional review that compresses alignment cycles. Expand from pilot to enterprise-wide contract.

### Why this phase matters
The core value proposition is that sequential stakeholder alignment becomes concurrent. But you can't deliver that with a single-user tool. Phase 3 is where Seedcraft becomes the platform where the cross-divisional review actually happens — not just where the document is generated.

### Features

**3.1 — Workspaces and Teams**
- Organisation-level workspace (all initiatives visible to authorised users)
- Team management: invite members, assign roles
- Initiative-level access control (who can view/edit which initiative)

**3.2 — Role-Based Views**
- Stakeholder roles: Product Owner, Architect, Legal Counsel, Security Reviewer, Compliance Officer, Business Line Lead, Engineering Lead
- Each role sees the full pack but their primary section is highlighted and surfaced first
- Role-specific summary: "Here's what you need to review and why"
- Customisable role definitions per organisation

**3.3 — Section-Level Review Workflow**
- Assign sections to specific reviewers (architecture section → enterprise architect)
- Review states per section: Draft → In Review → Changes Requested → Approved
- Reviewer can approve, request changes (with inline comments), or flag a blocker
- Dashboard showing review status across all sections and reviewers
- Blocked/unblocked status: "Legal has flagged a blocker on data residency — architecture section is paused pending resolution"

**3.4 — Inline Commenting and Discussion**
- Threaded comments on any paragraph, table row, or section
- @-mention stakeholders
- Resolve/unresolve threads
- Comment history preserved as audit trail

**3.5 — Cross-Section Conflict Detection**
- AI-powered detection: "The architecture section proposes storing PII in Region A, but the legal section identifies data residency restrictions requiring Region B"
- Surfaces contradictions between sections before humans have to find them
- Suggested resolution: "Consider deploying customer data services in Region B per Policy X"

**3.6 — Version History**
- Full diff view: what changed between versions
- Attribution: which changes were AI-generated vs. human-edited vs. reviewer-requested
- Rollback capability

**3.7 — Enterprise Authentication**
- SAML 2.0 / OIDC SSO integration (Okta, Azure AD, Ping)
- SCIM provisioning for automated user lifecycle
- MFA enforcement

**3.8 — Notifications**
- Email and in-app notifications for: review assignments, comments, approvals, blockers
- Digest mode for stakeholders who don't want real-time noise
- Integration-ready: Slack/Teams webhooks (Phase 4 extends this)

### Validation Criteria
- Full cross-divisional review conducted inside Seedcraft (not in email/Confluence alongside it)
- Measurable reduction in alignment cycles: from 3-4 rounds to 1-2
- Multiple business lines using the same workspace
- Net Promoter Score > 40 from enterprise reviewers

### Business Milestone
- First full enterprise contract: $100-300K ARR
- 3+ teams in the same organisation actively using the platform
- Expansion conversations: "Can we roll this out to other business lines?"

### Key Risks
- Adoption friction: getting 15 stakeholders to use a new tool when they already have Confluence and email is the hardest part of enterprise software. Need a champion inside the org.
- Workflow rigidity: every org's review process is slightly different. Need flexibility without building a general-purpose workflow engine.
- Notification fatigue: too many pings and stakeholders ignore the tool. Default to quiet, opt-in to noisy.

---

## Phase 4 — Technology Intelligence

> **Objective:** Map the technical blast radius of every initiative. Automatically identify which technology teams are affected, what dependencies exist, and where capacity conflicts will block delivery. Become the enterprise's product delivery nervous system.

### Why this phase matters
This is the moat. Organisation-specific technology intelligence — service catalogues, team ownership, API contracts, capacity constraints — is data that only exists inside each enterprise. Once Seedcraft has it, competitors can't replicate it. After 50 initiatives, Seedcraft knows more about the organisation's delivery topology than any single person. This is the layer that justifies $500K-1M+ ARR.

### Features

**4.1 — Service Catalogue Integration**
- Manual upload first: CSV/JSON of services, owners, dependencies (low friction onboarding)
- API integration later: pull from ServiceNow CMDB, Backstage, or custom catalogue
- Service metadata: name, owning team, tech stack, APIs exposed/consumed, data classification, SLA tier
- Keep alive: periodic re-sync to catch catalogue drift

**4.2 — Team and Ownership Mapping**
- Map services → teams → people
- Team metadata: capacity (story points/sprints available), current commitments, release cadence, change freeze windows
- Org hierarchy: business line → domain → team

**4.3 — Dependency Graph Generation**
- For each initiative: automatically identify affected services based on PRD and architecture sections
- Visualise dependency chain: "This feature touches Service A → which depends on Service B → owned by Team C"
- Depth-of-impact indicator: direct dependency vs. transitive dependency
- Interactive graph (click a service → see team, status, capacity)

**4.4 — Impact Brief Generation**
- Auto-generate a scoped brief for each affected technology team
- Brief contains: what's needed from them, estimated effort range, timeline constraints, relevant architectural context, dependencies on other teams
- Written in that team's context: references their service, their APIs, their tech stack
- Distributable: team lead gets a concise, actionable summary — not a 60-page inception pack

**4.5 — Capacity Conflict Detection**
- Cross-reference initiative timeline against team capacity and commitments
- Surface: "Team X is already committed to Initiative Y this quarter — cannot take on this dependency until Q3"
- Surface: "Service Z has a change freeze in weeks 8-12 — this dependency must be completed before or deferred"
- Suggest: re-sequencing options based on team availability

**4.6 — Cross-Initiative View**
- Portfolio-level dashboard: all in-flight initiatives and their overlapping dependencies
- "These 3 initiatives all depend on the Payments team in Q2 — risk of bottleneck"
- "Initiative A and Initiative B both propose changes to Service X — coordinate or sequence"
- Priority conflict resolution: which initiative takes precedence when resources collide

**4.7 — Precedent Engine**
- "A similar feature was delivered last year by the Wealth team — here's the initiative, the architecture decision, and the teams involved"
- Learning from historical initiatives: which dependencies were underestimated, which teams were bottlenecks, which compliance requirements were missed
- Feeds back into generation quality: future inception packs are more accurate based on past experience

### Validation Criteria
- Dependency graph accuracy: 80%+ of identified dependencies confirmed as real by engineering leads
- At least one instance where a dependency or capacity conflict was surfaced by Seedcraft that would have been discovered weeks later in manual process
- Engineering leads voluntarily check Seedcraft for impact briefs (pull, not push)

### Business Milestone
- Platform-level enterprise contracts: $300K-1M+ ARR
- Buyer shifts from Product/Transformation to CTO/VP Engineering office
- Multiple enterprises onboarded — beginning of repeatable sales motion

### Key Risks
- Service catalogue data quality: if the catalogue is stale or incomplete, dependency mapping is wrong and trust collapses. Need clear data freshness indicators and graceful handling of missing data.
- Integration complexity: every enterprise's CMDB, team structures, and capacity tracking is different. Can't build bespoke integrations for each customer — need a flexible ingestion model.
- Over-promising accuracy: LLM-generated dependency mapping will have false positives and false negatives. Must frame as "AI-assisted discovery" not "automated dependency detection." Humans still validate.

---

## Phase 5 — Enterprise Scale

> **Objective:** Remove all remaining barriers to enterprise procurement. Enable multi-tenant, regulated-industry deployment at scale.

### Why this phase matters
Phases 1-4 prove the product works. Phase 5 proves the company is enterprise-ready. Without SOC 2, VPC options, and proper data isolation, you can't pass procurement at most regulated enterprises. This phase is the difference between "we piloted it" and "we deployed it org-wide."

### Features

**5.1 — Compliance and Certifications**
- SOC 2 Type II certification
- ISO 27001 (required by many European and APAC enterprises)
- Penetration testing and vulnerability disclosure program
- Data processing agreements (DPA) and sub-processor list

**5.2 — Deployment Options**
- Multi-tenant SaaS (default, with data isolation per tenant)
- VPC deployment (customer's cloud, Seedcraft-managed)
- On-premise / air-gapped deployment (for defence, government, highly regulated)
- Data residency options: US, EU, APAC, AU regions

**5.3 — Fine-Grained Access Control**
- RBAC with custom role definitions
- Initiative-level, section-level, and field-level permissions
- Data classification enforcement: restrict who can see initiatives tagged as "Confidential"
- Admin console for org-level policy management

**5.4 — Audit Trail and Compliance Reporting**
- Immutable audit log: who generated, viewed, edited, approved, exported every artifact
- Compliance reports: exportable for internal audit and regulatory examination
- Retention policies: configurable per org (regulatory requirement in financial services)

**5.5 — API and Integration Platform**
- REST API for programmatic access (create initiatives, retrieve packs, trigger generation)
- Webhooks for lifecycle events (initiative created, section approved, blocker raised)
- Pre-built integrations: Jira (create epics/stories), Confluence (publish approved packs), ServiceNow (trigger change requests), Slack/Teams (notifications)
- Integration marketplace for customer-built connectors

**5.6 — Admin and Analytics**
- Org admin dashboard: user management, usage analytics, initiative pipeline
- Metrics: average time-to-approval, review cycle count, dependency discovery rate, content retention rate
- Executive reporting: "Seedcraft saved X review cycles across Y initiatives this quarter"
- Billing and subscription management

### Validation Criteria
- Pass enterprise security review at 2+ Tier 1 organisations
- SOC 2 Type II report issued
- At least one VPC deployment operational
- Multi-enterprise: 5+ paying enterprise customers

### Business Milestone
- $2-5M ARR across enterprise customers
- Repeatable sales and onboarding playbook
- Channel partnerships with 1-2 consulting firms
- Series A readiness

### Key Risks
- SOC 2 and compliance work is expensive and time-consuming (6-12 months, $50-200K)
- VPC deployment support is an ongoing operational burden — need to decide if it's strategic or a concession
- Building for multiple deployment models fragments engineering effort — prioritise SaaS, offer VPC only for largest contracts

---

## Phase Summary

| Phase | Objective | Key Deliverable | Validation Gate | Business Milestone |
|---|---|---|---|---|
| **1 — Enterprise Wedge** | Credible enough for design partner conversations | Editable output, PDF/DOCX export, section Q&A, enterprise positioning | 3-5 design partners on real initiatives | Design partner agreements |
| **2 — Org Context** | Output reflects the organisation's own standards | Knowledge base upload, RAG pipeline, context-aware generation | Content retention ≥70%, "this reflects our standards" | First paid pilot ($50-100K) |
| **3 — Collaborative Review** | Cross-divisional review happens inside Seedcraft | Role-based views, section review workflows, inline comments, SSO | Full review cycle completed in-platform, alignment cycles reduced | Enterprise contract ($100-300K ARR) |
| **4 — Tech Intelligence** | Map the blast radius of every initiative | Service catalogue, dependency graph, impact briefs, capacity conflicts | 80%+ dependency accuracy, conflicts surfaced early | Platform contracts ($300K-1M+ ARR) |
| **5 — Enterprise Scale** | Remove all procurement barriers | SOC 2, VPC deployment, RBAC, audit trail, API platform | Pass security review at Tier 1 orgs | $2-5M ARR, Series A ready |

---

## What to Build First Within Phase 1

Not everything in Phase 1 has equal leverage. Sequence by what unblocks design partner conversations fastest:

1. **Fix backend deployment** — can't demo a broken product
2. **PDF/DOCX export** — this is what gets forwarded to stakeholders; without it you're dead on arrival
3. **Reposition landing page** — enterprise visitors need to see enterprise language immediately
4. **Editable sections** — reviewers will reject a tool where they can't modify the output
5. **Section-level Q&A** — this is the "wow" moment in a demo; show that the AI can answer follow-ups about its own output grounded in full pack context

Items 1-3 unblock outreach. Items 4-5 are what you demo.

---

## Anti-Patterns to Avoid

1. **Don't build Phase 3 (collaboration) before proving Phase 2 (org context).** Collaboration on generic output is worthless. The output has to be good first.
2. **Don't build a general-purpose workflow engine.** You're not ServiceNow. Hard-code the review workflow to match 80% of enterprise review processes. Customise per customer only when a contract depends on it.
3. **Don't chase multiple verticals simultaneously.** Pick one: financial services, healthcare, or government. Nail the regulatory and architectural context for that vertical. Expand later.
4. **Don't price on seats.** Enterprise seat-based pricing penalises adoption. Price on value: per-initiative, per-workspace, or platform fee. You want 25 stakeholders reviewing, not 3 because the license is expensive.
5. **Don't build VPC deployment until a signed contract requires it.** The operational burden is enormous. SaaS-first, VPC only for $500K+ deals.
6. **Don't skip the human-in-the-loop.** The tool should never auto-approve anything. Every section needs human review and approval. Position as "AI-drafted, human-approved" — not "AI-decided." Regulated enterprises will reject anything that removes human judgment from the loop.
