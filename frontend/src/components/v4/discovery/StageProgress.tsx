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
} from 'lucide-react';

interface StageState {
  status: 'not_started' | 'in_progress' | 'completed' | 'approved' | 'skipped';
  output?: Record<string, unknown>;
  score?: number;
}

interface DiscoverySession {
  stages: Record<string, StageState>;
  mode: 'quick' | 'guided' | 'deep';
}

interface StageProgressProps {
  session: DiscoverySession;
  activeStage?: string;
  onSelectStage?: (stage: string) => void;
}

const DISCOVERY_STAGES = [
  {
    id: 'problem_love',
    name: 'Problem Love',
    shortName: 'Problem',
    icon: Heart,
    description: 'Validate the problem is worth solving',
    color: '#ef4444', // red
  },
  {
    id: 'customer_truth',
    name: 'Customer Truth',
    shortName: 'Customers',
    icon: Users,
    description: 'Understand real customer needs',
    color: '#f59e0b', // amber
  },
  {
    id: 'opportunity_mapping',
    name: 'Opportunity Map',
    shortName: 'Opportunities',
    icon: Map,
    description: 'Map opportunities to solutions',
    color: '#10b981', // emerald
  },
  {
    id: 'solution_design',
    name: 'Solution Design',
    shortName: 'Solution',
    icon: Lightbulb,
    description: 'Design and evaluate the solution',
    color: '#c2410c', // terracotta (V4 accent)
  },
  {
    id: 'validation_plan',
    name: 'Validation Plan',
    shortName: 'Validation',
    icon: CheckCircle,
    description: 'Plan validation experiments',
    color: '#8b5cf6', // purple
  },
];

// Upcoming phases after Discovery completes
const UPCOMING_PHASES = [
  {
    id: 'strategy',
    name: 'Strategy & Planning',
    icon: Target,
    description: 'Business model & go-to-market',
  },
  {
    id: 'requirements',
    name: 'Product Requirements',
    icon: FileText,
    description: 'PRD, epics & user stories',
  },
  {
    id: 'architecture',
    name: 'Technical Architecture',
    icon: Cpu,
    description: 'System design & tech stack',
  },
  {
    id: 'design',
    name: 'Design & Prototype',
    icon: Palette,
    description: 'Wireframes & interactive prototype',
  },
  {
    id: 'quality',
    name: 'Quality Review',
    icon: Award,
    description: 'Cross-validation & scoring',
  },
];

export function StageProgress({
  session,
  activeStage,
  onSelectStage,
}: StageProgressProps) {
  const getStageStatus = (stageId: string) => {
    const state = session.stages[stageId];
    if (!state) return 'not_started';
    return state.status;
  };

  const isStageClickable = (stageId: string, index: number) => {
    const status = getStageStatus(stageId);

    // Always clickable if complete or in progress
    if (status !== 'not_started') return true;

    // First stage is always clickable
    if (index === 0) return true;

    // Quick mode - all stages clickable
    if (session.mode === 'quick') return true;

    // Check if previous stage is complete
    if (index > 0) {
      const prevStatus = getStageStatus(DISCOVERY_STAGES[index - 1].id);
      return prevStatus === 'completed' || prevStatus === 'approved' || prevStatus === 'skipped';
    }

    return false;
  };

  // Calculate if all discovery stages are complete
  const allDiscoveryComplete = DISCOVERY_STAGES.every((stage) => {
    const state = session.stages[stage.id];
    return state?.status === 'completed' || state?.status === 'approved' || state?.status === 'skipped';
  });

  return (
    <nav className="stage-progress-container" aria-label="Discovery stages">
      <div className="stage-progress-header">
        <h2>Discovery</h2>
      </div>

      <ul className="stage-progress-list" role="list">
        {DISCOVERY_STAGES.map((stage, idx) => {
          const state = session.stages[stage.id] || { status: 'not_started' };
          const isActive = activeStage === stage.id;
          const isComplete = state.status === 'completed' || state.status === 'approved';
          const isInProgress = state.status === 'in_progress';
          const isSkipped = state.status === 'skipped';
          const isClickable = isStageClickable(stage.id, idx);
          const Icon = stage.icon;

          return (
            <li key={stage.id} role="listitem">
              <button
                className={`stage-item ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''} ${isInProgress ? 'in-progress' : ''} ${isSkipped ? 'skipped' : ''} ${!isClickable ? 'locked' : ''}`}
                onClick={() => isClickable && onSelectStage?.(stage.id)}
                disabled={!isClickable}
                aria-current={isActive ? 'step' : undefined}
                aria-disabled={!isClickable}
                aria-label={`${stage.name}: ${isComplete ? 'completed' : isInProgress ? 'in progress' : isSkipped ? 'skipped' : 'not started'}${state.score ? `, score ${state.score} out of 10` : ''}`}
                title={stage.description}
                style={{ '--stage-color': stage.color } as React.CSSProperties}
              >
                {idx > 0 && <div className="stage-connector" aria-hidden="true" />}

                <div className="stage-icon" aria-hidden="true">
                  {isComplete ? (
                    <Check size={18} />
                  ) : isInProgress ? (
                    <Loader2 size={18} className="spin" />
                  ) : !isClickable ? (
                    <Lock size={16} />
                  ) : (
                    <Icon size={18} />
                  )}
                </div>

                <div className="stage-info">
                  <span className="stage-name">{stage.name}</span>
                  <span className="stage-description">{stage.description}</span>
                </div>

                {state.score !== undefined && state.score !== null && (
                  <span className="stage-score" aria-hidden="true">{state.score}/10</span>
                )}
              </button>
            </li>
          );
        })}
      </ul>

      {/* Upcoming Phases Preview */}
      <div className="upcoming-phases-section" role="region" aria-label="Upcoming phases">
        <div className="upcoming-header">
          <h3>Coming Up</h3>
          <Lock size={14} className="lock-icon" aria-hidden="true" />
        </div>
        <ul className="upcoming-phases-list" role="list">
          {UPCOMING_PHASES.map((phase) => {
            const Icon = phase.icon;
            return (
              <li
                key={phase.id}
                className={`upcoming-phase-item ${allDiscoveryComplete ? 'ready' : ''}`}
                role="listitem"
              >
                <div className="upcoming-phase-icon" aria-hidden="true">
                  {allDiscoveryComplete ? <Icon size={16} /> : <Lock size={14} />}
                </div>
                <span className="upcoming-phase-name">
                  {phase.name}
                  <span className="sr-only">
                    {allDiscoveryComplete ? ' - ready to unlock' : ' - locked, complete Discovery first'}
                  </span>
                </span>
              </li>
            );
          })}
        </ul>
      </div>

      <style>{`
        .sr-only {
          position: absolute;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          overflow: hidden;
          clip: rect(0, 0, 0, 0);
          white-space: nowrap;
          border: 0;
        }

        .stage-progress-container {
          background: var(--v4-surface, white);
          border-radius: 12px;
          border: 1px solid var(--v4-border, #e5e7eb);
          overflow: hidden;
        }

        .stage-progress-header {
          padding: 16px 20px;
          border-bottom: 1px solid var(--v4-border, #e5e7eb);
        }

        .stage-progress-header h2,
        .stage-progress-header h3 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--v4-text, #1a1a2e);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .stage-progress-list {
          display: flex;
          flex-direction: column;
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .stage-progress-list > li {
          margin: 0;
          padding: 0;
        }

        .stage-item {
          position: relative;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px 20px;
          background: none;
          border: none;
          border-bottom: 1px solid var(--v4-border, #e5e7eb);
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
        }

        .stage-item:last-child {
          border-bottom: none;
        }

        .stage-item:hover:not(.locked) {
          background: var(--v4-bg, #f9fafb);
        }

        .stage-item:focus {
          outline: 2px solid var(--v4-accent, #c2410c);
          outline-offset: -2px;
          z-index: 1;
        }

        .stage-item.active {
          background: color-mix(in srgb, var(--stage-color) 8%, white);
        }

        .stage-item.locked {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .stage-connector {
          position: absolute;
          left: 30px;
          top: -8px;
          width: 2px;
          height: 16px;
          background: var(--v4-border, #e5e7eb);
        }

        .stage-item.complete .stage-connector,
        .stage-item.in-progress .stage-connector {
          background: var(--stage-color);
        }

        .stage-icon {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background: var(--v4-bg, #f3f4f6);
          color: var(--v4-text-secondary, #6b7280);
          flex-shrink: 0;
        }

        .stage-item.active .stage-icon {
          background: var(--stage-color);
          color: white;
        }

        .stage-item.complete .stage-icon {
          background: var(--stage-color);
          color: white;
        }

        .stage-item.in-progress .stage-icon {
          background: color-mix(in srgb, var(--stage-color) 20%, white);
          color: var(--stage-color);
        }

        .stage-item.skipped .stage-icon {
          background: var(--v4-bg, #f3f4f6);
          color: var(--v4-text-muted, #9ca3af);
        }

        .stage-info {
          flex: 1;
          min-width: 0;
        }

        .stage-name {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: var(--v4-text, #1a1a2e);
        }

        .stage-item.skipped .stage-name {
          text-decoration: line-through;
          color: var(--v4-text-muted, #9ca3af);
        }

        .stage-description {
          display: block;
          font-size: 12px;
          color: var(--v4-text-secondary, #6b7280);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .stage-score {
          padding: 4px 8px;
          background: var(--stage-color);
          color: white;
          font-size: 11px;
          font-weight: 600;
          border-radius: 12px;
        }

        .spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @media (max-width: 768px) {
          .stage-description {
            display: none;
          }
        }

        /* Upcoming Phases Section */
        .upcoming-phases-section {
          border-top: 1px solid var(--v4-border, #e5e7eb);
          padding: 16px 20px;
          background: var(--v4-bg, #f9fafb);
        }

        .upcoming-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }

        .upcoming-header h3,
        .upcoming-header h4 {
          margin: 0;
          font-size: 12px;
          font-weight: 600;
          color: var(--v4-text-muted, #9ca3af);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .upcoming-header .lock-icon {
          color: var(--v4-text-muted, #9ca3af);
        }

        .upcoming-phases-list {
          display: flex;
          flex-direction: column;
          gap: 4px;
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .upcoming-phases-list > li {
          margin: 0;
          padding: 0;
        }

        .upcoming-phase-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 10px;
          border-radius: 6px;
          opacity: 0.6;
          transition: all 0.2s ease;
        }

        .upcoming-phase-item.ready {
          opacity: 0.8;
        }

        .upcoming-phase-item:hover {
          background: rgba(0, 0, 0, 0.03);
        }

        .upcoming-phase-icon {
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background: var(--v4-surface, white);
          border: 1px dashed var(--v4-border, #e5e7eb);
          color: var(--v4-text-muted, #9ca3af);
        }

        .upcoming-phase-item.ready .upcoming-phase-icon {
          border-color: var(--v4-accent, #c2410c);
          color: var(--v4-accent, #c2410c);
        }

        .upcoming-phase-name {
          font-size: 13px;
          color: var(--v4-text-muted, #9ca3af);
        }

        .upcoming-phase-item.ready .upcoming-phase-name {
          color: var(--v4-text-secondary, #6b7280);
        }
      `}</style>
    </nav>
  );
}

export default StageProgress;
