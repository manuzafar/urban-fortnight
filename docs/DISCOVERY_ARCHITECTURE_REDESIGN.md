# Discovery Architecture Redesign Proposal

## Executive Summary

This document proposes a fundamental redesign of LifeCycle's discovery architecture based on:
1. **Wisdom from 8 world-class PMs** (Teresa Torres, Bob Moesta, Uri Levine, etc.)
2. **Stage-by-stage execution** with user control at each checkpoint
3. **AI-as-coach** paradigm vs AI-as-generator

---

## Current State Analysis

### What We Have Today

```
┌─────────────────────────────────────────────────────────────────┐
│                 CURRENT PIPELINE (v3.0)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Input ──→ [Planning] ──→ [Discovery] ──→ [Strategy] ──→  │
│                     ↓              ↓              ↓             │
│              (auto-runs)    (auto-runs)    (auto-runs)          │
│                     ↓              ↓              ↓             │
│              [Delivery] ──→ [Design] ──→ [Quality] ──→ [Synth] │
│                     ↓              ↓              ↓        ↓    │
│              (auto-runs)    (auto-runs)    (auto-runs)  OUTPUT  │
│                                                                 │
│  User waits ~10-15 minutes for complete pack                   │
│  No checkpoints, no editing between stages                     │
│  AI generates everything, PM receives outputs                  │
└─────────────────────────────────────────────────────────────────┘
```

### Current Discovery Phase Limitations

| Issue | Impact |
|-------|--------|
| **No real customer data** | All "research" is AI hypothesis (E4 tier) |
| **No user control** | Can't edit outputs between stages |
| **AI generates personas** | Not validated against real users |
| **Competitive analysis** | Snapshot in time, no user verification |
| **No interview integration** | PM's actual research isn't incorporated |
| **Monolithic execution** | Must run entire pipeline or nothing |

---

## Proposed Architecture

### Philosophy Shift

| FROM | TO |
|------|-----|
| AI generates everything | AI guides PM through frameworks |
| PM receives outputs | PM creates outputs with AI coaching |
| Monolithic pipeline | Stage-by-stage with checkpoints |
| One-shot execution | Iterative with user control |
| Fake customer research | Real interview integration |

### New Discovery Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              NEW STAGE-BASED DISCOVERY (v4.0)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ STAGE 1          │                                          │
│  │ Problem Love     │ ←── User validates problem               │
│  │ (Uri Levine)     │     AI coaches, asks hard questions      │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ CHECKPOINT 1     │ ←── User reviews & edits                 │
│  │ [Edit] [Approve] │     Can proceed or iterate               │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ STAGE 2          │                                          │
│  │ Customer Truth   │ ←── User inputs interview data           │
│  │ (Teresa Torres)  │     AI synthesizes & identifies patterns │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ CHECKPOINT 2     │ ←── User reviews synthesized insights    │
│  │ [Edit] [Approve] │     Can add more interviews              │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ STAGE 3          │                                          │
│  │ Opportunity Map  │ ←── AI + User build OST together         │
│  │ (Bob Moesta)     │     4 Forces mapping from real data      │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ CHECKPOINT 3     │ ←── User reviews opportunity tree        │
│  │ [Edit] [Approve] │     Can restructure priorities           │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ STAGE 4          │                                          │
│  │ Solution Design  │ ←── DHM scoring, Pre-mortems             │
│  │ (Gibson Biddle)  │     AI facilitates, user decides         │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ CHECKPOINT 4     │ ←── User reviews solution approach       │
│  │ [Edit] [Approve] │     Can modify DHM scores                │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ STAGE 5          │                                          │
│  │ Validation Plan  │ ←── Validation ladder, experiment design │
│  │ (Uri + Dalton)   │     AI suggests, user customizes         │
│  └────────┬─────────┘                                          │
│           ↓                                                     │
│  ┌──────────────────┐                                          │
│  │ DISCOVERY        │                                          │
│  │ COMPLETE         │ ←── Ready for Strategy phase             │
│  │ [View Pack]      │     (or continue to full lifecycle)      │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Stage Specifications

### STAGE 1: Problem Love

**Source:** Uri Levine (Waze founder)

**Purpose:** Validate the problem is worth solving before any research

**User Experience:**
```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: PROBLEM LOVE                                           │
│ "Fall in love with the problem, not the solution" - Uri Levine  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. PROBLEM STATEMENT                                            │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ What problem are you solving?                           │ │
│    │ [____________________________________________________] │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    AI COACHING:                                                │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ 💡 "Your problem statement is broad. Uri Levine says:   │ │
│    │    'A problem that is everyone's problem is no one's    │ │
│    │    problem.' Can you narrow to a specific struggling    │ │
│    │    moment?"                                             │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 2. REAL PEOPLE CHECK                                           │
│    Can you name 5 people who have this problem RIGHT NOW?      │
│                                                                 │
│    [ ] Person 1: [Name] - [Their struggling moment]            │
│    [ ] Person 2: [Name] - [Their struggling moment]            │
│    [ ] Person 3: [Name] - [Their struggling moment]            │
│    [ ] Person 4: [Name] - [Their struggling moment]            │
│    [ ] Person 5: [Name] - [Their struggling moment]            │
│                                                                 │
│    ⚠️  3/5 complete - AI will warn if <5                       │
│                                                                 │
│ 3. FREQUENCY CHECK                                             │
│    How often do people encounter this problem?                 │
│                                                                 │
│    (●) Daily      - "This could be huge"                       │
│    ( ) Weekly     - "Strong potential"                         │
│    ( ) Monthly    - "Needs 10X solution"                       │
│    ( ) Rarely     - "Red flag: harder to build habit"          │
│                                                                 │
│ 4. CURRENT ALTERNATIVES                                        │
│    What do people do TODAY to solve this?                      │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ [____________________________________________________] │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    AI COACHING:                                                │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ 💡 "If nothing exists today, that's a warning sign.     │ │
│    │    Uri Levine: 'If no one else has tried to solve it,   │ │
│    │    maybe it's not a real problem.'"                     │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 5. TARPIT CHECK (Dalton Caldwell)                              │
│    AI analyzes for common tarpit patterns...                   │
│                                                                 │
│    ⚠️  TARPIT WARNING: Your idea has similarities to          │
│    "social coordination apps" - a known tarpit where many      │
│    startups have failed despite positive feedback.             │
│                                                                 │
│    What do YOU know that all those failed startups didn't?     │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ [____________________________________________________] │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ────────────────────────────────────────────────────────────── │
│ PROBLEM LOVE SCORE: 7/10                                       │
│                                                                 │
│ [Save Draft]  [← Back]  [Proceed to Stage 2 →]                │
└─────────────────────────────────────────────────────────────────┘
```

**Backend Changes:**

```python
# New file: backend/agents/discovery_v4/problem_love.py

class ProblemLoveStage:
    """
    Stage 1: Validate problem worth solving
    Based on Uri Levine's frameworks
    """

    async def run(self, state: DiscoveryState) -> StageOutput:
        """
        Run problem love stage with AI coaching.
        Returns coaching prompts and validation checks.
        """

    async def validate_problem_statement(self, statement: str) -> CoachingResponse:
        """
        AI analyzes problem statement and provides coaching.
        Checks for: specificity, struggling moment, measurability
        """

    async def check_tarpit(self, problem: str) -> TarpitAnalysis:
        """
        Check against known tarpit patterns (Dalton Caldwell).
        Returns similarity score and specific concerns.
        """

    async def score_problem_love(self, inputs: ProblemLoveInputs) -> int:
        """
        Score 1-10 based on:
        - Problem specificity
        - Real people identified
        - Frequency of problem
        - Existing alternatives
        - Tarpit risk
        """
```

**New Schema:**

```python
# backend/models/discovery_v4_schemas.py

class ProblemLoveOutput(BaseModel):
    """Output from Stage 1: Problem Love"""

    problem_statement: str
    problem_specificity_score: int  # 1-10

    real_people: List[RealPersonWithProblem]
    real_people_count: int  # Target: 5

    frequency: Literal["daily", "weekly", "monthly", "rarely"]
    frequency_analysis: str

    current_alternatives: List[str]
    alternatives_analysis: str

    tarpit_check: TarpitAnalysis

    overall_score: int  # 1-10
    ai_coaching_notes: List[str]
    proceed_recommendation: bool

    # User can override AI recommendation
    user_override: Optional[str] = None

class RealPersonWithProblem(BaseModel):
    name: str
    struggling_moment: str
    how_you_know_them: Optional[str] = None

class TarpitAnalysis(BaseModel):
    is_tarpit: bool
    similarity_to_known_tarpits: float  # 0-1
    specific_concerns: List[str]
    user_differentiation: Optional[str] = None  # What they know others don't
```

---

### STAGE 2: Customer Truth

**Source:** Teresa Torres (Continuous Discovery Habits)

**Purpose:** Integrate REAL customer interviews, not AI-generated personas

**User Experience:**
```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: CUSTOMER TRUTH                                         │
│ "Interview for stories, not answers" - Teresa Torres            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ INTERVIEW TRACKER                          Goal: 5 this week   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ ●●●○○  3 of 5 interviews completed                             │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ INTERVIEW 1: Sarah, PM @ Series B startup    Feb 18, 2026 │  │
│ │ ─────────────────────────────────────────────────────────│  │
│ │ KEY STORY:                                                │  │
│ │ "Last week I spent 4 hours trying to find competitor      │  │
│ │ pricing. I had a board meeting and needed to justify our  │  │
│ │ pricing strategy. I ended up cobbling together data from  │  │
│ │ 12 different sources..."                                  │  │
│ │                                                           │  │
│ │ STRUGGLING MOMENT: Preparing for board meetings           │  │
│ │ EMOTIONAL STATE: Frustrated, anxious about looking bad    │  │
│ │ CURRENT WORKAROUND: Manual Google searches, spreadsheets  │  │
│ │                                                           │  │
│ │ [Edit Interview] [Delete]                                 │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ [+ Add Interview]  [Import from Notes]  [Interview Guide]      │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ AI SYNTHESIS (from your interviews)                            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ PATTERNS DETECTED:                                             │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 🔥 PAIN PATTERN 1 (3/3 interviews)                        │  │
│ │    "Time wasted on manual competitive research"           │  │
│ │    Evidence: E1 (direct quotes from Sarah, Mike, Priya)   │  │
│ │                                                           │  │
│ │ 🔥 PAIN PATTERN 2 (2/3 interviews)                        │  │
│ │    "Anxiety about presenting incomplete data"             │  │
│ │    Evidence: E1 (direct quotes from Sarah, Mike)          │  │
│ │                                                           │  │
│ │ 📊 TRIGGER SITUATION (2/3 interviews)                     │  │
│ │    "Preparing for board meetings or investor updates"     │  │
│ │                                                           │  │
│ │ 🎯 DESIRED OUTCOME                                        │  │
│ │    "Look prepared and data-driven to stakeholders"        │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ AI COACHING:                                                   │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 💡 "You have 3 interviews - great start! Teresa Torres    │  │
│ │    recommends weekly interviews. To strengthen your       │  │
│ │    evidence, try to interview:                            │  │
│ │    • Someone who DOESN'T have this problem (anti-persona) │  │
│ │    • Someone who tried a competitor solution              │  │
│ │    • Someone in a different company size"                 │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ [Save Draft]  [← Back to Stage 1]  [Proceed to Stage 3 →]     │
└─────────────────────────────────────────────────────────────────┘
```

**Interview Input Form:**
```
┌─────────────────────────────────────────────────────────────────┐
│ ADD INTERVIEW                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ INTERVIEWEE                                                     │
│ Name: [________________]  Role: [____________________]          │
│ Company Type: [Startup ▼]  Company Size: [11-50 ▼]             │
│ Date: [Feb 20, 2026]                                           │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ THE STORY (Teresa Torres: "Tell me about the last time...")    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ What specific situation did they describe?                     │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ [Paste or type the story they told you...]                 ││
│ │                                                             ││
│ │                                                             ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ KEY QUOTE (their exact words):                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ "[                                                        ]"││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ANALYSIS (you fill in)                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ What was their STRUGGLING MOMENT?                              │
│ [___________________________________________________________]  │
│                                                                 │
│ What EMOTION did they express?                                 │
│ [ ] Frustrated  [ ] Anxious  [ ] Overwhelmed  [ ] Embarrassed  │
│ [ ] Confused    [ ] Angry    [ ] Resigned     [ ] Other: [___] │
│                                                                 │
│ What do they do TODAY to solve this?                           │
│ [___________________________________________________________]  │
│                                                                 │
│ What would "success" look like for them?                       │
│ [___________________________________________________________]  │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ [Cancel]  [Save Interview]                                     │
└─────────────────────────────────────────────────────────────────┘
```

**Backend Changes:**

```python
# New file: backend/agents/discovery_v4/customer_truth.py

class CustomerTruthStage:
    """
    Stage 2: Synthesize real customer interviews
    Based on Teresa Torres's Continuous Discovery methodology
    """

    async def add_interview(self, interview: InterviewInput) -> Interview:
        """Store a new interview from user input."""

    async def synthesize_patterns(self, interviews: List[Interview]) -> PatternSynthesis:
        """
        AI analyzes interviews to find patterns.
        Returns patterns with E1 evidence (direct quotes).
        """

    async def identify_gaps(self, interviews: List[Interview]) -> List[InterviewGap]:
        """
        Identify what's missing:
        - Persona types not interviewed
        - Questions not explored
        - Contradictions to investigate
        """

    async def generate_interview_guide(self, context: StageContext) -> InterviewGuide:
        """
        Generate Teresa Torres-style interview guide.
        "Tell me about the last time..." questions
        """

    async def validate_readiness(self, state: DiscoveryState) -> ReadinessCheck:
        """
        Check if enough interviews to proceed.
        Minimum: 5 interviews recommended
        """
```

**New Schema:**

```python
class Interview(BaseModel):
    """A real customer interview"""
    id: str
    interviewee_name: str
    interviewee_role: str
    company_type: str
    company_size: str
    interview_date: date

    # The story (Teresa Torres method)
    story_raw: str  # User's notes
    key_quote: str  # Exact words

    # User analysis
    struggling_moment: str
    emotions: List[str]
    current_workaround: str
    desired_outcome: str

    # AI-extracted
    ai_extracted_pain_points: List[str]
    ai_extracted_triggers: List[str]
    ai_extracted_goals: List[str]

    evidence_tier: Literal["E1"] = "E1"  # Direct evidence

class PatternSynthesis(BaseModel):
    """AI synthesis of interview patterns"""
    pain_patterns: List[PainPattern]
    trigger_patterns: List[TriggerPattern]
    outcome_patterns: List[OutcomePattern]
    contradictions: List[Contradiction]
    interview_gaps: List[InterviewGap]

class PainPattern(BaseModel):
    description: str
    frequency: int  # How many interviews mentioned this
    evidence: List[InterviewEvidence]  # Direct quotes
    severity: Literal["critical", "high", "medium", "low"]
```

---

### STAGE 3: Opportunity Mapping

**Source:** Bob Moesta (JTBD), Teresa Torres (OST)

**Purpose:** Map the opportunity space from real data

**User Experience:**
```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: OPPORTUNITY MAPPING                                    │
│ "Struggling moments cause demand" - Bob Moesta                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ 4 FORCES MODEL (from your interviews)                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│   FORCES FOR CHANGE              FORCES AGAINST CHANGE          │
│   ─────────────────              ─────────────────────          │
│                                                                 │
│   F1: PUSH (Problems)            F3: ANXIETY (Fears)            │
│   ┌─────────────────┐            ┌─────────────────┐           │
│   │ • 4hrs wasted   │            │ • "AI might be  │           │
│   │   on research   │  ────────→ │   inaccurate"   │           │
│   │ • Look unprepared│           │ • "Learning     │           │
│   │   to board      │            │   curve"        │           │
│   │ [+ Add Push]    │            │ [+ Add Anxiety] │           │
│   └─────────────────┘            └─────────────────┘           │
│                                                                 │
│   F2: PULL (Attractions)         F4: HABIT (Comfort)            │
│   ┌─────────────────┐            ┌─────────────────┐           │
│   │ • Instant       │            │ • "I know how   │           │
│   │   answers       │  ────────→ │   to Google"    │           │
│   │ • Look smart    │            │ • "Spreadsheets │           │
│   │   in meetings   │            │   work ok"      │           │
│   │ [+ Add Pull]    │            │ [+ Add Habit]   │           │
│   └─────────────────┘            └─────────────────┘           │
│                                                                 │
│   FORCE BALANCE: Push + Pull (8) vs Anxiety + Habit (5)        │
│   ✅ Change likely - forces favor adoption                     │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ OPPORTUNITY SOLUTION TREE (Teresa Torres)                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│                    🎯 OUTCOME                                   │
│            "PMs make data-driven decisions faster"              │
│                          │                                      │
│          ┌───────────────┼───────────────┐                     │
│          │               │               │                     │
│     OPPORTUNITY 1   OPPORTUNITY 2   OPPORTUNITY 3              │
│     ┌───────────┐   ┌───────────┐   ┌───────────┐             │
│     │ Time spent │   │ Data is   │   │ Can't     │             │
│     │ finding    │   │ scattered │   │ compare   │             │
│     │ competitor │   │ across    │   │ apples to │             │
│     │ data       │   │ sources   │   │ apples    │             │
│     │ (5 stories)│   │ (3 stories)│  │ (2 stories)│            │
│     └─────┬─────┘   └─────┬─────┘   └─────┬─────┘             │
│           │               │               │                     │
│     ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐             │
│     │Solutions  │   │Solutions  │   │Solutions  │             │
│     │• Auto-scrape│ │• Central  │   │• Standard │             │
│     │• Alerts   │   │  dashboard│   │  framework│             │
│     │• Templates│   │• Import   │   │• Scoring  │             │
│     └───────────┘   └───────────┘   └───────────┘             │
│                                                                 │
│ [Edit Tree]  [Add Opportunity]  [Add Solution]                 │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ [Save Draft]  [← Back to Stage 2]  [Proceed to Stage 4 →]     │
└─────────────────────────────────────────────────────────────────┘
```

**Backend Changes:**

```python
# New file: backend/agents/discovery_v4/opportunity_mapping.py

class OpportunityMappingStage:
    """
    Stage 3: Map opportunities using JTBD and OST
    Based on Bob Moesta and Teresa Torres frameworks
    """

    async def generate_initial_4_forces(
        self,
        interviews: List[Interview],
        patterns: PatternSynthesis
    ) -> FourForcesModel:
        """
        AI generates initial 4 forces from interview data.
        User then edits/validates.
        """

    async def build_opportunity_tree(
        self,
        outcome: str,
        patterns: PatternSynthesis,
        four_forces: FourForcesModel
    ) -> OpportunitySolutionTree:
        """
        AI suggests OST structure based on patterns.
        User refines and prioritizes.
        """

    async def calculate_force_balance(
        self,
        four_forces: FourForcesModel
    ) -> ForceBalanceScore:
        """
        Analyze whether change is likely.
        Push + Pull vs Anxiety + Habit
        """
```

---

### STAGE 4: Solution Design

**Source:** Gibson Biddle (DHM), Shreyas Doshi (Pre-mortems)

**Purpose:** Evaluate solution approaches with frameworks

**User Experience:**
```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: SOLUTION DESIGN                                        │
│ "Delight in hard-to-copy, margin-enhancing ways" - Gibson Biddle│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ DHM SCORECARD                                                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ SOLUTION: AI-powered competitive intelligence dashboard         │
│                                                                 │
│ D - DELIGHT (How much better than alternatives?)               │
│     ┌────────────────────────────────────────────────────────┐ │
│     │ ○○○○○○○○●○  Score: 8/10                                │ │
│     └────────────────────────────────────────────────────────┘ │
│     Your reasoning:                                            │
│     [10X faster than manual research; real-time updates______] │
│                                                                 │
│ H - HARD TO COPY (What's your moat?)                           │
│     ┌────────────────────────────────────────────────────────┐ │
│     │ ○○○○○●○○○○  Score: 5/10                                │ │
│     └────────────────────────────────────────────────────────┘ │
│     Moat type: [Network effects ▼]                             │
│     Your reasoning:                                            │
│     [Data improves with usage, but tech is replicable________] │
│                                                                 │
│ M - MARGIN (Will this build a sustainable business?)           │
│     ┌────────────────────────────────────────────────────────┐ │
│     │ ○○○○○○○●○○  Score: 7/10                                │ │
│     └────────────────────────────────────────────────────────┘ │
│     Your reasoning:                                            │
│     [SaaS model with high retention potential________________] │
│                                                                 │
│ DHM TOTAL: 20/30 ✅ Gibson's threshold: 20+ to proceed         │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ PRE-MORTEM (Shreyas Doshi)                                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ "Imagine it's 6 months from now. This product has FAILED.      │
│  What went wrong?"                                              │
│                                                                 │
│ 🐯 TIGERS (Real threats that could kill us)                    │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ 1. [Data accuracy - users won't trust inaccurate info_] │ │
│    │ 2. [Enterprise sales cycle - can't survive long enough] │ │
│    │ 3. [_____________________________________________]       │ │
│    │ [+ Add Tiger]                                           │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 📄 PAPER TIGERS (Seem scary but aren't)                        │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ 1. [Big tech competitors - they won't serve SMBs______] │ │
│    │ [+ Add Paper Tiger]                                     │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 🐘 ELEPHANTS (Things no one is talking about)                  │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ 1. [Do PMs actually have budget for this?_____________] │ │
│    │ [+ Add Elephant]                                        │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│ MITIGATION PLANS:                                              │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ Tiger 1: Data accuracy                                    │  │
│ │ Mitigation: Human verification layer + confidence scores  │  │
│ │ Owner: [You ▼]                                            │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ [Save Draft]  [← Back to Stage 3]  [Proceed to Stage 5 →]     │
└─────────────────────────────────────────────────────────────────┘
```

---

### STAGE 5: Validation Plan

**Source:** Uri Levine, Dalton Caldwell (YC)

**Purpose:** Design validation experiments before building

**User Experience:**
```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: VALIDATION PLAN                                        │
│ "The only metric that matters is retention" - Uri Levine        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ VALIDATION LADDER                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ Current Rung: [2] Solution Interview                           │
│                                                                 │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ RUNG 5: RETENTION TEST                              ○ TODO │ │
│ │ "Do they come back?" (Uri Levine's PMF test)               │ │
│ │ Metric: Day 7 / Day 30 retention                           │ │
│ └────────────────────────────────────────────────────────────┘ │
│                              ↑                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ RUNG 4: SMOKE TEST                                  ○ TODO │ │
│ │ "Will they pay?"                                           │ │
│ │ Method: Landing page with pricing                          │ │
│ └────────────────────────────────────────────────────────────┘ │
│                              ↑                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ RUNG 3: PROTOTYPE TEST                              ○ TODO │ │
│ │ "Can they use it?"                                         │ │
│ │ Method: Clickable prototype, 5 user tests                  │ │
│ └────────────────────────────────────────────────────────────┘ │
│                              ↑                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ RUNG 2: SOLUTION INTERVIEW                    ● IN PROGRESS│ │
│ │ "Does this solve their problem?"                           │ │
│ │ Method: Show mockup, observe reaction                      │ │
│ │                                                            │ │
│ │ Progress: 2/5 interviews completed                         │ │
│ │ [Add Result] [View Results]                                │ │
│ └────────────────────────────────────────────────────────────┘ │
│                              ↑                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ RUNG 1: PROBLEM INTERVIEW                        ✓ COMPLETE│ │
│ │ "Is this a real problem?"                                  │ │
│ │ Method: Story collection (Teresa Torres)                   │ │
│ │                                                            │ │
│ │ Result: 5/5 interviews, strong problem validation          │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ EXPERIMENT DESIGN                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ NEXT EXPERIMENT: Solution Interview                            │
│                                                                 │
│ Hypothesis: "PMs will express excitement when shown a          │
│ dashboard that auto-updates competitor pricing"                │
│                                                                 │
│ Success Criteria:                                              │
│ [4 of 5 interviewees say "I would use this today"____________] │
│                                                                 │
│ Failure Criteria:                                              │
│ [<3 express interest OR >2 say "I don't trust AI accuracy"___] │
│                                                                 │
│ Target Participants:                                           │
│ [5 PMs at Series A-C startups who do competitive research____] │
│                                                                 │
│ Timeline: [1 week ▼]                                           │
│                                                                 │
│ [Save Experiment]                                              │
│                                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                 │
│ [Save Draft]  [← Back to Stage 4]  [Complete Discovery →]     │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Design for Stage-by-Stage Execution

### New Endpoints

```python
# backend/api/discovery_v4_routes.py

# ============================================================
# SESSION MANAGEMENT
# ============================================================

@router.post("/discovery/sessions")
async def create_discovery_session(
    product_idea: str,
    industry: str,
    target_market: str
) -> DiscoverySession:
    """Create a new discovery session."""

@router.get("/discovery/sessions/{session_id}")
async def get_session(session_id: str) -> DiscoverySession:
    """Get session with all stage outputs."""

@router.get("/discovery/sessions/{session_id}/status")
async def get_session_status(session_id: str) -> SessionStatus:
    """Get which stages are complete/in-progress."""

# ============================================================
# STAGE EXECUTION (Run Individual Stages)
# ============================================================

@router.post("/discovery/sessions/{session_id}/stages/{stage}/run")
async def run_stage(
    session_id: str,
    stage: Literal["problem_love", "customer_truth", "opportunity_mapping",
                   "solution_design", "validation_plan"]
) -> StageOutput:
    """
    Run a specific stage.
    - Can be run independently
    - Uses outputs from previous stages if available
    - Can be re-run to regenerate
    """

@router.post("/discovery/sessions/{session_id}/stages/{stage}/ai-assist")
async def get_ai_assistance(
    session_id: str,
    stage: str,
    assistance_type: str,  # "coaching", "synthesis", "suggestions"
    context: dict
) -> AIAssistanceResponse:
    """Get AI coaching/suggestions without running full stage."""

# ============================================================
# STAGE OUTPUTS (Save/Edit User Work)
# ============================================================

@router.put("/discovery/sessions/{session_id}/stages/{stage}/output")
async def save_stage_output(
    session_id: str,
    stage: str,
    output: StageOutput
) -> StageOutput:
    """
    Save user's work for a stage.
    - User can edit AI-generated outputs
    - User can save partial progress
    - Triggers re-validation
    """

@router.get("/discovery/sessions/{session_id}/stages/{stage}/output")
async def get_stage_output(session_id: str, stage: str) -> StageOutput:
    """Get saved output for a stage."""

# ============================================================
# INTERVIEW MANAGEMENT (Stage 2)
# ============================================================

@router.post("/discovery/sessions/{session_id}/interviews")
async def add_interview(
    session_id: str,
    interview: InterviewInput
) -> Interview:
    """Add a customer interview."""

@router.get("/discovery/sessions/{session_id}/interviews")
async def list_interviews(session_id: str) -> List[Interview]:
    """List all interviews for session."""

@router.post("/discovery/sessions/{session_id}/interviews/synthesize")
async def synthesize_interviews(session_id: str) -> PatternSynthesis:
    """AI synthesizes patterns from interviews."""

# ============================================================
# STAGE-SPECIFIC HELPERS
# ============================================================

@router.post("/discovery/sessions/{session_id}/tarpit-check")
async def check_tarpit(session_id: str) -> TarpitAnalysis:
    """Check if idea is a tarpit (Stage 1)."""

@router.post("/discovery/sessions/{session_id}/interview-guide")
async def generate_interview_guide(session_id: str) -> InterviewGuide:
    """Generate Teresa Torres interview guide (Stage 2)."""

@router.post("/discovery/sessions/{session_id}/four-forces")
async def generate_four_forces(session_id: str) -> FourForcesModel:
    """Generate 4 forces from interviews (Stage 3)."""

@router.post("/discovery/sessions/{session_id}/opportunity-tree")
async def generate_opportunity_tree(session_id: str) -> OpportunitySolutionTree:
    """Generate OST from patterns (Stage 3)."""

@router.post("/discovery/sessions/{session_id}/dhm-analysis")
async def analyze_dhm(session_id: str, solution: str) -> DHMAnalysis:
    """AI-assisted DHM scoring (Stage 4)."""

@router.post("/discovery/sessions/{session_id}/pre-mortem")
async def run_pre_mortem(session_id: str) -> PreMortemOutput:
    """AI-assisted pre-mortem (Stage 4)."""

# ============================================================
# EXPORT & CONTINUE
# ============================================================

@router.post("/discovery/sessions/{session_id}/export")
async def export_discovery(
    session_id: str,
    format: Literal["pdf", "notion", "json"]
) -> ExportResult:
    """Export discovery pack."""

@router.post("/discovery/sessions/{session_id}/continue-to-strategy")
async def continue_to_strategy(session_id: str) -> StrategySession:
    """
    Continue to strategy phase.
    Creates new strategy session with discovery outputs as input.
    """
```

---

## State Management

### New Discovery State Structure

```python
# backend/models/discovery_v4_state.py

class DiscoverySessionV4(BaseModel):
    """
    New discovery session with stage-by-stage execution.
    Each stage can be run, edited, and approved independently.
    """

    # Session metadata
    session_id: str
    created_at: datetime
    updated_at: datetime
    status: SessionStatus

    # Initial inputs
    product_idea: str
    industry: str
    target_market: str
    additional_context: Optional[str]

    # Stage outputs (each stage is optional)
    stages: Dict[str, StageState] = {
        "problem_love": StageState(),
        "customer_truth": StageState(),
        "opportunity_mapping": StageState(),
        "solution_design": StageState(),
        "validation_plan": StageState()
    }

    # User's interview data (Stage 2)
    interviews: List[Interview] = []

    # Cross-stage data
    patterns: Optional[PatternSynthesis] = None
    four_forces: Optional[FourForcesModel] = None
    opportunity_tree: Optional[OpportunitySolutionTree] = None

    # Readiness checks
    readiness: Dict[str, bool] = {
        "problem_validated": False,
        "enough_interviews": False,
        "opportunities_mapped": False,
        "solution_designed": False,
        "validation_planned": False
    }

class StageState(BaseModel):
    """State of a single stage."""
    status: Literal["not_started", "in_progress", "completed", "approved"]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    approved_at: Optional[datetime]

    # Output can be AI-generated or user-edited
    output: Optional[dict] = None
    output_source: Literal["ai_generated", "user_edited", "user_created"] = "ai_generated"

    # User's notes/edits
    user_notes: Optional[str] = None
    user_edits: List[UserEdit] = []

    # AI coaching provided
    coaching_provided: List[CoachingMessage] = []

    # Validation
    score: Optional[int] = None  # Stage-specific score
    validation_issues: List[str] = []
```

### Stage Transitions

```python
class StageTransitionManager:
    """
    Manages stage transitions and dependencies.
    Ensures stages can be run independently but with proper context.
    """

    STAGE_ORDER = [
        "problem_love",
        "customer_truth",
        "opportunity_mapping",
        "solution_design",
        "validation_plan"
    ]

    STAGE_DEPENDENCIES = {
        "problem_love": [],  # No dependencies
        "customer_truth": ["problem_love"],  # Needs problem context
        "opportunity_mapping": ["customer_truth"],  # Needs interview data
        "solution_design": ["opportunity_mapping"],  # Needs opportunities
        "validation_plan": ["solution_design"]  # Needs solution to validate
    }

    def can_run_stage(self, session: DiscoverySessionV4, stage: str) -> Tuple[bool, List[str]]:
        """
        Check if stage can be run.
        Returns (can_run, missing_dependencies)
        """
        dependencies = self.STAGE_DEPENDENCIES[stage]
        missing = []

        for dep in dependencies:
            if session.stages[dep].status not in ["completed", "approved"]:
                missing.append(dep)

        # Allow running with warnings for missing deps
        return (len(missing) == 0, missing)

    def can_skip_stage(self, stage: str) -> bool:
        """
        Some stages can be skipped if user has own data.
        """
        skippable = ["problem_love"]  # User might have already validated
        return stage in skippable

    def get_context_for_stage(self, session: DiscoverySessionV4, stage: str) -> StageContext:
        """
        Get context from previous stages for running current stage.
        """
        context = StageContext()

        if stage != "problem_love" and session.stages["problem_love"].output:
            context.problem_statement = session.stages["problem_love"].output.get("problem_statement")

        if stage in ["opportunity_mapping", "solution_design", "validation_plan"]:
            context.interviews = session.interviews
            context.patterns = session.patterns

        if stage in ["solution_design", "validation_plan"]:
            context.opportunity_tree = session.opportunity_tree
            context.four_forces = session.four_forces

        if stage == "validation_plan":
            context.solution = session.stages["solution_design"].output

        return context
```

---

## Prompt Redesign

### FROM: Generation Prompts
### TO: Coaching Prompts

```python
# backend/agents/discovery_v4/prompts.py

# ============================================================
# STAGE 1: PROBLEM LOVE PROMPTS
# ============================================================

PROBLEM_LOVE_COACHING_PROMPT = """
You are a product discovery coach helping a PM validate their problem.
Your role is to coach, not generate. Ask hard questions like Uri Levine.

## YOUR COACHING PHILOSOPHY
- "Fall in love with the problem, not the solution" - Uri Levine
- "A problem that is everyone's problem is no one's problem"
- "If no one else has tried to solve it, maybe it's not a real problem"

## USER'S PROBLEM STATEMENT
{problem_statement}

## COACHING TASK
Analyze this problem statement and provide coaching feedback:

1. SPECIFICITY CHECK
   - Is this a specific struggling moment or a broad category?
   - Can you picture a real person in a real situation?
   - Would two PMs understand this the same way?

2. FREQUENCY CHECK
   - How often would someone encounter this?
   - Daily problems build habits; rare problems need 10X solutions

3. EXISTING ALTERNATIVES
   - What do people do today? If nothing exists, why?
   - "If no one else has tried to solve it, maybe it's not a real problem"

4. TARPIT CHECK
   - Does this resemble known tarpit ideas?
   - Social coordination apps, music discovery, local social networks, etc.

## OUTPUT FORMAT
Provide coaching in a supportive but challenging tone.
Ask questions that make the PM think deeper.
Don't generate answers - prompt reflection.
"""

TARPIT_CHECK_PROMPT = """
You are a startup advisor who has seen thousands of failed startups.
Analyze this problem/solution for tarpit patterns.

## KNOWN TARPIT PATTERNS (from Dalton Caldwell, YC)
1. Apps to coordinate meeting up with friends
2. Music discovery apps
3. Local social networks
4. Calendars that schedule themselves
5. Social networks for X (niche groups)
6. Apps that require both parties to have the app
7. Marketplace for local services
8. Better email clients
9. Social todo lists

## USER'S IDEA
Problem: {problem_statement}
Solution concept: {solution_concept}

## ANALYSIS TASK
1. Calculate similarity to each known tarpit (0-100%)
2. Identify specific concerns
3. Ask: "What do YOU know that all those failed startups didn't?"

Be direct but not discouraging. Some tarpits DO get solved eventually.
"""

# ============================================================
# STAGE 2: CUSTOMER TRUTH PROMPTS
# ============================================================

INTERVIEW_SYNTHESIS_PROMPT = """
You are synthesizing real customer interviews using Teresa Torres's methodology.

## TERESA TORRES PRINCIPLES
- "Interview for stories, not answers"
- "The opportunity is an unmet need, pain point, or desire"
- Evidence from real interviews is E1 tier (direct evidence)

## INTERVIEWS TO SYNTHESIZE
{interviews_json}

## SYNTHESIS TASK
Analyze these real interviews and extract:

1. PAIN PATTERNS
   - What struggling moments appear in multiple interviews?
   - Quote the exact words customers used
   - Note frequency: how many interviews mentioned this?

2. TRIGGER PATTERNS
   - What situations trigger the need?
   - When does the problem become acute?

3. OUTCOME PATTERNS
   - What does "success" look like to customers?
   - What emotional state do they want to achieve?

4. CONTRADICTIONS
   - Where do customers disagree?
   - What might explain the differences?

5. GAPS
   - What personas haven't we interviewed?
   - What questions haven't we explored?

## CRITICAL RULES
- Only cite what's in the actual interviews
- Use exact quotes, not paraphrases
- Mark everything as E1 (direct evidence)
- Highlight where evidence is thin
"""

INTERVIEW_GUIDE_PROMPT = """
Generate a Teresa Torres-style interview guide.

## TERESA TORRES METHOD
- Never ask "What do you want?"
- Always ask "Tell me about the last time..."
- Collect stories, not opinions
- Follow the energy - go deeper on emotional moments

## CONTEXT
Problem space: {problem_statement}
Target user: {target_user}
Previous interviews found: {previous_findings}

## GENERATE INTERVIEW GUIDE
Create 10 questions that:
1. Start with story collection ("Tell me about...")
2. Follow up with context questions ("What happened next?")
3. Explore emotions ("How did that feel?")
4. Understand current behavior ("What do you do today?")
5. End with expansion ("Who else struggles with this?")

DO NOT ask:
- "Would you use a product that...?"
- "What features would you want?"
- "What's your biggest pain point?"
"""

# ============================================================
# STAGE 3: OPPORTUNITY MAPPING PROMPTS
# ============================================================

FOUR_FORCES_GENERATION_PROMPT = """
Generate Bob Moesta's 4 Forces model from interview data.

## BOB MOESTA'S 4 FORCES
F1: PUSH - What's broken about the current situation?
F2: PULL - What's attractive about a new solution?
F3: ANXIETY - What fears prevent switching?
F4: HABIT - What comfort keeps them in status quo?

## CHANGE EQUATION
Change happens when: Push + Pull > Anxiety + Habit

## INTERVIEW DATA
{pattern_synthesis_json}

## GENERATION TASK
Extract the 4 forces from the interview data:

For each force:
1. List specific items from interviews
2. Cite the interview evidence (E1)
3. Rate strength (1-10)

Calculate force balance:
- Sum of Push + Pull strengths
- Sum of Anxiety + Habit strengths
- Prediction: Will change happen?
"""

OPPORTUNITY_TREE_PROMPT = """
Build an Opportunity Solution Tree using Teresa Torres's framework.

## OST STRUCTURE
- Start with OUTCOME (what we're trying to achieve)
- Branch into OPPORTUNITIES (unmet needs, pain points, desires)
- Each opportunity branches into potential SOLUTIONS

## CONTEXT
Target outcome: {outcome}
Pain patterns: {pain_patterns}
Trigger patterns: {trigger_patterns}

## GENERATION TASK
Create an OST with:
1. Clear outcome statement
2. 3-5 opportunities (from interview patterns)
3. 2-3 solution ideas per opportunity

For each opportunity:
- Link to specific interview evidence
- Note how many interviews support it
- Rank by frequency/severity
"""

# ============================================================
# STAGE 4: SOLUTION DESIGN PROMPTS
# ============================================================

DHM_COACHING_PROMPT = """
Coach the user through Gibson Biddle's DHM analysis.

## DHM FRAMEWORK
D - DELIGHT: Is this 10X better than alternatives?
H - HARD TO COPY: Network effects? Data moat? Brand? Scale?
M - MARGIN: Will this build a sustainable business?

## SOLUTION TO ANALYZE
{solution_description}

## COMPETITIVE CONTEXT
Current alternatives: {alternatives}
Market dynamics: {market_context}

## COACHING TASK
For each dimension, provide:
1. Questions to consider
2. Warning signs to watch
3. Comparison to known successful products

Gibson's rule: Total DHM should be 20+ out of 30 to proceed.
"""

PRE_MORTEM_FACILITATION_PROMPT = """
Facilitate a Shreyas Doshi pre-mortem exercise.

## PRE-MORTEM PROMPT
"Imagine it's 6 months from now. This product has FAILED miserably.
What went wrong?"

## CONTEXT
Solution: {solution}
Market: {market}
Competitive landscape: {competitors}

## FACILITATION TASK
Generate potential:

1. TIGERS (Real threats that could kill the product)
   - Technical risks
   - Market risks
   - Competitive risks
   - Execution risks

2. PAPER TIGERS (Seem scary but probably aren't)
   - Common fears that data doesn't support

3. ELEPHANTS (Things no one is talking about)
   - Uncomfortable truths
   - Hidden assumptions
   - Political/organizational issues

For each Tiger, suggest:
- Mitigation strategy
- Early warning signals
- Owner assignment
"""
```

---

## Migration Path

### Phase 1: Backend Infrastructure (Week 1-2)
1. Create new `discovery_v4` module structure
2. Implement new schemas and state management
3. Build stage execution engine
4. Create new API endpoints

### Phase 2: Stage Implementations (Week 3-4)
1. Implement Problem Love stage
2. Implement Customer Truth stage with interview tracking
3. Implement Opportunity Mapping stage
4. Implement Solution Design stage
5. Implement Validation Plan stage

### Phase 3: Frontend Integration (Week 5-6)
1. Build new discovery UI components
2. Implement stage-by-stage navigation
3. Create interview input forms
4. Build visual tools (OST builder, 4 forces mapper)

### Phase 4: Integration & Testing (Week 7-8)
1. Connect to existing strategy/delivery phases
2. Migrate existing sessions (optional)
3. A/B test new vs old flow
4. Gather user feedback

---

## Files to Create

| File | Purpose |
|------|---------|
| `backend/agents/discovery_v4/__init__.py` | Module init |
| `backend/agents/discovery_v4/problem_love.py` | Stage 1 implementation |
| `backend/agents/discovery_v4/customer_truth.py` | Stage 2 implementation |
| `backend/agents/discovery_v4/opportunity_mapping.py` | Stage 3 implementation |
| `backend/agents/discovery_v4/solution_design.py` | Stage 4 implementation |
| `backend/agents/discovery_v4/validation_plan.py` | Stage 5 implementation |
| `backend/agents/discovery_v4/prompts.py` | All coaching prompts |
| `backend/agents/discovery_v4/stage_manager.py` | Stage transitions |
| `backend/models/discovery_v4_schemas.py` | New Pydantic models |
| `backend/models/discovery_v4_state.py` | Session state |
| `backend/api/discovery_v4_routes.py` | New API endpoints |

## Files to Modify

| File | Changes |
|------|---------|
| `backend/api/routes.py` | Add discovery v4 router |
| `backend/agents/facilitator.py` | Add v4 discovery integration |
| `backend/main.py` | Include new routes |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time to first output | ~15 min (full pack) | <2 min (first stage) |
| User engagement | Passive waiting | Active participation |
| Evidence quality | E3-E4 (hypothesis) | E1-E2 (real data) |
| Discovery iterations | 1 (one-shot) | 3-5 (iterative) |
| Interview integration | None | Full support |
| User control | None | Full stage control |

---

## Summary

This redesign transforms LifeCycle from an AI that generates documents to an AI that coaches PMs through world-class discovery frameworks. Key changes:

1. **Stage-by-stage execution** - Run, edit, approve each stage independently
2. **Real interview integration** - Teresa Torres methodology with actual customer data
3. **AI as coach** - Prompts guide thinking, not generate content
4. **Framework-based** - Uri Levine, Bob Moesta, Gibson Biddle, Shreyas Doshi
5. **User control** - Edit outputs, re-run stages, skip with own data
6. **Evidence quality** - E1 tier from real interviews vs E4 hypotheses
