# Seedcraft — YC-Style Assessment

> Generated: February 2026
> Perspective: Y Combinator Partner evaluation of Seedcraft as an enterprise product lifecycle platform for large regulated organisations.

---

## 1. Clarity Test

**Problem (one sentence):**
In large regulated enterprises, getting a product idea from concept to approved-for-development takes 3-12 months because 15-25 stakeholders across business lines, architecture, legal, security, compliance, and privacy must align — sequentially, each with veto power, none reporting to each other.

**Is it real, frequent, and painful?**
Yes. This is one of the most painful structural problems in enterprise software delivery. It kills good ideas at banks, insurers, telecoms, and government agencies. A feature that touches payments, customer data, and a third-party API might need sign-off from product, architecture, security, legal, compliance, data privacy, and procurement — each with a 2-6 week review cycle, often sequential. A 3-month idea becomes a 12-month initiative before a line of code is written.

**Who feels this pain most?**
- Product owners and delivery leads in Tier 1 banks, insurance companies, healthcare systems, government agencies
- Heads of engineering who lose 40-60% of their capacity to "governance overhead"
- CTOs / VP Engineering managing cross-team technology dependencies
- Transformation/innovation teams measured on time-to-market

**Is it solved well enough?**
No. Current solutions:
- Confluence templates and manual document creation (slow, inconsistent)
- PowerPoint decks circulated via email (no structured review)
- ServiceNow/Jira workflows (track the process but don't accelerate the content)
- Consulting firms (expensive, slow, output still needs internal review)

Nobody is using AI to pre-populate cross-divisional artifacts with organisation-specific context and surface dependencies before the first meeting.

---

## 2. Solution & Product

**What Seedcraft does:**
Generates a unified inception brief — pre-populated from the organisation's own policies, architecture standards, and regulatory obligations — that surfaces cross-divisional conflicts, dependencies, and constraints before the first meeting happens. Every stakeholder reviews concurrently instead of sequentially.

**Three-layer product vision:**

```
Layer 1: AI-generated inception brief (built today)
         ↓ feeds into
Layer 2: Cross-divisional stakeholder alignment
         (business lines, legal, security, compliance, privacy)
         ↓ feeds into
Layer 3: Technology dependency mapping and team coordination
         (service catalogue, team capacity, API contracts, release cadences)
```

Layer 1 is a document generator. Layer 2 is a decision compression platform. Layer 3 is enterprise delivery infrastructure. Each layer increases value, stickiness, and defensibility by an order of magnitude.

**Is this 10x better?**
The current build generates generic output. The vision — ingesting an enterprise's internal context (architecture standards, approved technology radar, regulatory obligations, data classification policies, security frameworks, existing service catalogue) and generating first-draft artifacts 70-80% aligned with that specific organisation's requirements — compresses weeks into hours. Human reviewers edit and approve rather than create from scratch.

**Key assumptions:**
1. Enterprises will allow internal data into the platform (requires VPC/on-prem deployment options)
2. LLM-generated first drafts are good enough that reviewers save time vs. starting from scratch
3. Integration with enterprise toolchain (Confluence, Jira, ServiceNow, SharePoint) is achievable

**Product wedge:**
The kickoff artifact — the single document circulated before the first cross-divisional review meeting. If Seedcraft generates a unified brief that every stakeholder can annotate from their perspective before they meet, it eliminates 2-3 alignment cycles. Every enterprise PM understands this value in one sentence.

---

## 3. The Stakeholder Alignment Problem

In a large enterprise, a single product initiative crosses:

| Stakeholder | What they need to see | Why they currently block |
|---|---|---|
| **Business line product owners** | Revenue impact, customer journeys, scope boundaries, dependencies on their roadmap | "This wasn't on our roadmap" / "How does this affect our P&L?" |
| **Enterprise architecture** | Tech stack alignment, integration points, service catalogue fit, scalability | "This doesn't conform to our standards" |
| **Legal** | Regulatory exposure, licensing, contractual implications, liability | "Has anyone checked if we can even do this?" |
| **Security / CISO** | Data flows, authentication model, threat surface, classification levels | "What data are we moving and where?" |
| **Compliance** | Regulatory mapping, audit trail, reporting obligations | "Which regulations apply and are we covered?" |
| **Data privacy / DPO** | PII handling, consent flows, DPIA requirements, cross-border transfers | "We need a privacy impact assessment first" |
| **Procurement** | Third-party dependencies, vendor risk, cost implications | "Is this a new vendor relationship?" |
| **Other business lines** | Cross-divisional dependencies, shared services impact, data sharing agreements | "Nobody told us this would affect our system" |

Today, these conversations happen sequentially because each function discovers the implications only when the document reaches their desk. Legal finds a regulatory issue at week 8 that invalidates what architecture approved at week 3. A downstream business line learns at week 10 that their API is a dependency, and they haven't planned capacity.

**Seedcraft's structural advantage:** The AI considers all dimensions in parallel from minute one. The architect's section already reflects legal constraints. The legal section already accounts for data flows in the technical architecture. The business case already flags cross-divisional dependencies. Nobody is surprised in the review meeting because the draft pre-surfaced the conflicts.

---

## 4. Technology Team Alignment

Technology in a large enterprise isn't one team. It's dozens of teams owning different platforms, services, and domains — each with their own backlog, release cadence, tech debt, and capacity constraints. A single product initiative can create work for 5-10 technology teams who didn't ask for it and aren't planning for it.

**Example:** A retail banking product owner wants a new onboarding flow. But:
- **Identity platform team** needs a new verification method — mid-migration, can't take it until Q3
- **Core banking team** needs a new account type — change freeze in 4 weeks
- **API gateway team** needs a new route and rate limiting — capacity-constrained
- **Data platform team** needs a new event stream — migrating to new pipeline
- **Mobile team** needs new screens — committed to another business line this quarter
- **Payments team** is a downstream dependency nobody flagged — needs DPIA and PCI scope review

**What Seedcraft does with internal context:**

| Capability | Impact |
|---|---|
| **Map technical dependencies automatically** | "This feature requires changes to 6 services owned by 4 teams" — surfaced at day 1, not week 10 |
| **Flag capacity conflicts** | "The Identity team has a change freeze weeks 8-12; this dependency needs to be raised now" |
| **Generate team-specific impact briefs** | Each technology team gets a scoped summary of what's needed from them, in their language, with their context |
| **Identify integration risks** | "Service A exposes a v1 API being deprecated in Q3 — this feature depends on it" |
| **Surface precedent** | "A similar feature was delivered last year by the wealth team — here's how they handled the payments dependency" |

---

## 5. Market & Timing

**TAM/SAM/SOM:**
- TAM: Enterprise product lifecycle management / governance tooling (~$8-12B)
- SAM: AI-assisted enterprise delivery acceleration for regulated industries (~$2-4B, growing fast)
- SOM: Architecture and compliance review automation for Tier 1 financial services and healthcare — $200-500M addressable in year 1-3

**Why now:**
1. LLMs are finally good enough to generate structured technical and regulatory documents
2. Regulatory pressure is increasing (AI Act, DORA, updated GDPR enforcement) — more review gates, not fewer
3. Enterprise AI adoption hit an inflection point in 2025-2026 — CIOs have AI budget line items

**Early adopters:**
Innovation teams and digital transformation leads at banks and insurers. They have budget, pain, and mandate to demonstrate AI adoption. Find 3-5 design partners through network or enterprise AI conferences (Gartner, Forrester events).

---

## 6. Monetization & Distribution

**Revenue model:** Enterprise SaaS. Per-seat or per-team licensing. $2-5K/month per team, or $50-150K/year per enterprise. With technology alignment layer: $300K-1M+ ARR (platform-level spend).

**Distribution channels:**
- Direct enterprise sales (required at this price point)
- Design partner program with 3-5 enterprises (build with them, convert to paying)
- Channel partnerships with consulting firms (Accenture, Deloitte, Thoughtworks)
- Marketplace plays (ServiceNow, Atlassian Marketplace)

**Unit economics:** Enterprise SaaS margins 70-85%. AI inference costs manageable at enterprise price points. A $100K/year contract absorbs thousands of LLM calls.

---

## 7. Competition & Moat

**Direct competitors:**
- Ardoq / LeanIX — enterprise architecture management (adjacent, not AI-generative)
- Planview / Aha! — product portfolio management (workflow, not content generation)
- ServiceNow — governance workflows (tracks process, doesn't generate artifacts)
- McKinsey / Deloitte — consulting (expensive humans doing what AI could draft)
- Generic AI tools (Copilot, ChatGPT Enterprise) — no workflow, no org context, no multi-stakeholder review

**Durable moat (if vision is executed):**

1. **Organisation-specific knowledge base** — once you've ingested a bank's architecture standards, technology radar, regulatory obligations, and policy documents, switching costs are enormous
2. **Workflow lock-in** — if architecture review boards, legal teams, and security teams all route through Seedcraft, it becomes infrastructure. Rip-out cost is high
3. **Data flywheel** — every approved artifact teaches the system what "good" looks like for that organisation. First drafts improve over time. Competitors starting fresh can't match this
4. **Technology dependency graph** — after 50 initiatives, Seedcraft knows more about the enterprise's delivery topology than any single person. Which teams are always bottlenecks. Which APIs break. Which compliance requirements get missed. Not replicable by a competitor
5. **Compliance audit trail** — in regulated industries, tracked review decisions have regulatory value. Once in the audit trail, you don't get removed

**Could an incumbent crush this?**
ServiceNow or Atlassian could build it but won't — too vertical and too AI-native for their product orgs. Microsoft Copilot is horizontal, not workflow-specific. Real risk: a well-funded startup with enterprise sales DNA getting there first.

---

## 8. Buyer & Pricing by Layer

| Aspect | Layer 1 (current) | Layer 2 (stakeholder alignment) | Layer 3 (technology alignment) |
|---|---|---|---|
| **Buyer** | Product owner / innovation team | Head of Product / Transformation lead | CTO / VP Engineering / Head of Delivery |
| **Budget** | Innovation budget | Product/transformation budget | Engineering productivity budget (largest) |
| **Value metric** | Time to first draft | Time-to-approval | Time-to-market across full dependency chain |
| **Price point** | $50-100K ARR | $100-200K ARR | $300K-1M+ ARR |
| **Stickiness** | Useful tool | Decision infrastructure | Delivery infrastructure — removing it breaks planning |

---

## 9. Execution & Risks

**Top 3 existential risks:**

1. **Enterprise trust and deployment model.** Regulated enterprises will not send internal architecture docs and policies to a multi-tenant SaaS. Need SOC 2 Type II, VPC deployment, data residency controls, enterprise SSO. 6-12 months of infrastructure work before first enterprise deal closes.

2. **The "70% good" problem.** If AI-generated first drafts are only 50% usable, reviewers spend as much time fixing as writing from scratch, and the tool becomes shelfware. Must validate that output quality with org-specific context crosses the threshold where reviewers genuinely save time.

3. **Sales motion.** Enterprise AI tools are sold, not adopted. Need at least one person who can run consultative sales, discovery calls, pilots, and navigate procurement. If founding team is purely technical, need a co-founder or early hire who's sold $100K+ enterprise software.

**What to test first (cheaply):**
- Take the current tool. Find one enterprise through network. Run 3-5 real product ideas through it. Sit with architecture reviewers, legal, and product owners as they read output. Measure: how much of generated content did they keep vs. rewrite? If 60%+ is kept, there's something. If 80% is rewritten, AI generation isn't the bottleneck.

**Key success metrics:**
- Content retention rate (% of generated artifact kept after human review)
- Time-to-approval reduction vs. baseline manual process
- Number of review cycles eliminated
- Cross-team dependency discovery accuracy
- Net Promoter Score from enterprise reviewers (architects, legal, security)
- Repeat usage rate (does the organisation run a second initiative through the tool?)

---

## 10. Gap Analysis: What Exists vs. What's Needed

| What exists today | What the enterprise vision requires |
|---|---|
| Generic Gemini output | RAG over internal org docs (architecture standards, policies, tech radar) |
| Public market research | Integration with internal data (Jira, Confluence, ServiceNow, internal wikis) |
| One-shot generation | Iterative human-in-the-loop review workflow with role-based approvals |
| Single user | Multi-stakeholder collaboration (architect reviews arch section, legal reviews legal section) |
| No org context | Tenant-specific knowledge base per enterprise customer |
| Free, no auth model | Enterprise SSO (SAML/OIDC), RBAC, audit trails |
| Multi-tenant SaaS | VPC / on-prem deployment options |
| No compliance certs | SOC 2 Type II, ISO 27001 |
| No service catalogue integration | Maps to org's actual services, teams, APIs, and capacity |

---

## 11. Final Verdict

**Would I fund this? Maybe — leaning toward yes with conditions.**

**The problem is real, large, and painful.** The market is big and underserved. The timing is right. The technical foundation demonstrates ability to build.

**Conditions for a clear yes:**
1. One signed LOI or paid pilot with a Tier 1 bank, insurer, or healthcare system
2. A co-founder or advisor with enterprise sales DNA in regulated industries
3. A working demo that ingests one organisation's actual architecture standards and generates artifacts that their real reviewers say "this saves me 60% of my time"

---

## 12. The Pitch

*"In large regulated enterprises, a single product initiative touches 15-25 stakeholders across business lines, architecture, legal, security, compliance, and privacy — plus 5-10 technology teams who each own a piece of the dependency chain. None report to each other. All have veto power. Today they align sequentially: architecture reviews at week 3, legal flags a blocker at week 8, a downstream business line discovers they're a dependency at week 10, and the payments team learns they need a PCI scope review at week 12.*

*Seedcraft maps the full blast radius of a product initiative — business impact, regulatory exposure, technical dependencies, and team capacity constraints — from your organisation's own service catalogue, policies, and standards. Every affected team and stakeholder gets a scoped, context-aware brief on day one. Sequential discovery becomes concurrent alignment. We compress 6-12 months of cross-org coordination into days."*
