# Design Brief: Seedcraft UI

## Product Context

**Seedcraft** is an enterprise AI platform that compresses the idea-to-outcome cycle for large, complex organizations.

### The Problem It Solves

Enterprise product teams don't lack ideas — they lack velocity. Discovery takes months. Stakeholder alignment takes longer. By the time there's a business case, competitors have shipped. And 80% of what finally launches? Never used.

### What Seedcraft Does

- Ingests enterprise context (industry, regulations, tech stack, constraints, budget, stakeholders)
- Deploys 12+ specialized AI agents across 3 coordinated swarms (Discovery, Strategy, Delivery)
- Generates a 16-section inception pack — validated, cross-referenced, critique-checked
- Delivers decision-ready outputs in ~12 minutes, not months

### The 16 Sections

1. Executive Summary
2. Customer Research (with evidence tiers E1-E4)
3. Competitive Analysis
4. Personas
5. Business Case (Lean Canvas, unit economics)
6. Go-to-Market Strategy
7. Financial Model
8. Product Requirements (PRD with epics/stories)
9. Technical Architecture (with Mermaid diagrams)
10. Legal & Regulatory Review
11. Risk Assessment
12. Wireframes (React components)
13. Interactive Prototype
14. Stakeholder Views (CFO, CTO, CISO-specific summaries)
15. Validation Playbook (prioritized experiments)
16. Quality Assessment (critique-validated scoring)

### Key Differentiators

- **Context-aware:** Works with YOUR constraints, not generic assumptions
- **Full lifecycle:** Discovery → Strategy → Delivery in one session
- **Critique-validated:** AI agents cross-check each other before output
- **Evidence-tiered:** Every claim tagged with confidence level (E1-E4)
- **Stakeholder-ready:** Tailored views for different decision-makers

### Target Users

- VP/Director of Product at Fortune 500
- Chief Innovation Officers
- CTOs evaluating new initiatives
- Enterprise strategy teams
- Corporate venture arms

### Competitive Frame

Not a chatbot. Not a document generator. An outcome accelerator that turns enterprise context into decision-ready inception packs — replacing months of discovery workshops, siloed research, and misaligned kickoffs.

### Tone of the Product

Competent. Confident. Enterprise-grade without being sterile. The tool a seasoned product leader would trust to prepare materials for a board presentation.

---

## Pages Needed

### 1. Landing Page

**Purpose:** Convert enterprise visitors. Communicate value proposition clearly.

**Content hierarchy:**
- Hero: Headline + subheadline + primary CTA
- Problem statement: Why discovery is broken
- How it works: Input → Swarms → Output (simple, not over-designed)
- What you get: The 16 sections (scannable, not overwhelming)
- Trust signals: Enterprise-grade features (evidence tiers, critique validation, stakeholder views)
- Final CTA: Drive to input page

**Design should feel:** Confident and sparse. Like Linear or Vercel — not cluttered SaaS template. Typography does the heavy lifting. Minimal decoration.

**Key copy:**
- Headline: "Accelerate your enterprise from idea to outcome."
- Subheadline: "Seedcraft ingests your enterprise context and deploys AI agent swarms to compress the entire discovery-to-delivery lifecycle. Decision-ready inception packs in minutes, not months."
- CTA: "Accelerate Your Next Initiative"

---

### 2. Input Page

**Purpose:** Capture product idea + enterprise context.

**Sections:**
- Product idea (name + description)
- Target market & customers
- Enterprise context (industry, company size, regulations)
- Technical context (tech stack, constraints)
- Business constraints (budget, timeline, funding stage)
- Key stakeholders to address

**Design should feel:** Guided but not patronizing. Clean form, clear hierarchy. Like filling out a thoughtful intake — not fighting a wizard. Show what sections their input feeds into (subtle, not cluttered).

**Footer/action bar:** Show "16 sections · 12+ agents · ~12-15 min" — then primary CTA "Generate Inception Pack"

---

### 3. Results Page

**Purpose:** Present 16-section inception pack for review, navigation, and export.

**Layout:**
- Left sidebar: Quality score + section navigation organized by category
- Main content: Current section with cards for subsections
- Top bar: Project name, status, share/print/export actions

**Sidebar categories:**
- Overview (1 section)
- Discovery (3 sections)
- Strategy (3 sections)
- Delivery (4 sections)
- Design (2 sections)
- Synthesis (2 sections)
- Quality (1 section)

**Key elements:**
- Quality score prominently displayed (percentage + "Decision-Ready" status)
- Section status indicators (complete/warning)
- Evidence tier legend (E1-E4)
- Cross-reference count per section
- Stakeholder quick-links (tabs for CFO, CTO, Product, Legal views)
- Export functionality

**Design should feel:** Like reviewing a polished strategy document. Content-forward. Clean information hierarchy. Not "AI output viewer."

---

## Design Direction

### Primary References

| Reference | Why |
|-----------|-----|
| [Linear.app](https://linear.app) | Clean hierarchy, subtle gradients, purposeful whitespace |
| [Vercel.com](https://vercel.com) | Typography-forward, minimal decoration, confident restraint |
| [Notion.so](https://notion.so) | Warm neutrals, content-first, readable density |
| [Stripe Dashboard](https://stripe.com) | Professional data presentation, clear information architecture |

### Secondary References

| Reference | Why |
|-----------|-----|
| Claude.ai | Warm, approachable tone |
| Raycast.com | Keyboard-first feel, developer credibility |

---

## What to Avoid

- Generic hero icons (the lightbulb, the rocket, the handshake)
- Excessive iconography — use typography and spacing instead
- Gradient overload or "glassmorphism for the sake of it"
- Rounded everything — mix sharp and soft intentionally
- Cookie-cutter SaaS patterns (floating nav, badge pills everywhere)
- Over-styled form fields
- Decorative illustrations
- "AI-generated aesthetic" — no glowing orbs, no particle effects, no excessive visual noise

---

## Design Principles

1. **Content is the interface** — Let the text breathe. No decorative filler.
2. **Confident restraint** — Every element earns its place.
3. **Information hierarchy through typography** — Size, weight, color — not boxes and icons.
4. **Warm professionalism** — Enterprise-grade but not cold. Competent but human.
5. **Purposeful color** — Use color to signal meaning, not decoration.

---

## Specifics

### Typography

| Element | Recommendation |
|---------|----------------|
| Display | Inter, Geist, or SF Pro (tight tracking on headlines) |
| Body | System or Inter (line-height 1.6-1.7) |
| Mono | For data/metrics if needed |

### Color (Minimal Palette)

| Role | Value | Notes |
|------|-------|-------|
| Background | `#FAFAFA` or `#F7F7F5` | Off-white or warm gray |
| Text | `#171717` | Near-black |
| Muted text | `#737373` | Medium gray |
| Accent | `#C2410C` or `#2563EB` | Warm terracotta OR muted blue — pick one |
| Success | `#16A34A` | Muted green |
| Warning | `#CA8A04` | Muted amber |
| Error | `#DC2626` | Muted red |

### Spacing

- Generous padding (24-48px sections)
- Consistent 8px grid
- Let content breathe — no cramming

### Cards/Containers

- Subtle borders: `1px solid rgba(0,0,0,0.06)`
- Minimal or no shadows
- Border radius: `4px` or `8px` max — no rounded-2xl everywhere

### Forms

- Simple inputs with subtle outline or bottom border
- Floating labels or clean stacked labels
- Chip selectors for multi-select (minimal styling)

### Navigation (Results Page)

- Text-based, not icon-heavy
- Current section: weight change or subtle background
- Quality score: simple number, not elaborate gauge/chart

### Buttons

- Primary: Solid fill, single accent color
- Secondary: Outline or ghost
- No gradients unless extremely subtle

---

## Deliverables

1. **Landing page** — Desktop (1440px) + mobile responsive
2. **Input page** — Desktop + responsive
3. **Results page** — Desktop with sidebar navigation
4. **Component specs** if implementing in React/Tailwind

---

## Tone

> Think: "The design a senior PM at Stripe would trust to present to their CFO."
>
> Not: "The design an AI would generate when asked for 'modern SaaS'."

---

*Last updated: February 2026*
