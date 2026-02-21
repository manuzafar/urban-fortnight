# Seedcraft Landing Page - Design Specification v2

## Modern, Light Mode Aesthetic | Inspired by Tako.com

---

## 1. Design Philosophy

**Core Principles:**
- **Clean & airy** - Light backgrounds, generous whitespace
- **Professional trust** - Subtle, sophisticated, not flashy
- **Data-forward** - Show credibility through structure
- **Calm confidence** - Premium without being intimidating

**Mood:** Professional, trustworthy, intelligent, approachable

---

## 2. Color Palette (Light Mode)

```
┌─────────────────────────────────────────────────────────┐
│  LIGHT MODE                                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Background         #FFFFFF    ████  Pure white         │
│  Background Alt     #F8FAFC    ████  Subtle gray        │
│  Surface            #FFFFFF    ████  Cards              │
│  Surface Elevated   #F1F5F9    ████  Hover states       │
│                                                         │
│  Primary            #0D9488    ████  Teal (trust)       │
│  Primary Dark       #0F766E    ████  Teal hover         │
│  Primary Light      #CCFBF1    ████  Teal backgrounds   │
│                                                         │
│  Accent             #D97706    ████  Amber (warmth)     │
│  Accent Light       #FEF3C7    ████  Amber backgrounds  │
│                                                         │
│  Text Primary       #0F172A    ████  Headings (slate)   │
│  Text Secondary     #475569    ████  Body text          │
│  Text Muted         #94A3B8    ████  Captions           │
│                                                         │
│  Border             #E2E8F0    ████  Card borders       │
│  Border Dark        #CBD5E1    ████  Hover borders      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Semantic Colors
```
Success     #10B981    (emerald)
Warning     #F59E0B    (amber)
Error       #EF4444    (red)
Info        #3B82F6    (blue)
```

---

## 3. Typography

### Font Stack
```css
--font-display: 'Space Grotesk', system-ui, sans-serif;
--font-body: 'Inter', system-ui, sans-serif;
```

### Type Scale
```
Hero Title        48px / 56px    Space Grotesk 600
Section Title     32px / 40px    Space Grotesk 600
Card Title        20px / 28px    Space Grotesk 500
Body Large        18px / 28px    Inter 400
Body              16px / 24px    Inter 400
Caption           14px / 20px    Inter 500
Eyebrow           12px / 16px    Inter 600, uppercase, tracking wide
```

---

## 4. Revised Copy (Product-Relevant)

### Hero Section

**Eyebrow Badge:**
```
● 3 Agent Swarms • 12+ Specialists • Working Now
```

**Headline:**
```
The inception layer
for modern product teams
```

**Subheadline:**
```
Swarms of AI agents research, strategize, and document in parallel —
then critique each other's work before you see it.
From idea to decision-ready pack in minutes.
```

**Primary CTA:** `Generate Inception Pack`
**Secondary CTA:** `See sample output`

**Metrics Row:**
```
12+ Agents        3 Swarms          7 Deliverables       AI Critique
Discovery,        Working in        Complete pack        Every section
Strategy &        parallel          ready for            cross-validated
Delivery                            stakeholders         before delivery
```

---

### Social Proof Bar (Optional)
```
"Three swarms of agents replaced our entire discovery phase.
Now I just validate with customers." — Product Lead
```

---

### Deliverables Section

**Eyebrow:** `WHAT YOU GET`

**Headline:**
```
A complete inception pack,
ready for stakeholder review
```

**Subheadline:**
```
Three agent swarms — Discovery, Strategy, and Delivery — work in parallel.
A critique agent cross-validates everything before it reaches you.
```

**Cards:**

| # | Title | Description |
|---|-------|-------------|
| 01 | **Executive Summary** | The TL;DR for leadership. Problem statement, solution overview, key risks, and recommended next steps — everything needed to greenlight or pivot. |
| 02 | **Market Hypotheses** | AI-generated hypotheses about your market, customers, and competitors. Tiered by confidence (E1-E5) so you know what to validate first. |
| 03 | **Business Strategy** | Lean Canvas, revenue model, go-to-market approach, and financial projections. Built on market research, not guesswork. |
| 04 | **Product Requirements** | Epics, user stories, and acceptance criteria structured for engineering handoff. Automatically critiqued for completeness. |
| 05 | **Technical Architecture** | System design, tech stack recommendations, and infrastructure considerations. Includes architecture diagrams. |
| 06 | **Legal & Compliance** | Regulatory requirements, data protection obligations, and legal risks specific to your industry and geography. |
| 07 | **Quality Assessment** | Cross-validation across all sections. Gaps, contradictions, and risks surfaced before you review — not after. |

---

### How It Works Section

**Eyebrow:** `HOW IT WORKS`

**Headline:**
```
Three steps to clarity
```

**Steps:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   1. Describe   │───▶│   2. Swarm      │───▶│   3. Review     │
│                 │    │                 │    │                 │
│   Enter your    │    │   3 agent       │    │   Get a scored, │
│   product idea  │    │   swarms work   │    │   critiqued     │
│   and context   │    │   in parallel   │    │   inception     │
│                 │    │                 │    │   pack          │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

### Final CTA Section

**Headline:**
```
Stop researching. Start validating.
```

**Subheadline:**
```
Get your inception pack in minutes, then spend your time
where it matters — talking to real customers.
```

**CTA Button:** `Generate Your Pack — Free`

**Trust line:**
```
✓ No signup required  ✓ No credit card  ✓ Results in under 12 minutes
```

---

## 5. Component Designs (Light Mode)

### 5.1 Primary Button
```
Background: #0D9488 (teal-600)
Text: #FFFFFF
Padding: 14px 28px
Border-radius: 10px
Font: Space Grotesk 500, 16px
Shadow: 0 1px 2px rgba(0,0,0,0.05)

Hover:
  background: #0F766E (teal-700)
  shadow: 0 4px 12px rgba(13,148,136,0.25)
  transform: translateY(-1px)
```

### 5.2 Secondary Button
```
Background: transparent
Border: 1px solid #E2E8F0
Text: #475569
Padding: 14px 28px
Border-radius: 10px

Hover:
  border-color: #0D9488
  text-color: #0D9488
```

### 5.3 Feature Card
```
Background: #FFFFFF
Border: 1px solid #E2E8F0
Border-radius: 16px
Padding: 28px
Shadow: 0 1px 3px rgba(0,0,0,0.04)

Icon container:
  48x48px
  background: #CCFBF1 (teal-100)
  border-radius: 12px
  color: #0D9488

Number: Inter 600, 14px, #94A3B8
Title: Space Grotesk 500, 20px, #0F172A
Description: Inter 400, 15px, #475569, line-height 1.6

Hover:
  border-color: #0D9488
  shadow: 0 8px 24px rgba(0,0,0,0.08)
  transform: translateY(-2px)
```

### 5.4 Trust Badge (Hero)
```
"● 3 Agent Swarms • 12+ Specialists • Working Now"

Background: #F8FAFC
Border: 1px solid #E2E8F0
Border-radius: 100px (pill)
Padding: 8px 16px
Font: Inter 500, 14px, #475569

Dot: #10B981 (emerald-500)
     Pulse animation
```

### 5.5 Metric Display
```
Number: Space Grotesk 600, 28px, #0F172A
Label: Inter 500, 13px, #94A3B8
       text-transform: uppercase
       letter-spacing: 0.04em
Sublabel: Inter 400, 14px, #64748B
```

---

## 6. Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  NAVBAR ─────────────────────────────────────────────────────── │
│                                                                 │
│  ◆ Seedcraft                                    [Generate Pack] │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HERO (bg: white) ──────────────────────────────────────────── │
│                          padding: 96px 0                        │
│                                                                 │
│              ╭────────────────────────────────────────╮         │
│              │ ● 3 Agent Swarms • 12+ Specialists     │         │
│              ╰────────────────────────────────────────╯         │
│                                                                 │
│                       The inception layer                       │
│                   for modern product teams                      │
│                                                                 │
│          Swarms of AI agents research, strategize, and          │
│           document in parallel — then critique each             │
│           other's work before you see it.                       │
│                                                                 │
│            ╭──────────────────────╮  ╭─────────────────╮        │
│            │ Generate Inception   │  │ See sample      │        │
│            │ Pack                 │  │ output          │        │
│            ╰──────────────────────╯  ╰─────────────────╯        │
│                                                                 │
│         ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │
│         │  12+   │  │   3    │  │   7    │  │   AI   │         │
│         │ Agents │  │ Swarms │  │ Docs   │  │Critique│         │
│         └────────┘  └────────┘  └────────┘  └────────┘         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DELIVERABLES (bg: #F8FAFC) ─────────────────────────────────── │
│                          padding: 80px 0                        │
│                                                                 │
│                        WHAT YOU GET                             │
│                                                                 │
│                   A complete inception pack,                    │
│                   ready for stakeholder review                  │
│                                                                 │
│     ┌──────────┐   ┌──────────┐   ┌──────────┐                 │
│     │ 01       │   │ 02       │   │ 03       │                 │
│     │ Exec     │   │ Market   │   │ Business │                 │
│     │ Summary  │   │ Hypothes.│   │ Strategy │                 │
│     └──────────┘   └──────────┘   └──────────┘                 │
│                                                                 │
│     ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│     │ 04       │   │ 05       │   │ 06       │   │ 07       │  │
│     │ PRD      │   │ Tech     │   │ Legal    │   │ Quality  │  │
│     │          │   │ Arch     │   │          │   │ Check    │  │
│     └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HOW IT WORKS (bg: white) ────────────────────────────────────  │
│                          padding: 80px 0                        │
│                                                                 │
│                       HOW IT WORKS                              │
│                    Three steps to clarity                       │
│                                                                 │
│       ┌─────────┐      ┌─────────┐      ┌─────────┐            │
│       │    1    │ ───▶ │    2    │ ───▶ │    3    │            │
│       │Describe │      │  Swarm  │      │ Review  │            │
│       └─────────┘      └─────────┘      └─────────┘            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FINAL CTA (bg: #F8FAFC) ─────────────────────────────────────  │
│                          padding: 80px 0                        │
│                                                                 │
│     ┌─────────────────────────────────────────────────────┐     │
│     │                                                     │     │
│     │          Stop researching. Start validating.        │     │
│     │                                                     │     │
│     │        Get your inception pack in minutes, then     │     │
│     │        spend your time talking to real customers.   │     │
│     │                                                     │     │
│     │           ╭─────────────────────────────╮           │     │
│     │           │  Generate Your Pack — Free  │           │     │
│     │           ╰─────────────────────────────╯           │     │
│     │                                                     │     │
│     │     ✓ No signup   ✓ No card   ✓ Under 12 min       │     │
│     │                                                     │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FOOTER ─────────────────────────────────────────────────────── │
│                                                                 │
│  © 2026 Seedcraft                            GitHub · Twitter   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Animations

### Page Load (Staggered Fade-In)
```
Hero badge:      0ms delay,   400ms duration
Hero title:      100ms delay, 400ms duration
Hero subtitle:   200ms delay, 400ms duration
Hero buttons:    300ms delay, 400ms duration
Hero metrics:    400ms delay, 400ms duration

Animation: opacity 0→1, translateY 16px→0
Easing: cubic-bezier(0.16, 1, 0.3, 1)
```

### Scroll Animations
```
Sections fade in when 15% visible
Cards stagger with 80ms delay between each
```

### Hover States
```
Buttons: translateY(-1px), deeper shadow
Cards: translateY(-2px), border color, shadow
Duration: 200ms ease-out
```

### Badge Pulse
```
Dot scales 1 → 1.4 → 1, opacity 1 → 0.6 → 1
Duration: 2s infinite
```

---

## 8. CSS Variables

```css
:root {
  /* Colors - Light Mode */
  --color-bg: #FFFFFF;
  --color-bg-alt: #F8FAFC;
  --color-surface: #FFFFFF;
  --color-primary: #0D9488;
  --color-primary-dark: #0F766E;
  --color-primary-light: #CCFBF1;
  --color-accent: #D97706;
  --color-text: #0F172A;
  --color-text-secondary: #475569;
  --color-text-muted: #94A3B8;
  --color-border: #E2E8F0;
  --color-border-dark: #CBD5E1;

  /* Typography */
  --font-display: 'Space Grotesk', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;
  --space-4xl: 96px;

  /* Radii */
  --radius-sm: 8px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 100px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.08);
}
```

---

## 9. Approval Checklist

- [ ] Light mode color palette feels clean and professional
- [ ] Teal primary color conveys trust
- [ ] Copy accurately describes the product
- [ ] Deliverable descriptions are clear
- [ ] "How it works" flow makes sense
- [ ] CTA copy is compelling
- [ ] Overall layout flows well

**Questions:**
1. Happy with "Generate Inception Pack" as primary CTA?
2. Want to include the "How it Works" section, or keep it shorter?
3. Any deliverables to rename or re-describe?
4. Should we add a sample output preview/screenshot?

---

*Ready to implement once approved!*
