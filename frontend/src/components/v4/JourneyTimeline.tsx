/**
 * JourneyTimeline - Unified sidebar component for Discovery and Execution views
 * Shows the complete journey from Discovery through Quality Review
 */

import React from 'react';
import {
  Heart,
  Users,
  Map,
  Lightbulb,
  CheckCircle,
  Check,
  Loader2,
  Lock,
  Target,
  FileText,
  Cpu,
  Palette,
  Award,
  ChevronDown,
  ChevronRight,
  Eye,
} from 'lucide-react';
import '../../styles/theme-v4.css';

// Discovery stages definition
const DISCOVERY_STAGES = [
  { id: 'problem_love', name: 'Problem Love', icon: Heart },
  { id: 'customer_truth', name: 'Customer Truth', icon: Users },
  { id: 'opportunity_mapping', name: 'Opportunity Map', icon: Map },
  { id: 'solution_design', name: 'Solution Design', icon: Lightbulb },
  { id: 'validation_plan', name: 'Validation Plan', icon: CheckCircle },
];

// Execution phases definition
const EXECUTION_PHASES = [
  {
    id: 'strategy',
    name: 'Strategy & Planning',
    icon: Target,
    agents: ['planner', 'business_strategy', 'gtm', 'financial_model'],
  },
  {
    id: 'requirements',
    name: 'Product Requirements',
    icon: FileText,
    agents: ['prd_generator', 'prd_critic', 'prd_formatter'],
  },
  {
    id: 'architecture',
    name: 'Technical Architecture',
    icon: Cpu,
    agents: ['technical_architect', 'legal_regulatory'],
  },
  {
    id: 'design',
    name: 'Design & Prototype',
    icon: Palette,
    agents: ['wireframe', 'prototype'],
  },
  {
    id: 'quality',
    name: 'Quality Review',
    icon: Award,
    agents: ['critique', 'executive_summary'],
  },
];

export interface DiscoveryStage {
  id: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'approved' | 'skipped';
  score?: number;
}

export interface ExecutionAgent {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
}

export interface ExecutionPhase {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  agents: ExecutionAgent[];
}

interface JourneyTimelineProps {
  // Discovery state
  discoveryStages?: Record<string, DiscoveryStage>;
  activeDiscoveryStage?: string;
  onDiscoveryStageClick?: (stageId: string) => void;
  discoveryComplete?: boolean;
  /** Allow clicking on Discovery stages even in execution view (to view outputs) */
  allowDiscoveryClick?: boolean;

  // Execution state
  executionPhases?: ExecutionPhase[];
  currentExecutionPhase?: string;
  onAgentClick?: (agentId: string) => void;

  // View mode
  currentView: 'discovery' | 'execution';
}

export function JourneyTimeline({
  discoveryStages = {},
  activeDiscoveryStage,
  onDiscoveryStageClick,
  discoveryComplete = false,
  allowDiscoveryClick = false,
  executionPhases = [],
  currentExecutionPhase,
  onAgentClick,
  currentView,
}: JourneyTimelineProps) {
  // Keep Discovery expanded if in discovery view OR if discovery is complete (in execution view)
  const [isDiscoveryExpanded, setIsDiscoveryExpanded] = React.useState(
    currentView === 'discovery' || discoveryComplete
  );

  // Auto-expand when discovery is complete or we're in discovery view
  React.useEffect(() => {
    if (currentView === 'discovery' || discoveryComplete) {
      setIsDiscoveryExpanded(true);
    }
  }, [currentView, discoveryComplete]);

  const getDiscoveryStatus = (stageId: string): DiscoveryStage['status'] => {
    return discoveryStages[stageId]?.status || 'not_started';
  };

  const getStatusIcon = (status: string, Icon: React.ElementType) => {
    switch (status) {
      case 'completed':
      case 'approved':
        return <Check size={14} />;
      case 'in_progress':
      case 'running':
        return <Loader2 size={14} className="jt-spin" />;
      default:
        return <Icon size={14} />;
    }
  };

  return (
    <div className="journey-timeline">
      <div className="jt-header">
        <h3>Journey</h3>
      </div>

      {/* Discovery Section */}
      <div className={`jt-section ${discoveryComplete ? 'complete' : ''} ${currentView === 'discovery' ? 'active' : ''}`}>
        <button
          className="jt-section-header"
          onClick={() => setIsDiscoveryExpanded(!isDiscoveryExpanded)}
        >
          <div className="jt-section-icon">
            {discoveryComplete ? <Check size={14} /> : <Loader2 size={14} className={currentView === 'discovery' ? 'jt-spin' : ''} />}
          </div>
          <span className="jt-section-name">Discovery</span>
          {discoveryComplete && <span className="jt-badge-complete">Complete</span>}
          {isDiscoveryExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>

        {isDiscoveryExpanded && (
          <div className="jt-stages">
            {DISCOVERY_STAGES.map((stage) => {
              const status = getDiscoveryStatus(stage.id);
              const isActive = activeDiscoveryStage === stage.id;
              const isComplete = status === 'completed' || status === 'approved';
              const Icon = stage.icon;

              return (
                <button
                  key={stage.id}
                  className={`jt-stage ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''} ${status === 'in_progress' ? 'running' : ''} ${allowDiscoveryClick ? 'clickable' : ''}`}
                  onClick={() => onDiscoveryStageClick?.(stage.id)}
                  disabled={currentView !== 'discovery' && !allowDiscoveryClick}
                >
                  <div className="jt-stage-icon">
                    {getStatusIcon(status, Icon)}
                  </div>
                  <span className="jt-stage-name">{stage.name}</span>
                  {discoveryStages[stage.id]?.score !== undefined && (
                    <span className="jt-stage-score">{discoveryStages[stage.id]?.score}/10</span>
                  )}
                  {/* View indicator when clickable in execution view */}
                  {allowDiscoveryClick && isComplete && (
                    <span className="jt-view-indicator" title="View stage output">
                      <Eye size={14} />
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Execution Phases */}
      {EXECUTION_PHASES.map((phase) => {
        const execPhase = executionPhases.find(p => p.id === phase.id);
        const isLocked = !discoveryComplete && !execPhase;
        const isActive = currentExecutionPhase === phase.id;
        const isComplete = execPhase?.status === 'completed';
        const isRunning = execPhase?.status === 'running';
        const Icon = phase.icon;

        return (
          <div
            key={phase.id}
            className={`jt-section ${isLocked ? 'locked' : ''} ${isComplete ? 'complete' : ''} ${isActive ? 'active' : ''}`}
          >
            <div className="jt-section-header">
              <div className="jt-section-icon">
                {isLocked ? (
                  <Lock size={14} />
                ) : isComplete ? (
                  <Check size={14} />
                ) : isRunning ? (
                  <Loader2 size={14} className="jt-spin" />
                ) : (
                  <Icon size={14} />
                )}
              </div>
              <span className="jt-section-name">{phase.name}</span>
              {isLocked && <Lock size={12} className="jt-lock-badge" />}
            </div>

            {/* Show agents when phase is active or complete */}
            {!isLocked && execPhase && (isActive || isComplete) && (
              <div className="jt-agents">
                {execPhase.agents.map((agent) => (
                  <button
                    key={agent.id}
                    className={`jt-agent ${agent.status}`}
                    onClick={() => onAgentClick?.(agent.id)}
                  >
                    <span className={`jt-agent-dot ${agent.status}`} />
                    <span className="jt-agent-name">{agent.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}

      <style>{`
        .journey-timeline {
          display: flex;
          flex-direction: column;
          background: var(--v4-surface);
          border: 1px solid var(--v4-border-subtle);
          border-radius: var(--v4-radius-lg);
          overflow: hidden;
          box-shadow: var(--v4-shadow-xs);
        }

        .jt-header {
          padding: 16px 20px;
          border-bottom: 1px solid var(--v4-border-subtle);
        }

        .jt-header h3 {
          margin: 0;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: var(--v4-text-muted);
          font-family: var(--v4-font-body);
        }

        .jt-section {
          border-bottom: 1px solid var(--v4-border-subtle);
          transition: background 0.2s ease;
        }

        .jt-section:last-child {
          border-bottom: none;
        }

        .jt-section.locked {
          opacity: 0.5;
        }

        .jt-section.active {
          background: var(--v4-accent-lighter);
        }

        .jt-section-header {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;
          padding: 14px 16px;
          background: none;
          border: none;
          cursor: pointer;
          text-align: left;
          transition: background 0.15s ease;
        }

        .jt-section-header:hover:not(:disabled) {
          background: var(--v4-bg-subtle);
        }

        .jt-section.locked .jt-section-header {
          cursor: default;
        }

        .jt-section-icon {
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background: var(--v4-bg-subtle);
          color: var(--v4-text-secondary);
          transition: all 0.2s ease;
        }

        .jt-section.active .jt-section-icon {
          background: var(--v4-accent);
          color: white;
          box-shadow: 0 2px 8px rgba(194, 65, 12, 0.25);
        }

        .jt-section.complete .jt-section-icon {
          background: var(--v4-success);
          color: white;
        }

        .jt-section-name {
          flex: 1;
          font-size: 13px;
          font-weight: 500;
          color: var(--v4-text);
          font-family: var(--v4-font-display);
        }

        .jt-section.locked .jt-section-name {
          color: var(--v4-text-muted);
        }

        .jt-badge-complete {
          padding: 3px 10px;
          font-size: 10px;
          font-weight: 600;
          color: var(--v4-success);
          background: var(--v4-success-light);
          border-radius: var(--v4-radius-full);
        }

        .jt-lock-badge {
          color: var(--v4-text-muted);
        }

        .jt-stages,
        .jt-agents {
          padding: 0 12px 12px 12px;
          animation: jt-expand 0.2s ease;
        }

        @keyframes jt-expand {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .jt-stage,
        .jt-agent {
          display: flex;
          align-items: center;
          gap: 10px;
          width: calc(100% - 20px);
          padding: 10px 12px;
          margin-left: 20px;
          background: none;
          border: none;
          border-left: 2px solid var(--v4-border-subtle);
          cursor: pointer;
          text-align: left;
          transition: all 0.15s ease;
          border-radius: 0 var(--v4-radius-sm) var(--v4-radius-sm) 0;
        }

        .jt-stage:hover:not(:disabled),
        .jt-agent:hover {
          background: var(--v4-bg-subtle);
        }

        .jt-stage:disabled {
          cursor: default;
          opacity: 0.6;
        }

        .jt-stage.clickable:disabled {
          cursor: pointer;
          opacity: 1;
        }

        .jt-stage.clickable:disabled:hover {
          background: var(--v4-bg-subtle);
        }

        .jt-stage.active {
          border-left-color: var(--v4-accent);
          background: var(--v4-accent-light);
        }

        .jt-stage.complete {
          border-left-color: var(--v4-success);
        }

        .jt-stage.running {
          border-left-color: var(--v4-accent);
        }

        .jt-stage-icon {
          width: 22px;
          height: 22px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--v4-text-muted);
        }

        .jt-stage.active .jt-stage-icon {
          color: var(--v4-accent);
        }

        .jt-stage.complete .jt-stage-icon {
          color: var(--v4-success);
        }

        .jt-stage.running .jt-stage-icon {
          color: var(--v4-accent);
        }

        .jt-stage-name,
        .jt-agent-name {
          flex: 1;
          font-size: 12px;
          color: var(--v4-text-secondary);
        }

        .jt-stage.active .jt-stage-name {
          color: var(--v4-text);
          font-weight: 500;
        }

        .jt-stage-score {
          font-size: 10px;
          font-weight: 600;
          color: var(--v4-success);
          background: var(--v4-success-light);
          padding: 3px 8px;
          border-radius: var(--v4-radius-full);
        }

        .jt-view-indicator {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          border-radius: 4px;
          color: var(--v4-text-muted);
          transition: all 0.15s ease;
          flex-shrink: 0;
        }

        .jt-stage:hover .jt-view-indicator {
          color: var(--v4-accent);
          background: var(--v4-accent-lighter);
        }

        /* Enhanced hover for clickable stages */
        .jt-stage.clickable {
          cursor: pointer;
        }

        .jt-stage.clickable:hover {
          background: var(--v4-bg-subtle);
        }

        .jt-stage.clickable:hover .jt-stage-name {
          color: var(--v4-text);
        }

        .jt-agent-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--v4-text-muted);
          transition: all 0.2s ease;
        }

        .jt-agent-dot.running {
          background: var(--v4-accent);
          box-shadow: 0 0 0 3px rgba(194, 65, 12, 0.15);
          animation: jt-pulse 1.5s ease-in-out infinite;
        }

        .jt-agent-dot.completed {
          background: var(--v4-success);
        }

        .jt-agent-dot.error {
          background: var(--v4-error);
        }

        .jt-spin {
          animation: jt-spin 1s linear infinite;
        }

        @keyframes jt-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes jt-pulse {
          0%, 100% { opacity: 1; box-shadow: 0 0 0 3px rgba(194, 65, 12, 0.15); }
          50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(194, 65, 12, 0.1); }
        }
      `}</style>
    </div>
  );
}

export default JourneyTimeline;
