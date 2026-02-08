# Seedcraft — Enterprise Deployment & Integration Strategy

> Last updated: February 2026

---

## The Core Tension

Seedcraft needs access to an enterprise's most sensitive internal documents — architecture standards, security policies, regulatory frameworks, service catalogues — to generate useful output. These documents are often classified as Confidential or Internal-Only. No regulated enterprise will upload them to an unknown startup's multi-tenant SaaS.

At the same time, Seedcraft is a startup. You cannot afford to manage bespoke on-premise deployments for each customer. You need to iterate fast, ship updates to all customers simultaneously, and keep operational costs manageable.

The answer isn't SaaS or on-prem. It's a hybrid architecture designed from day one to separate the **control plane** (the application, the UI, the orchestration logic) from the **data plane** (the customer's documents, embeddings, and generated artifacts).

---

## Data Classification

Before choosing a deployment model, understand what data you're handling and who owns it:

| Data Category | Sensitivity | Examples | Who owns it |
|---|---|---|---|
| **Platform code** | Seedcraft IP | Application, agents, prompts, orchestration | Seedcraft |
| **AI model** | Third-party | Gemini API | Google |
| **Organisation knowledge base** | Highly sensitive | Architecture standards, security policies, tech radar, compliance frameworks | Customer |
| **Generated inception packs** | Sensitive | AI-generated artifacts grounded in org data | Customer |
| **Integration credentials** | Critical | OAuth tokens for SharePoint, Confluence, ServiceNow | Customer |
| **User identity & sessions** | Moderate | Auth tokens, session history, preferences | Shared |
| **Embeddings / vector store** | Sensitive | Derived from org documents — can be reverse-engineered to reveal source content | Customer |
| **Usage analytics** | Low | Feature usage, generation counts, performance metrics | Seedcraft |

**The key principle:** Everything derived from customer data belongs to the customer and should reside where the customer controls it. Everything that makes Seedcraft work as a product belongs to Seedcraft and should be centrally managed.

---

## Deployment Models

### Model 1: SaaS with Tenant Isolation

```
┌─────────────────────────────────────────────────┐
│              SEEDCRAFT CLOUD                     │
│                                                  │
│  ┌──────────────┐   ┌────────────────────────┐  │
│  │  Control      │   │   Tenant A (isolated)  │  │
│  │  Plane        │   │  ┌──────────────────┐  │  │
│  │               │   │  │ Vector Store      │  │  │
│  │  - UI/App     │   │  │ Doc Storage       │  │  │
│  │  - Auth       │   │  │ Generated Packs   │  │  │
│  │  - Agent      │   │  └──────────────────┘  │  │
│  │    Orchestr.  │   ├────────────────────────┤  │
│  │  - Billing    │   │   Tenant B (isolated)  │  │
│  │               │   │  ┌──────────────────┐  │  │
│  └──────────────┘   │  │ Vector Store      │  │  │
│                      │  │ Doc Storage       │  │  │
│         │            │  │ Generated Packs   │  │  │
│         ▼            │  └──────────────────┘  │  │
│  ┌──────────────┐   └────────────────────────┘  │
│  │ Gemini API   │                                │
│  │ (Google)     │                                │
│  └──────────────┘                                │
└─────────────────────────────────────────────────┘
```

**How it works:**
- Single Seedcraft cloud instance serves all customers
- Each customer gets a logically isolated tenant: separate vector store, separate document storage, separate generated artifacts
- No data leaks between tenants (enforced at database and storage layer)
- All customers get updates simultaneously

**Good for:** Design partners, mid-market enterprises, less regulated industries, customers who accept cloud-hosted SaaS with a strong DPA

**Not good for:** Tier 1 banks, government, defence, healthcare systems with strict data sovereignty requirements

**When to offer this:** Phase 1 onwards. This is your default.

---

### Model 2: Customer Data Plane (Hybrid)

```
┌──────────────────────┐      ┌──────────────────────────┐
│   SEEDCRAFT CLOUD    │      │   CUSTOMER CLOUD (VPC)   │
│                      │      │                           │
│  ┌────────────────┐  │      │  ┌─────────────────────┐ │
│  │ Control Plane   │  │◄────►│  │ Data Plane Agent    │ │
│  │                 │  │ TLS  │  │                     │ │
│  │ - UI/App        │  │      │  │ - Vector Store      │ │
│  │ - Auth (SAML)   │  │      │  │ - Doc Storage       │ │
│  │ - Orchestration │  │      │  │ - Generated Packs   │ │
│  │ - Billing       │  │      │  │ - Connector Runtime │ │
│  └────────────────┘  │      │  │ - Embedding Engine  │ │
│                      │      │  └─────────────────────┘ │
│  ┌────────────────┐  │      │                           │
│  │ Gemini API     │  │      │  ┌─────────────────────┐ │
│  │ (can also be   │  │      │  │ Enterprise Systems  │ │
│  │  customer's    │  │      │  │ - SharePoint        │ │
│  │  Vertex AI)    │  │      │  │ - Confluence        │ │
│  └────────────────┘  │      │  │ - ServiceNow        │ │
│                      │      │  │ - Backstage         │ │
└──────────────────────┘      │  └─────────────────────┘ │
                              └──────────────────────────┘
```

**How it works:**
- Seedcraft control plane (UI, auth, orchestration logic) runs in Seedcraft's cloud
- A lightweight **Data Plane Agent** runs inside the customer's cloud (their AWS/Azure/GCP VPC)
- All customer documents, embeddings, and generated artifacts stay inside the customer's network boundary
- The Data Plane Agent handles: document ingestion, embedding generation, vector storage, connector runtime
- The control plane sends orchestration instructions to the data plane agent; the agent returns results
- LLM calls can go through Seedcraft's Gemini API or through the customer's own Vertex AI / Azure OpenAI endpoint
- No raw customer documents ever leave the customer's cloud

**The Data Plane Agent is the key architectural concept.** It's a containerised service (Docker/K8s) that Seedcraft deploys and manages inside the customer's environment. It's the bridge between Seedcraft's intelligence and the customer's data — without the data leaving.

**Good for:** Tier 1 banks, insurers, healthcare, government — anyone who says "our data cannot leave our cloud"

**Not good for:** Very early stage (too complex to build initially)

**When to offer this:** Phase 3-4. Don't build this until you have paying customers who require it. But **design your architecture now** so that the migration from Model 1 to Model 2 is not a rewrite.

---

### Model 3: Full Private Deployment

```
┌──────────────────────────────────────────┐
│        CUSTOMER ENVIRONMENT              │
│       (On-Prem / Air-Gapped)             │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │        SEEDCRAFT (Full Stack)     │   │
│  │                                   │   │
│  │  - Control Plane                  │   │
│  │  - Data Plane                     │   │
│  │  - UI/App                         │   │
│  │  - Agent Orchestration            │   │
│  │  - Vector Store                   │   │
│  │  - Local LLM (or customer's      │   │
│  │    private Vertex AI / Azure OAI) │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Enterprise Systems               │   │
│  │  SharePoint / Confluence / etc.   │   │
│  └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

**How it works:**
- Entire Seedcraft stack deployed inside customer's environment
- No outbound network calls (air-gapped capable)
- LLM is either customer's own (Vertex AI, Azure OpenAI) or a locally-hosted model
- Seedcraft ships updates as versioned container images; customer controls upgrade cadence

**Good for:** Defence, intelligence agencies, central banks, government with air-gap requirements

**Not good for:** Anyone else. Operational overhead is massive.

**When to offer this:** Phase 5, and only for $500K+ ARR contracts that justify the support cost. Consider partnering with a systems integrator (Accenture, Deloitte) to handle deployment and support.

---

## Recommended Progression

| Phase | Deployment Model | Why |
|---|---|---|
| Phase 1-2 | SaaS with tenant isolation | Fast to build, fast to iterate. Design partners accept this with a DPA. |
| Phase 3 | SaaS + customer data plane option | First enterprise contracts will demand that their data stays in their cloud. Build the data plane agent. |
| Phase 4 | Hybrid as default, SaaS as entry | Most customers use hybrid. SaaS remains for onboarding and evaluation. |
| Phase 5 | Full private deployment available | Only for the largest contracts. Partner with SIs for delivery. |

**Critical architectural decision:** Design the control plane / data plane separation from Phase 2 onward, even if you only deploy Model 1 initially. If you build a monolith that assumes all data is co-located with the app, migrating to Model 2 later is a rewrite.

---

## Integration Architecture: Connecting to Enterprise Data

### Where the Context Lives

Enterprises don't have a single source of truth. The context Seedcraft needs is spread across many systems:

| System | What it contains | Relevance to Seedcraft |
|---|---|---|
| **Confluence** | Architecture Decision Records, design docs, runbooks, team pages, standards | Architecture, PRD, and technical context |
| **SharePoint / OneDrive** | Policies, compliance frameworks, security standards, executive presentations | Legal, compliance, security context |
| **ServiceNow** | CMDB (service catalogue), change requests, incident history, team ownership | Technology intelligence, dependency mapping |
| **Jira** | Backlogs, epics, sprint commitments, team capacity | Capacity awareness, existing roadmap context |
| **Backstage / Developer Portal** | Service catalogue, API specs, tech radar, ownership | Architecture, dependency mapping |
| **Google Drive / Docs** | Policies, meeting notes, research docs | General context |
| **Slack / Teams** | Decision threads, stakeholder discussions (historical) | Alignment context, precedent |
| **GRC Tools (Archer, OneTrust)** | Risk registers, compliance obligations, control frameworks | Legal, compliance context |
| **Git Repositories** | Code, ADRs in code, README files, API contracts | Technical architecture context |

### Connector Architecture

Rather than building bespoke integrations, build a **connector framework** — an abstract layer that any data source plugs into:

```
┌─────────────────────────────────────────────────────┐
│                 CONNECTOR FRAMEWORK                  │
│                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │SharePt  │ │Confluenc│ │ServiceNw│ │Backstage│  │
│  │Connector│ │Connector│ │Connector│ │Connector│  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│       │           │           │            │        │
│       ▼           ▼           ▼            ▼        │
│  ┌──────────────────────────────────────────────┐   │
│  │              SYNC ENGINE                      │   │
│  │                                               │   │
│  │  Connect → Crawl → Extract → Chunk → Embed   │   │
│  │                                               │   │
│  │  - Incremental sync (only changed docs)       │   │
│  │  - Permission mapping                         │   │
│  │  - Freshness tracking                         │   │
│  │  - Conflict resolution                        │   │
│  └──────────────────────────────────────────────┘   │
│                      │                               │
│                      ▼                               │
│  ┌──────────────────────────────────────────────┐   │
│  │            VECTOR STORE                       │   │
│  │   (per-tenant, isolated)                      │   │
│  │                                               │   │
│  │   Chunks + metadata + source tracking         │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Connector Interface

Every connector implements the same interface:

```
Connector:
  authenticate()        → OAuth 2.0 flow, store tokens securely
  list_sources()        → return available spaces/sites/repos
  configure(sources)    → admin selects which sources to index
  crawl(since?)         → enumerate documents, return metadata
  extract(doc_id)       → return document content + metadata
  get_permissions(doc)  → return who can access this document
  watch(callback)       → real-time updates via webhooks (optional)
```

This means adding a new source (e.g., Notion, Google Drive) is implementing one interface — not rebuilding the pipeline.

### Source-Specific Integration Notes

**SharePoint / OneDrive**
- API: Microsoft Graph API
- Auth: OAuth 2.0 with Azure AD app registration (admin consent required)
- Sync: Delta queries (`/delta` endpoint) for efficient incremental sync
- Permissions: Maps to Azure AD groups/users — can enforce in Seedcraft
- Gotchas: Rate limiting is aggressive (429s common). Need backoff strategy. Large tenants have millions of files — selective sync is essential.
- Deployment: Customer's IT admin must register the Seedcraft app in their Azure AD and grant permissions. This is a procurement/IT gate.

**Confluence (Cloud & Data Center)**
- API: Atlassian REST API v2 (Cloud) or v1 (Data Center/Server)
- Auth: OAuth 2.0 (Cloud) or Personal Access Tokens (Data Center)
- Sync: CQL queries with `lastModified` filtering for incremental sync. Webhooks available for real-time.
- Permissions: Space-level and page-level restrictions. Confluence API respects user permissions if using delegated auth.
- Gotchas: Data Center/Server versions are on-prem — connector must run inside customer network (data plane agent). Cloud version is straightforward.
- Sweet spot: Architecture Decision Records, design documents, and team standards live here at most enterprises. This is likely the highest-value first connector.

**ServiceNow**
- API: Table API (REST) and CMDB API
- Auth: OAuth 2.0 or basic auth with service account
- Sync: `sys_updated_on` field for incremental queries
- Data: CMDB contains service catalogue, CI relationships, team ownership — critical for Phase 4 technology intelligence
- Gotchas: Every ServiceNow instance is heavily customised. Field names, table structures, and relationships vary wildly across enterprises. Need flexible field mapping.
- When: Phase 4 (technology intelligence). Not needed for Phase 2.

**Jira**
- API: Atlassian REST API v3
- Auth: OAuth 2.0 (Cloud) or PAT (Data Center)
- Data: Epics, stories, sprint capacity, team velocity — useful for capacity awareness
- Sync: JQL queries with `updated` filtering
- When: Phase 4. Lower priority than Confluence and SharePoint for Phase 2.

**Backstage / Internal Developer Portal**
- API: REST API (varies by instance), Software Catalogue API
- Data: Service catalogue, API specs, tech radar, ownership
- Auth: Varies (often internal-only, behind VPN)
- When: Phase 4. Requires data plane agent (runs inside customer network).

### Connector Prioritisation

| Priority | Connector | Phase | Rationale |
|---|---|---|---|
| **1st** | Document upload (manual) | Phase 2 | Zero integration complexity. Gets you started immediately. |
| **2nd** | Confluence Cloud | Phase 2-3 | Highest-value content (ADRs, standards). Most enterprises have it. Well-documented API. |
| **3rd** | SharePoint / OneDrive | Phase 2-3 | Policies, compliance docs, security standards live here. Microsoft Graph API is mature. |
| **4th** | ServiceNow CMDB | Phase 4 | Service catalogue and team ownership — critical for technology intelligence layer. |
| **5th** | Jira | Phase 4 | Capacity awareness and roadmap context. |
| **6th** | Git repositories | Phase 4 | API specs, ADRs-as-code, technical context. |
| **7th** | Backstage | Phase 4-5 | Tech radar, service catalogue — overlaps with ServiceNow. |
| **8th** | GRC tools | Phase 5 | Compliance frameworks, risk registers. Niche but high-value for regulated industries. |

### The Manual Upload Bridge

Don't wait for connectors to deliver org context. Phase 2 starts with manual document upload:

1. Admin uploads PDFs/DOCX/markdown files
2. Files are chunked, embedded, and stored in the tenant's vector store
3. Agents query the vector store during generation
4. Output references uploaded documents

This is low-tech but it validates the core hypothesis: does org-specific context make the output meaningfully better? If it does, connectors automate what users are already doing manually. If it doesn't, connectors won't save you.

---

## Where the LLM Sits

This is a decision enterprise customers will ask about explicitly.

### Option A: Seedcraft-Managed LLM (Default)

- Seedcraft calls Gemini API (or other models) using Seedcraft's API keys
- Customer's data is sent to the LLM provider for processing
- Covered by Seedcraft's DPA with Google (Gemini) — Google does not train on API data
- Simplest for Seedcraft to manage

**Acceptable for:** Most enterprises with a clear DPA. Google's Gemini API has enterprise data processing agreements.

**Not acceptable for:** Enterprises that prohibit any customer data from being processed by third-party AI providers (some banks, government).

### Option B: Customer's Own LLM Endpoint

- Customer provides their own Vertex AI (Google) or Azure OpenAI endpoint
- Seedcraft sends prompts to the customer's endpoint instead of Seedcraft's
- Customer controls data processing, region, and retention
- Customer pays their own LLM inference costs

**How it works technically:**
- Seedcraft's agent orchestration is model-agnostic (LangGraph supports multiple providers)
- Customer configures their LLM endpoint URL and credentials in their org settings
- All inference calls are routed to the customer's endpoint
- Seedcraft never sees the raw LLM responses if using the data plane agent model

**Acceptable for:** Enterprises that require full control over AI data processing. This is the answer to "where does our data go when the AI processes it?"

### Option C: Local/Private LLM (Phase 5)

- LLM runs inside customer's environment (e.g., self-hosted Llama, Mistral, or Google's Gemma)
- No data leaves the customer's network
- Quality may be lower than frontier models — needs testing

**Only for:** Air-gapped environments. Defence, intelligence, central banks.

### Recommended Default

Phase 1-2: Option A (Seedcraft-managed Gemini). Fastest, simplest.
Phase 3-4: Option A default, Option B available for customers who require it.
Phase 5: All three options available.

In the sales process, being able to say "your data can be processed by your own Vertex AI endpoint in your own GCP project" removes the single biggest objection to AI tools in regulated enterprises.

---

## Permission and Access Control Model

Connecting to enterprise systems means inheriting their permission models. This is critical — if Seedcraft surfaces content from a Confluence page that a user doesn't have access to, it's a data breach.

### Principle: Seedcraft Never Elevates Permissions

If a user cannot access a document in SharePoint, Seedcraft must not use that document's content when generating output for that user. The generated inception pack should only be grounded in documents the requesting user (or their role) is authorised to see.

### Implementation Approaches

**Approach 1: Service Account with Post-Filtering (Simpler)**
- Connector uses a service account with broad read access to index all authorised documents
- At query time, filter vector store results against the requesting user's permissions
- Permissions are synced periodically from the source system

**Approach 2: Delegated Access (Stricter)**
- Connector uses the requesting user's own OAuth token to access source systems
- Only documents the user can see are retrieved
- More secure but slower (can't pre-index) and requires per-user OAuth tokens

**Recommended:** Approach 1 for indexing (background sync with service account), with permission filtering at query time. Sync permissions from source systems on a schedule (hourly or daily). This balances security with performance.

---

## Data Residency and Compliance

### What Enterprises Will Ask

1. "Where is our data stored?" → Must be able to answer with a specific region (e.g., AU, EU, US)
2. "Is our data isolated from other customers?" → Yes, per-tenant isolation
3. "Can our data be processed in our own cloud?" → Yes, via customer data plane or customer LLM endpoint
4. "Do you have SOC 2?" → Phase 5. Until then: DPA, security questionnaire, architecture review
5. "Can we audit what the AI did with our data?" → Yes, generation audit trail showing inputs, outputs, and sources referenced
6. "What happens to our data if we cancel?" → Data export + deletion within 30 days, certificate of destruction

### Regional Deployment Options (Phase 5)

| Region | Cloud | Rationale |
|---|---|---|
| Australia (Sydney) | GCP / AWS | APRA-regulated financial services |
| EU (Frankfurt / Ireland) | GCP / AWS | GDPR data residency |
| US (Virginia / Oregon) | GCP / AWS | US financial services, healthcare |
| UK (London) | GCP / AWS | UK FCA-regulated firms post-Brexit |

For Phases 1-3, deploy in a single region (likely AU or US depending on your first customers) and be transparent about it.

---

## Recommended Architecture for Phase 2

Keep it simple. Don't build the full hybrid architecture yet. Build the SaaS version with clean separation so it can evolve:

```
┌──────────────────────────────────────────────────┐
│                  SEEDCRAFT SAAS                   │
│                                                   │
│  ┌─────────────┐    ┌───────────────────────┐    │
│  │  Frontend    │    │  Backend (FastAPI)     │    │
│  │  (React)     │───►│                       │    │
│  │              │    │  - Auth (Supabase)     │    │
│  └─────────────┘    │  - Agent Orchestration │    │
│                      │  - Doc Upload API      │    │
│                      │  - RAG Query API       │    │
│                      └───────┬───────────────┘    │
│                              │                     │
│              ┌───────────────┼───────────────┐    │
│              ▼               ▼               ▼    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│  │ Supabase     │ │ Vector Store │ │ Gemini   │ │
│  │ PostgreSQL   │ │ (pgvector /  │ │ API      │ │
│  │              │ │  Pinecone)   │ │          │ │
│  │ - Sessions   │ │              │ │          │ │
│  │ - Users      │ │ - Embeddings │ │          │ │
│  │ - Org Config │ │ - Chunks     │ │          │ │
│  │ - Packs      │ │ - Metadata   │ │          │ │
│  └──────────────┘ └──────────────┘ └──────────┘ │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  Document Storage (per-tenant)            │    │
│  │  Supabase Storage / S3                    │    │
│  │  - Uploaded docs (original files)         │    │
│  │  - Processing status                      │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

**Key design decisions for Phase 2:**
1. Per-tenant vector store namespace (not a shared index) — makes future migration to customer data plane trivial
2. Document storage uses Supabase Storage with row-level security — each org only sees their docs
3. Org config table in PostgreSQL — stores industry, regulatory frameworks, tech preferences
4. RAG query API is a separate service boundary — can be extracted to the data plane agent later without changing the frontend or orchestration layer

---

## Summary: The Deployment Strategy in One Page

**Phase 1-2:** SaaS multi-tenant. Manual document upload. Seedcraft-managed Gemini. Data in Seedcraft's cloud with per-tenant isolation and DPA.

**Phase 2-3:** Add Confluence and SharePoint connectors. Still SaaS, but data is now continuously synced from customer systems (with customer's OAuth consent). Customer can revoke access at any time.

**Phase 3-4:** Introduce customer data plane option. Customer's documents and embeddings stay in their cloud. Seedcraft control plane orchestrates remotely. Customer can use their own Vertex AI/Azure OpenAI endpoint. This unlocks Tier 1 regulated enterprises.

**Phase 5:** Full deployment flexibility. SaaS / hybrid / private. Multi-region. SOC 2 certified. Air-gap capable for defence/government.

**The architectural principle that makes this work:** Build the control plane / data plane separation cleanly in Phase 2. Don't hard-code data access into the orchestration layer. Every document read, every vector query, every LLM call should go through an abstraction that can be pointed at a local service or a remote one. Do this once and the migration path from Model 1 → Model 2 → Model 3 is configuration, not code.
