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
    color: '#3b82f6', // blue
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

  return (
    <div className="stage-progress-container">
      <div className="stage-progress-header">
        <h3>Discovery Progress</h3>
      </div>

      <div className="stage-progress-list">
        {DISCOVERY_STAGES.map((stage, idx) => {
          const state = session.stages[stage.id] || { status: 'not_started' };
          const isActive = activeStage === stage.id;
          const isComplete = state.status === 'completed' || state.status === 'approved';
          const isInProgress = state.status === 'in_progress';
          const isSkipped = state.status === 'skipped';
          const isClickable = isStageClickable(stage.id, idx);
          const Icon = stage.icon;

          return (
            <button
              key={stage.id}
              className={`stage-item ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''} ${isInProgress ? 'in-progress' : ''} ${isSkipped ? 'skipped' : ''} ${!isClickable ? 'locked' : ''}`}
              onClick={() => isClickable && onSelectStage?.(stage.id)}
              disabled={!isClickable}
              style={{ '--stage-color': stage.color } as React.CSSProperties}
            >
              {idx > 0 && <div className="stage-connector" />}

              <div className="stage-icon">
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
                <span className="stage-score">{state.score}/10</span>
              )}
            </button>
          );
        })}
      </div>

      <style>{`
        .stage-progress-container {
          background: white;
          border-radius: 12px;
          border: 1px solid var(--border-color, #e5e7eb);
          overflow: hidden;
        }

        .stage-progress-header {
          padding: 16px 20px;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
        }

        .stage-progress-header h3 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .stage-progress-list {
          display: flex;
          flex-direction: column;
        }

        .stage-item {
          position: relative;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px 20px;
          background: none;
          border: none;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
        }

        .stage-item:last-child {
          border-bottom: none;
        }

        .stage-item:hover:not(.locked) {
          background: var(--bg-hover, #f9fafb);
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
          background: var(--border-color, #e5e7eb);
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
          background: var(--bg-secondary, #f3f4f6);
          color: var(--text-secondary, #6b7280);
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
          background: var(--bg-secondary, #f3f4f6);
          color: var(--text-muted, #9ca3af);
        }

        .stage-info {
          flex: 1;
          min-width: 0;
        }

        .stage-name {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary, #1a1a2e);
        }

        .stage-item.skipped .stage-name {
          text-decoration: line-through;
          color: var(--text-muted, #9ca3af);
        }

        .stage-description {
          display: block;
          font-size: 12px;
          color: var(--text-secondary, #6b7280);
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
      `}</style>
    </div>
  );
}

export default StageProgress;
