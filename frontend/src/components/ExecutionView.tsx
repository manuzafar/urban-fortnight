/**
 * ExecutionView Component
 *
 * Real-time execution view showing:
 * - Agent progress panel on the left
 * - Live pack preview building on the right
 * - SSE streaming integration
 */

import { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Search,
  TrendingUp,
  FileText,
  Cpu,
  Shield,
  CheckCircle,
  FileCheck,
  Loader2,
  Clock,
  AlertCircle,
  Target,
  Users,
  Rocket,
  DollarSign,
  AlertTriangle,
  Layout,
  PlayCircle,
  Briefcase,
  ClipboardCheck,
  ClipboardList,
} from 'lucide-react';
import { useSSE, type AgentState } from '../hooks/useSSE';
import { getInceptionPack } from '../api/client';
import type { InceptionPack } from '../types/api';
import './ExecutionView.css';

export interface ExecutionViewProps {
  sessionId: string;
  authToken: string;
  onComplete: (pack: InceptionPack) => void;
  onBack: () => void;
}

const AGENT_ICONS: Record<string, React.ReactNode> = {
  // Planning
  planner: <ClipboardList size={18} />,
  // Discovery
  customer_research: <Search size={18} />,
  competitive_intelligence: <Target size={18} />,
  persona_development: <Users size={18} />,
  // Strategy
  business_strategy: <TrendingUp size={18} />,
  gtm_strategy: <Rocket size={18} />,
  financial_modeling: <DollarSign size={18} />,
  // Delivery
  product_requirements: <FileText size={18} />,
  technical_architect: <Cpu size={18} />,
  legal_regulatory: <Shield size={18} />,
  risk_assessment: <AlertTriangle size={18} />,
  // Design
  wireframe_agent: <Layout size={18} />,
  prototype_agent: <PlayCircle size={18} />,
  // Quality
  critique: <CheckCircle size={18} />,
  // Synthesis
  stakeholder_agent: <Briefcase size={18} />,
  validation_agent: <ClipboardCheck size={18} />,
  executive_summary_agent: <FileCheck size={18} />,
  // Legacy
  executive_summary: <FileCheck size={18} />,
};

// Phase display order
const PHASE_ORDER = ['Planning', 'Discovery', 'Strategy', 'Delivery', 'Design', 'Quality', 'Synthesis'];

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function ExecutionView({
  sessionId,
  authToken,
  onComplete,
  onBack,
}: ExecutionViewProps) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isFetchingPack, setIsFetchingPack] = useState(false);

  const {
    isConnected,
    currentAgent,
    agentStates,
    insights,
    progress,
    isComplete,
    completionStatus,
    error,
    agentOrder,
  } = useSSE(sessionId, authToken);

  // Timer
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime((t) => t + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Handle completion
  useEffect(() => {
    if (isComplete && completionStatus === 'completed' && !isFetchingPack) {
      setIsFetchingPack(true);
      getInceptionPack(sessionId)
        .then(onComplete)
        .catch((err) => {
          console.error('Failed to fetch pack:', err);
          setIsFetchingPack(false);
        });
    }
  }, [isComplete, completionStatus, sessionId, onComplete, isFetchingPack]);

  const getAgentStatusClass = (state: AgentState) => {
    switch (state.status) {
      case 'running':
        return 'running';
      case 'completed':
        return 'completed';
      case 'error':
        return 'error';
      default:
        return 'pending';
    }
  };

  // Collect all insights for preview
  const allInsights = Object.entries(insights).flatMap(([agent, agentInsights]) =>
    agentInsights.map((insight) => ({ ...insight, agent }))
  );

  return (
    <div className="execution-view">
      {/* Header */}
      <header className="execution-header">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={18} />
          <span>Back</span>
        </button>

        <div className="execution-title">
          <h1>Generating your inception pack...</h1>
          <div className="execution-meta">
            {isConnected ? (
              <span className="connected-badge">
                <span className="pulse-dot"></span>
                Live
              </span>
            ) : (
              <span className="disconnected-badge">
                <AlertCircle size={14} />
                Connecting...
              </span>
            )}
            <span className="timer">
              <Clock size={14} />
              {formatTime(elapsedTime)}
            </span>
          </div>
        </div>

        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
          <span className="progress-text">{progress}%</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="execution-content">
        {/* Agent Panel */}
        <aside className="agent-panel">
          <h2>Agents</h2>
          <div className="agent-list">
            {PHASE_ORDER.map((phase) => {
              const phaseAgents = agentOrder.filter(
                (agentKey) => agentStates[agentKey]?.phase === phase
              );

              if (phaseAgents.length === 0) return null;

              return (
                <div key={phase} className="agent-phase-group">
                  <h3 className="phase-label">{phase}</h3>
                  <ul className="phase-agents">
                    {phaseAgents.map((agentKey) => {
                      const state = agentStates[agentKey];
                      if (!state) return null;

                      return (
                        <li
                          key={agentKey}
                          className={`agent-card ${getAgentStatusClass(state)} ${
                            currentAgent === agentKey ? 'active' : ''
                          }`}
                        >
                          <div className="agent-icon">
                            {state.status === 'running' ? (
                              <Loader2 size={18} className="spin" />
                            ) : (
                              AGENT_ICONS[agentKey] || <Cpu size={18} />
                            )}
                          </div>
                          <div className="agent-info">
                            <span className="agent-name">{state.displayName}</span>
                            <span className="agent-status-text">
                              {state.status === 'running' && (state.message || 'Processing...')}
                              {state.status === 'completed' && (state.summary || 'Complete')}
                              {state.status === 'pending' && 'Waiting...'}
                              {state.status === 'error' && 'Failed'}
                            </span>
                          </div>
                          {state.status === 'completed' && (
                            <div className="agent-check">
                              <CheckCircle size={16} />
                            </div>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            })}
          </div>
        </aside>

        {/* Pack Preview */}
        <main className="pack-preview">
          <h2>Pack Preview</h2>

          {error && (
            <div className="preview-error">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div className="preview-content">
            {/* Executive Summary Building */}
            <div className="preview-section building">
              <h3>Executive Summary</h3>
              <div className="building-indicator">
                <div className="building-bar"></div>
                <span>Building...</span>
              </div>
            </div>

            {/* Insights appearing */}
            {agentOrder.map((agentKey) => {
              const agentInsights = insights[agentKey] || [];
              const state = agentStates[agentKey];

              if (state?.status !== 'completed' && agentInsights.length === 0) {
                return null;
              }

              return (
                <div key={agentKey} className="preview-section">
                  <h3>{state?.displayName || agentKey}</h3>
                  {agentInsights.length > 0 ? (
                    <ul className="insight-list">
                      {agentInsights.map((insight, idx) => (
                        <li key={idx} className="insight-item animate-in">
                          <CheckCircle size={14} className="insight-check" />
                          <span>{insight.value}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="no-insights">Processing complete</p>
                  )}
                </div>
              );
            })}

            {allInsights.length === 0 && !error && (
              <div className="preview-placeholder">
                <Loader2 size={24} className="spin" />
                <p>Insights will appear here as agents discover them...</p>
              </div>
            )}
          </div>

          {isComplete && completionStatus === 'completed' && (
            <div className="preview-complete">
              <CheckCircle size={24} />
              <span>Pack complete! Loading results...</span>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default ExecutionView;
