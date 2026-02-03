# Inception - Multi-Agent Product Discovery System

<p align="center">
  <img src="docs/logo.svg" alt="Inception Logo" width="120" height="120">
</p>

<p align="center">
  <strong>Transform product ideas into comprehensive inception packs using AI agents</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#usage">Usage</a> •
  <a href="#api-reference">API Reference</a>
</p>

---

## Overview

Inception is an AI-powered product discovery system that transforms raw product ideas into comprehensive inception packs. Using a multi-agent architecture built on LangGraph, it orchestrates specialized AI agents to produce:

- **Customer Research** - Evidence-based market analysis with uncomfortable truths
- **Business Strategy** - Lean Canvas, financial projections, and go-to-market plans
- **Product Requirements Document (PRD)** - Epics, user stories, and acceptance criteria
- **Technical Architecture** - System design, tech stack recommendations, and component diagrams

## Features

### Multi-Agent Orchestration
- **5 Specialized AI Agents** working in concert via LangGraph StateGraph
- **PRD Quality Loop** - Generator → Critic → Formatter with automatic revision cycles
- **Evidence-Based Research** - Tiered evidence system (E1: Direct quotes → E4: Hypothesis)

### Modern Tech Stack
- **Backend**: FastAPI + LangGraph + Google Gemini API
- **Frontend**: React 18 + TypeScript + Vite
- **Validation**: Pydantic v2 with strict schema enforcement

### User Experience
- **Claude-like UI** - Clean, centered interface for product idea input
- **Real-time Progress** - Live tracking of agent execution
- **Tabbed Results Viewer** - Navigate through all sections of the inception pack

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ DiscoveryForm│  │ProgressTracker│  │InceptionPackViewer │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 LangGraph Orchestrator                    │  │
│  │  ┌────────────┐    ┌────────────┐    ┌──────────────┐   │  │
│  │  │ Customer   │───▶│ Business   │───▶│     PRD      │   │  │
│  │  │ Research   │    │ Strategy   │    │  Sub-Graph   │   │  │
│  │  └────────────┘    └────────────┘    └──────────────┘   │  │
│  │                                             │            │  │
│  │  ┌────────────┐    ┌────────────┐          │            │  │
│  │  │ Executive  │◀───│ Critique   │◀───┬─────┘            │  │
│  │  │  Summary   │    │   Agent    │    │                  │  │
│  │  └────────────┘    └────────────┘    ▼                  │  │
│  │                              ┌──────────────────┐       │  │
│  │                              │ Tech Architect   │       │  │
│  │                              └──────────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Google Gemini  │
                    │      API        │
                    └─────────────────┘
```

### PRD Sub-Graph (Quality Assurance Loop)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    PRD      │────▶│    PRD      │────▶│    PRD      │
│  Generator  │     │   Critic    │     │  Formatter  │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          │ Score < 0.75?
                          ▼
                    ┌─────────────┐
                    │   Revise    │──────┐
                    │    PRD      │      │
                    └─────────────┘      │
                          ▲              │
                          └──────────────┘
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/urban-fortnight.git
   cd urban-fortnight
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## Usage

1. **Enter your product idea** in the centered text area
2. **Add optional context** like industry and target market
3. **Click "Generate"** to start the multi-agent discovery process
4. **Watch real-time progress** as each agent completes its analysis
5. **Explore the results** through the tabbed interface

### Example Input

```
A mobile app that helps small business owners manage their inventory
using smartphone cameras and AI-powered barcode scanning. The app should
work offline and sync when connectivity is restored.
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/discovery/start` | Start a new discovery session |
| `GET` | `/api/discovery/session/{id}` | Get session status and results |
| `GET` | `/api/health` | Health check endpoint |

### Start Discovery Request

```json
{
  "product_idea": "string (required, min 10 chars)",
  "industry": "string (optional)",
  "target_market": "string (optional)",
  "constraints": ["string array (optional)"],
  "additional_context": "string (optional)"
}
```

### Response Structure

The inception pack includes:

- **customer_research** - Evidence-based market analysis
- **business_strategy** - Lean canvas and financial projections
- **product_requirements** - PRD with epics and user stories
- **technical_architecture** - System design and tech recommendations
- **critique** - Cross-validation and quality assessment
- **executive_summary** - High-level overview

## Project Structure

```
urban-fortnight/
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py      # LangGraph workflow
│   │   ├── customer_research.py # Customer research agent
│   │   ├── business_strategy.py # Business strategy agent
│   │   ├── prd_generator.py     # PRD generation agent
│   │   ├── prd_critic.py        # PRD quality critic
│   │   ├── prd_formatter.py     # PRD formatting agent
│   │   ├── technical_architect.py
│   │   ├── critique.py          # Cross-validation agent
│   │   └── prompts.py           # All agent prompts
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── main.py                  # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DiscoveryForm.tsx
│   │   │   ├── ProgressTracker.tsx
│   │   │   └── InceptionPackViewer.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── types/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── App.css
│   └── package.json
└── README.md
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `GEMINI_MODEL` | Model name (default: gemini-2.0-flash) | No |
| `CORS_ORIGINS` | Allowed CORS origins | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

## Evidence Tiers (Customer Research)

The customer research agent uses a tiered evidence system:

| Tier | Description | Example |
|------|-------------|---------|
| **E1** | Direct quotes/observations | "User said: I spend 2 hours daily on this" |
| **E2** | Observed behavior data | Click patterns, usage analytics |
| **E3** | Market/industry data | Market reports, competitor analysis |
| **E4** | Hypothesis/inference | Logical deduction from patterns |

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- Powered by [Google Gemini](https://deepmind.google/technologies/gemini/) for AI capabilities
- UI inspired by [Claude](https://claude.ai) by Anthropic

---

<p align="center">
  Made with ❤️ using Multi-Agent AI
</p>
