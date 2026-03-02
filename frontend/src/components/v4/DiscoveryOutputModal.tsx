/**
 * DiscoveryOutputModal - Modal to display Discovery V4 stage outputs
 * Used in ExecutionView to show completed Discovery stages
 */

import { X, Heart, Users, Map, Lightbulb, CheckCircle } from 'lucide-react';
import {
  ProblemLoveRenderer,
  CustomerTruthRenderer,
  OpportunityMappingRenderer,
  SolutionDesignRenderer,
  ValidationPlanRenderer,
} from './discovery/renderers';
import type { V4StageOutput } from '../../api/client';

const STAGE_CONFIG: Record<string, { name: string; icon: typeof Heart }> = {
  problem_love: { name: 'Problem Love', icon: Heart },
  customer_truth: { name: 'Customer Truth', icon: Users },
  opportunity_mapping: { name: 'Opportunity Map', icon: Map },
  solution_design: { name: 'Solution Design', icon: Lightbulb },
  validation_plan: { name: 'Validation Plan', icon: CheckCircle },
};

interface DiscoveryOutputModalProps {
  stageId: string;
  stageOutput: V4StageOutput;
  onClose: () => void;
}

export function DiscoveryOutputModal({
  stageId,
  stageOutput,
  onClose,
}: DiscoveryOutputModalProps) {
  const config = STAGE_CONFIG[stageId];
  const Icon = config?.icon || Heart;

  const renderStageOutput = () => {
    if (!stageOutput.output) {
      return (
        <div className="dom-empty">
          <p>No output available for this stage.</p>
        </div>
      );
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const output = stageOutput.output as any;

    switch (stageId) {
      case 'problem_love':
        return <ProblemLoveRenderer output={output} />;
      case 'customer_truth':
        return <CustomerTruthRenderer output={output} />;
      case 'opportunity_mapping':
        return <OpportunityMappingRenderer output={output} />;
      case 'solution_design':
        return <SolutionDesignRenderer output={output} />;
      case 'validation_plan':
        return <ValidationPlanRenderer output={output} />;
      default:
        return (
          <div className="dom-empty">
            <p>Unknown stage: {stageId}</p>
          </div>
        );
    }
  };

  return (
    <div className="dom-overlay" onClick={onClose}>
      <div className="dom-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="dom-header">
          <div className="dom-title">
            <div className="dom-icon">
              <Icon size={18} />
            </div>
            <div>
              <h2>{config?.name || stageId}</h2>
              <span className="dom-subtitle">Discovery Stage Output</span>
            </div>
          </div>
          <button className="dom-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Score badge if available */}
        {stageOutput.score !== undefined && (
          <div className="dom-score-bar">
            <span className="dom-score-label">Stage Score</span>
            <span className="dom-score-value">{stageOutput.score}/10</span>
          </div>
        )}

        {/* Content */}
        <div className="dom-content">{renderStageOutput()}</div>
      </div>

      <style>{`
        .dom-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: dom-fade-in 0.2s ease;
        }

        @keyframes dom-fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .dom-modal {
          background: var(--v4-surface, white);
          border-radius: 12px;
          width: 90%;
          max-width: 800px;
          max-height: 85vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
          animation: dom-slide-up 0.3s ease;
        }

        @keyframes dom-slide-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .dom-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 20px 24px;
          border-bottom: 1px solid var(--v4-border-subtle, #ebebeb);
        }

        .dom-title {
          display: flex;
          align-items: center;
          gap: 14px;
        }

        .dom-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 10px;
          background: var(--v4-accent-lighter, rgba(194, 65, 12, 0.08));
          color: var(--v4-accent, #c2410c);
        }

        .dom-title h2 {
          margin: 0;
          font-family: var(--v4-font-display, 'Plus Jakarta Sans', sans-serif);
          font-size: 18px;
          font-weight: 600;
          color: var(--v4-text, #171717);
        }

        .dom-subtitle {
          font-size: 13px;
          color: var(--v4-text-muted, #a3a3a3);
        }

        .dom-close {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          border: none;
          background: var(--v4-bg-subtle, #f5f5f5);
          border-radius: 8px;
          color: var(--v4-text-secondary, #525252);
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .dom-close:hover {
          background: var(--v4-bg, #fafafa);
          color: var(--v4-text, #171717);
        }

        .dom-score-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 24px;
          background: var(--v4-success-light, rgba(22, 163, 74, 0.08));
          border-bottom: 1px solid var(--v4-border-subtle, #ebebeb);
        }

        .dom-score-label {
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--v4-success, #16a34a);
        }

        .dom-score-value {
          font-family: var(--v4-font-display, 'Plus Jakarta Sans', sans-serif);
          font-size: 16px;
          font-weight: 700;
          color: var(--v4-success, #16a34a);
        }

        .dom-content {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
        }

        .dom-empty {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 200px;
          color: var(--v4-text-muted, #a3a3a3);
        }

        /* Override renderer styles for modal context */
        .dom-content .stage-renderer {
          background: transparent;
          border: none;
          padding: 0;
        }
      `}</style>
    </div>
  );
}

export default DiscoveryOutputModal;
