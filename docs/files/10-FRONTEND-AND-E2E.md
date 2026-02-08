# Phase 10: Frontend Revamp + End-to-End Testing

**Goal:** Build the frontend that renders everything beautifully, then run 3 showcase packs to verify quality.

**Dependencies:** Phases 1-9 (full pipeline must work)

---

## 10.1 New Component Structure

```
frontend/src/components/
├── PackViewer/
│   ├── PackViewer.tsx              # Main viewer — tab navigation across sections
│   ├── NarrativeSummary.tsx        # Executive summary (default/landing view)
│   ├── EvidenceBadge.tsx           # E1-E5 coloured badges
│   ├── EvidenceBar.tsx             # Horizontal tier distribution bar
│   ├── ClaimCard.tsx               # Single claim with cross-reference links
│   ├── ClaimGraph.tsx              # Interactive dependency graph (optional)
│   ├── SectionViewer.tsx           # Generic section renderer
│   │
│   ├── sections/
│   │   ├── MarketIntelligence.tsx
│   │   ├── CompetitiveLandscape.tsx
│   │   ├── CustomerPersonas.tsx
│   │   ├── BusinessCase.tsx
│   │   ├── GoToMarket.tsx
│   │   ├── FinancialModel.tsx
│   │   ├── ProductRequirements.tsx
│   │   ├── TechnicalArchitecture.tsx
│   │   ├── RegulatoryCompliance.tsx
│   │   └── RiskAssessment.tsx
│   │
│   ├── design/
│   │   ├── WireframeViewer.tsx     # Renders React code in sandboxed iframe
│   │   ├── PrototypeViewer.tsx     # Interactive prototype in sandboxed iframe
│   │   └── UserFlowDiagram.tsx     # Renders Mermaid flow diagrams
│   │
│   ├── stakeholders/
│   │   ├── StakeholderViewSelector.tsx  # Dropdown/tabs for switching views
│   │   ├── StakeholderView.tsx          # Single stakeholder view renderer
│   │   └── ObjectionCard.tsx            # Anticipated objection with pre-response
│   │
│   └── validation/
│       ├── ValidationPlaybook.tsx       # Validation playbook view
│       └── ExperimentCard.tsx           # Single experiment card
│
└── charts/                         # EXISTING — keep and extend
    ├── CompetitivePositionChart.tsx
    ├── FinancialProjectionChart.tsx  # MODIFY: add scenario lines
    ├── RiskMatrixChart.tsx
    ├── LeanCanvasVisual.tsx
    └── EvidenceDistributionChart.tsx # NEW: donut/bar chart of evidence tiers
```

---

## 10.2 Key Components to Build

### Evidence Badge

```tsx
// EvidenceBadge.tsx
const TIER_CONFIG = {
  E1: { colour: "bg-green-100 text-green-800", label: "Primary Research" },
  E2: { colour: "bg-blue-100 text-blue-800", label: "Verified Source" },
  E3: { colour: "bg-yellow-100 text-yellow-800", label: "Industry Data" },
  E4: { colour: "bg-orange-100 text-orange-800", label: "Hypothesis" },
  E5: { colour: "bg-red-100 text-red-800", label: "Assumption" },
};

function EvidenceBadge({ tier, source, validationMethod }: Props) {
  const config = TIER_CONFIG[tier] || TIER_CONFIG.E4;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.colour}`}
          title={source || validationMethod || config.label}>
      {tier}
      {tier === "E2" && source && (
        <a href={source} target="_blank" className="ml-1 underline">↗</a>
      )}
    </span>
  );
}
```

### Sandboxed Prototype Viewer

```tsx
// PrototypeViewer.tsx
function PrototypeViewer({ reactCode }: { reactCode: string }) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.9/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body { margin: 0; font-family: system-ui, sans-serif; }</style>
      </head>
      <body>
        <div id="root"></div>
        <script type="text/babel">
          ${reactCode}
          const App = typeof exports !== 'undefined' && exports.default
            ? exports.default
            : () => React.createElement('div', null, 'Component not found');
          ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
        </script>
      </body>
      </html>
    `;
    if (iframeRef.current) iframeRef.current.srcdoc = html;
  }, [reactCode]);

  return (
    <div className="rounded-lg overflow-hidden border border-gray-200 shadow-lg">
      <div className="bg-gray-800 text-white px-4 py-2 flex items-center gap-2 text-sm">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
        </div>
        <span className="ml-2">Interactive Prototype</span>
      </div>
      <iframe
        ref={iframeRef}
        className="w-full border-0"
        style={{ height: '600px' }}
        sandbox="allow-scripts"
        title="Product Prototype"
      />
    </div>
  );
}
```

### Stakeholder View Toggle

```tsx
// StakeholderViewSelector.tsx
function StakeholderViewSelector({ views, activeView, onSelect }: Props) {
  return (
    <div className="flex gap-2 p-2 bg-gray-50 rounded-lg">
      <button
        className={activeView === "full" ? "active-styles" : "inactive-styles"}
        onClick={() => onSelect("full")}
      >
        Full Pack
      </button>
      {views.map((v) => (
        <button
          key={v.stakeholder_role}
          className={activeView === v.stakeholder_role ? "active-styles" : "inactive-styles"}
          onClick={() => onSelect(v.stakeholder_role)}
        >
          {v.stakeholder_role}
        </button>
      ))}
    </div>
  );
}
```

---

## 10.3 Key Frontend Features

### Evidence Badges Throughout
Throughout the pack, every evidence-tagged claim shows a coloured badge:
- E1: Green "Primary Research"
- E2: Blue "Verified Source" (clickable → opens source URL in new tab)
- E3: Yellow "Industry Data"
- E4: Orange "Hypothesis" (hover shows validation method)
- E5: Red "Assumption"

### Evidence Distribution Chart (NEW)
Donut chart or horizontal bar showing tier distribution across the pack. Prominently displayed in the executive summary view.

### Wireframe Viewer
Renders wireframe React code in sandboxed iframe. Tabs to switch between screens. Each screen shows which user stories it implements.

### Prototype Viewer
Renders prototype React code in sandboxed iframe. Full interactive experience. Include a "View Code" toggle showing the source.

### Stakeholder View Toggle
Dropdown at the top of the pack: "Full Pack | CFO View | CISO View | Architecture Review | VP Product". Switching views replaces the content with the stakeholder-specific version.

### Mermaid Diagram Rendering
User flow diagrams and ER diagrams use Mermaid. Use a Mermaid rendering library or embed via iframe.

### SSE Event Handling
Update `useSSE.ts` to handle new event types: `WIREFRAME_READY`, `PROTOTYPE_READY`, `DESIGN_PHASE`.

---

## 10.4 Generate 3 Showcase Packs

| # | Product Idea | Industry | Key Sections to Validate |
|---|-------------|----------|------------------------|
| 1 | "AI-powered cash flow forecasting for SME banking — predicts gaps 30-90 days ahead with recommended actions" | Banking/Fintech | Regulatory (APRA), Financial Model, Stakeholder Views (CFO, CISO, ARB) |
| 2 | "AI clinical trial matching platform connecting patients with eligible trials based on medical records and genomics" | Healthcare | Regulatory (HIPAA/TGA), Technical Architecture (data sensitivity), Personas (patients vs researchers) |
| 3 | "Automated insurance claims processing with AI fraud detection — reduces processing from 14 days to 24 hours" | Insurance | Regulatory (APRA/ASIC), Risk Assessment (fraud model risks), Financial Model (claims volume) |

---

## 10.5 Quality Checklist Per Pack

### Evidence & Cross-References
- [ ] Cross-reference index contains 80+ claims
- [ ] Claims span all section prefixes (MI, CL, CP, BC, GM, FM, PR, TA, RC, RM)
- [ ] At least 30% of claims are E2 or E3 (grounded)
- [ ] E4/E5 claims have specific validation methods
- [ ] Cross-references exist between sections (depends_on populated)

### Section Quality
- [ ] Market Intelligence: specific market size numbers with methodology shown
- [ ] Competitive Landscape: real competitor pricing with source URLs
- [ ] Personas: decision-making models with JTBD, not just demographics
- [ ] Business Case: unit economics with step-by-step derivations
- [ ] Business Case: sensitivity analysis with kill conditions
- [ ] GTM: specific tactics with budgets and timelines per phase
- [ ] Financial Model: 12 monthly Year 1 projections
- [ ] Financial Model: numbers consistent with Business Case unit economics
- [ ] PRD: screen references (S1, S2), persona names, edge cases per story
- [ ] Technical Architecture: data model with entities/fields/types
- [ ] Technical Architecture: ER diagram and system diagram (Mermaid)
- [ ] Technical Architecture: API endpoints with request/response shapes
- [ ] Regulatory: specific regulation section/clause numbers cited
- [ ] Risk Assessment: claim_id references and actionable mitigations

### Design
- [ ] 5-8 wireframe screens generated
- [ ] Screens match PRD screen_map IDs
- [ ] React code renders without errors in browser
- [ ] User flows have valid Mermaid diagrams
- [ ] Wireframes use grayscale only
- [ ] Interactive prototype with working navigation (3-5 screens)
- [ ] Prototype uses colour, typography, and realistic data
- [ ] Prototype looks like a real product, not a wireframe

### Synthesis
- [ ] 3-4 stakeholder views for different roles
- [ ] Each view has tailored executive summary
- [ ] Anticipated objections reference specific claim_ids
- [ ] Validation playbook: 5-8 experiments with specific instructions
- [ ] Experiments have success/failure criteria and target profiles
- [ ] Decision framework provides Build/Pivot/Kill signals
- [ ] Executive summary reads as narrative argument, not section summary
- [ ] Executive summary includes BUILD/INVESTIGATE/PIVOT/KILL recommendation
- [ ] Executive summary has evidence score and tier distribution

### Overall Pack Coherence
- [ ] Financial projections reference market intelligence TAM
- [ ] PRD accounts for regulatory requirements
- [ ] Tech architecture supports PRD non-functional requirements
- [ ] Stakeholder views reference actual pack evidence
- [ ] Validation playbook targets the weakest claims in the pack
- [ ] No section contradicts another section

---

## 10.6 Fix-and-Iterate

After running the 3 showcase packs:
1. Identify which quality checklist items fail
2. Trace failures to the specific agent prompt or schema
3. Fix the prompt/schema and re-run
4. Repeat until all 3 packs pass the checklist

Common issues to watch for:
- Generic output → prompt needs more specific anti-pattern examples
- Missing evidence tiers → prompt's evidence tier section needs strengthening
- Inconsistent numbers across sections → context builder may be truncating too aggressively
- Prototype rendering failures → check Tailwind class usage and React component exports
