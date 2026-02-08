# Seedcraft Design Mockups

Version-controlled HTML mockups for the Seedcraft landing page and app UI.

## Versions

| Version | File | Date | Description |
|---------|------|------|-------------|
| v1 | `v1-enterprise-professional.html` | 2024-02-06 | Enterprise aesthetic with warm neutrals, tabbed navigation (Landing/Execution/Pack Viewer), Superagent-inspired three-panel execution view |
| v2 | `v2-single-page-scroll.html` | 2024-02-06 | Warp-inspired single-page scroll, inline pack preview, conversion-focused with stats and social proof |
| v3 | `v3-full-pack-preview.html` | 2024-02-06 | Full pack preview with all 7 sections, PDF/DOCX download buttons per section, professional blue accent (#2563eb) |
| v4 | `v4-stripe-inspired.html` | 2024-02-06 | Dark mode Stripe-inspired design with gradient accents, AI agents visualization |
| v5 | `v5-superagent-style.html` | 2026-02-06 | Superagent-inspired warm cream aesthetic, output-focused gallery |
| v6 | `v6-landing-page.html` | 2026-02-06 | Superagent-style: persona filters, live demo cards, evidence tiers, discover gallery |
| v7 | `v7-outcome-hero.html` | 2026-02-06 | **Current** - Outcome-focused hero showing what you get, not just brand. Dark hero with live output preview, prompt input, evidence-tiered examples. Designed for AI-native users. |

## How to View

```bash
# Open specific version
open frontend/mockups/v1-enterprise-professional.html
open frontend/mockups/v2-single-page-scroll.html
open frontend/mockups/v3-full-pack-preview.html
```

## Design Decisions

### v1 - Enterprise Professional
- Inspired by: Stripe, Palantir, Superagent
- Three-panel execution view showing agents working
- Separate Pack Viewer tab
- Warm neutral palette (#faf9f7)
- Professional blue accent (#2563eb)

### v2 - Single Page Scroll
- Inspired by: Warp (joinwarp.com)
- Progressive reveal as you scroll
- Inline output preview (no separate tabs)
- Stats/metrics section for social proof
- Problem → Solution narrative
- Multiple CTA touchpoints throughout
- Emerald green accent (#10b981)

### v3 - Full Pack Preview
- Inspired by: Superagent + Warp
- Professional blue accent (#2563eb)
- All 7 sections displayed with full content preview
- PDF/DOCX download buttons for each section
- Left navigation with quality indicators

### v4 - Stripe/Superagent Inspired
- **Dark mode** with vibrant gradient accents (purple → pink)
- **AI Agents visualization** - Shows 6 agents working in parallel
- **Gradient mesh backgrounds** - Stripe-style radial gradients
- **Pack preview** with circular score ring, left nav, export footer

### v5 - Superagent Style
- Warm cream aesthetic (#faf8f5)
- Output-focused gallery with pack content previews
- Evidence tier tags (E1-E4)

### v6 - Full Superagent Journey (Current)
Based on complete Superagent customer journey analysis:

**Hero Section:**
- Giant "Seedcraft" wordmark (like Superagent)
- **Persona filters**: PMs, Founders, Innovation Teams, Consultants
- Establishes "this is for people like me"

**Live Demo Cards:**
- Three colored cards showing agents actively working
- Real-time status: "Generating pack...", "Analyzing market...", "Scanning regulations..."
- Agent progress visible: Research ✓, Business ✓, Tech Working..., Legal Pending
- "Try it out →" CTA on each card

**Value Proposition:**
- Headline: "Know what to validate. Before your first call."
- Three feature cards:
  1. **Six specialist agents** - Research, Business, Product, Tech, Legal, Quality
  2. **Evidence-tiered insights** - E1 (validated) to E4 (speculation)
  3. **360° view** - Customers, Market, Legal, Tech dimensions

**Discover Gallery:**
- Output type filters: Full Pack, Research Focus, Compliance Check, Tech Assessment
- Pack cards showing:
  - Hero section with title, subtitle, key metrics (TAM, Pack Score, Hypotheses)
  - Content preview with Key Pain Point + Evidence tier
  - Regulatory summary
  - Original prompt that generated it

**Footer:**
- Giant "Seedcraft" wordmark
- Tagline: "Know what to validate."

**Key patterns from Superagent:**
- Show output, don't just describe it
- Persona-based filtering
- Live agent activity in hero
- Evidence/sources build trust
- Prompts visible below outputs

### v7 - Outcome-Focused Hero (Current)
Designed for AI-native users who want to see what they get:

**Hero - The Transformation:**
- Dark background for premium feel
- Split layout: value prop left, output preview right
- Headline: "Your product idea, mapped in minutes."
- Eyebrow: "6 AI agents working in parallel"
- Stats: 7 sections, ~8 min, E1-E4 evidence tiers
- **Live output preview** showing a complete inception pack:
  - Pack summary card (title, TAM, score, hypotheses)
  - Section cards with evidence dots (Customer Research, Business Case, Legal, Tech)
  - Floating elements showing agent completing + E1 insight
- CTA: "Start mapping your idea"

**Prompt Section:**
- Embedded in dark section below hero
- Large textarea with placeholder example
- Pack type options: Full Pack, Research Focus, Compliance Check
- "Generate Pack →" button

**How It Works:**
- 3-step flow: Describe → Agents work → Get roadmap
- Each step has visual: prompt example, agent grid, evidence tier list
- Clean, educational

**Discover Gallery:**
- Industry filters: All, B2B SaaS, Healthcare, Fintech
- Pack cards showing:
  - Colored hero with title, TAM, score
  - Key insight with evidence badge
  - Section tags
  - Original prompt in footer

**Footer:**
- Dark background matching hero
- Tagline: "Turn product ideas into discovery roadmaps"
- Link columns: Product, Company, Legal
- Social links

**Design principles:**
- Show the output, not just the brand
- Evidence tiers visible everywhere (builds trust)
- AI-native: assumes user understands AI tools
- Outcome-first: "what do I get?" answered immediately
