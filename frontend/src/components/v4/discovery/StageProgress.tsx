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
    color: 'var(--v4-error, #dc2626)',
  },
  {
    id: 'customer_truth',
    name: 'Customer Truth',
    shortName: 'Customers',
    icon: Users,
    description: 'Understand real customer needs',
    color: 'var(--v4-warning, #ca8a04)',
  },
  {
    id: 'opportunity_mapping',
    name: 'Opportunity Map',
    shortName: 'Opportunities',
    icon: Map,
    description: 'Map opportunities to solutions',
    color: 'var(--v4-success, #16a34a)',
  },
  {
    id: 'solution_design',
    name: 'Solution Design',
    shortName: 'Solution',
    icon: Lightbulb,
    description: 'Design and evaluate the solution',
    color: 'var(--v4-accent, #c2410c)',
  },
  {
    id: 'validation_plan',
    name: 'Validation Plan',
    shortName: 'Validation',
    icon: CheckCircle,
    description: 'Plan validation experiments',
    color: 'var(--v4-info, #2563eb)',
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

  // Calculate completion stats
  const completedStages = DISCOVERY_STAGES.filter((stage) => {
    const state = session.stages[stage.id];
    return state?.status === 'completed' || state?.status === 'approved';
  }).length;

  const progressPercentage = Math.round((completedStages / DISCOVERY_STAGES.length) * 100);

  return (
    <div className="stage-progress-container">
      {/* Progress Summary */}
      <div className="sp-progress">
        <div className="sp-progress-header">
          <span className="sp-progress-label">Discovery Progress</span>
          <span className="sp-progress-value">{progressPercentage}%</span>
        </div>
        <div className="sp-progress-bar">
          <div
            className="sp-progress-fill"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <div className="sp-progress-count">
          {completedStages} of {DISCOVERY_STAGES.length} stages complete
        </div>
      </div>

      {/* Stage Header */}
      <div className="sp-section-header">
        <span className="sp-section-label">Discovery</span>
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
              <div className="stage-icon">
                {isComplete ? (
                  <Check size={16} />
                ) : isInProgress ? (
                  <Loader2 size={16} className="spin" />
                ) : !isClickable ? (
                  <Lock size={14} />
                ) : (
                  <Icon size={16} />
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

      {/* Upcoming Phases Preview */}
      <div className="upcoming-phases-section">
        <div className="sp-section-header upcoming">
          <span className="sp-section-label">Coming Up</span>
          <Lock size={12} className="lock-icon" />
        </div>
        <div className="upcoming-phases-list">
          {UPCOMING_PHASES.map((phase) => {
            const Icon = phase.icon;
            return (
              <div
                key={phase.id}
                className={`upcoming-phase-item ${allDiscoveryComplete ? 'ready' : ''}`}
                title={allDiscoveryComplete ? 'Complete Discovery to unlock' : 'Locked - complete Discovery first'}
              >
                <div className="upcoming-phase-icon">
                  {allDiscoveryComplete ? <Icon size={14} /> : <Lock size={12} />}
                </div>
                <span className="upcoming-phase-name">{phase.name}</span>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        .stage-progress-container {
          background: var(--v4-surface, white);
        }

        /* Progress Section */
        .sp-progress {
          padding: 16px 20px;
          border-bottom: 1px solid var(--v4-border-subtle, #ebebeb);
        }

        .sp-progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .sp-progress-label {
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--v4-text-muted, #a3a3a3);
        }

        .sp-progress-value {
          font-size: 13px;
          font-weight: 600;
          color: var(--v4-text, #171717);
          font-family: var(--v4-font-display, 'Plus Jakarta Sans', sans-serif);
        }

        .sp-progress-bar {
          height: 4px;
          background: var(--v4-bg-subtle, #f5f5f5);
          border-radius: 2px;
          overflow: hidden;
        }

        .sp-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--v4-success, #16a34a), var(--v4-success, #16a34a));
          border-radius: 2px;
          transition: width 0.5s ease;
        }

        .sp-progress-count {
          font-size: 11px;
          color: var(--v4-text-muted, #a3a3a3);
          margin-top: 6px;
        }

        /* Section Header */
        .sp-section-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 20px;
          background: var(--v4-bg-subtle, #f5f5f5);
          border-bottom: 1px solid var(--v4-border-subtle, #ebebeb);
        }

        .sp-section-header.upcoming {
          background: var(--v4-bg, #fafafa);
          border-top: 1px solid var(--v4-border-subtle, #ebebeb);
        }

        .sp-section-label {
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: var(--v4-text-muted, #a3a3a3);
        }

        .sp-section-header .lock-icon {
          color: var(--v4-text-muted, #a3a3a3);
        }

        /* Stage List */
        .stage-progress-list {
          display: flex;
          flex-direction: column;
        }

        .stage-item {
          position: relative;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 20px;
          background: none;
          border: none;
          border-bottom: 1px solid var(--v4-border-subtle, #ebebeb);
          border-left: 3px solid transparent;
          cursor: pointer;
          transition: all 0.15s ease;
          text-align: left;
        }

        .stage-item:last-child {
          border-bottom: none;
        }

        .stage-item:hover:not(.locked) {
          background: var(--v4-bg-subtle, #f5f5f5);
        }

        .stage-item.active {
          background: rgba(194, 65, 12, 0.06);
          border-left-color: var(--v4-accent, #c2410c);
        }

        .stage-item.locked {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .stage-icon {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background: var(--v4-bg-subtle, #f5f5f5);
          color: var(--v4-text-muted, #a3a3a3);
          flex-shrink: 0;
          transition: all 0.15s ease;
        }

        .stage-item.active .stage-icon {
          background: var(--v4-accent, #c2410c);
          color: white;
        }

        .stage-item.complete .stage-icon {
          background: var(--v4-success, #16a34a);
          color: white;
        }

        .stage-item.in-progress .stage-icon {
          background: var(--v4-accent-light, rgba(194, 65, 12, 0.08));
          color: var(--v4-accent, #c2410c);
        }

        .stage-item.skipped .stage-icon {
          background: var(--v4-bg-subtle, #f5f5f5);
          color: var(--v4-text-muted, #a3a3a3);
        }

        .stage-info {
          flex: 1;
          min-width: 0;
        }

        .stage-name {
          display: block;
          font-family: var(--v4-font-display, 'Plus Jakarta Sans', sans-serif);
          font-size: 14px;
          font-weight: 500;
          color: var(--v4-text-secondary, #525252);
        }

        .stage-item.active .stage-name {
          color: var(--v4-text, #171717);
          font-weight: 600;
        }

        .stage-item.complete .stage-name {
          color: var(--v4-text, #171717);
        }

        .stage-item.skipped .stage-name {
          text-decoration: line-through;
          color: var(--v4-text-muted, #a3a3a3);
        }

        .stage-description {
          display: block;
          font-size: 12px;
          color: var(--v4-text-muted, #a3a3a3);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-top: 2px;
        }

        .stage-score {
          padding: 4px 10px;
          background: var(--v4-success, #16a34a);
          color: white;
          font-size: 11px;
          font-weight: 600;
          border-radius: 12px;
          flex-shrink: 0;
        }

        .spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        /* Upcoming Phases Section */
        .upcoming-phases-section {
          background: var(--v4-bg, #fafafa);
        }

        .upcoming-phases-list {
          display: flex;
          flex-direction: column;
          padding: 8px 12px;
        }

        .upcoming-phase-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 12px;
          border-radius: 6px;
          opacity: 0.6;
          transition: all 0.15s ease;
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
          border: 1px dashed var(--v4-border, #e5e5e5);
          color: var(--v4-text-muted, #a3a3a3);
          flex-shrink: 0;
        }

        .upcoming-phase-item.ready .upcoming-phase-icon {
          border-color: var(--v4-accent, #c2410c);
          color: var(--v4-accent, #c2410c);
          border-style: solid;
        }

        .upcoming-phase-name {
          font-size: 13px;
          color: var(--v4-text-muted, #a3a3a3);
        }

        .upcoming-phase-item.ready .upcoming-phase-name {
          color: var(--v4-text-secondary, #525252);
        }

        @media (max-width: 768px) {
          .stage-description {
            display: none;
          }

          .stage-item {
            padding: 12px 16px;
          }

          .stage-icon {
            width: 32px;
            height: 32px;
          }
        }
      `}</style>
    </div>
  );
}

export default StageProgress;
