import { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Play,
  Plus,
  Download,
  ArrowRight,
  RefreshCw,
  Check,
  Edit3,
  Shield,
  Loader2,
  AlertCircle,
  X,
} from 'lucide-react';
import { useDiscoveryV4, type Interview } from '../../../hooks/useDiscoveryV4';
import StageProgress from './StageProgress';
import InterviewForm from './InterviewForm';
import CoachingPanel from './CoachingPanel';
import {
  ProblemLoveRenderer,
  CustomerTruthRenderer,
  OpportunityMappingRenderer,
  SolutionDesignRenderer,
  ValidationPlanRenderer,
} from './renderers';

interface DiscoveryViewV4Props {
  sessionId: string;
  onBack?: () => void;
  onComplete?: (pack: Record<string, unknown>) => void;
  onContinueToExecution?: (sessionId: string) => void;
}

// Evidence quality badge component
function EvidenceBadge({ quality }: { quality: string }) {
  const colors: Record<string, { bg: string; text: string; label: string }> = {
    E1: { bg: '#dcfce7', text: '#166534', label: 'E1 - Direct Evidence' },
    E2: { bg: '#dbeafe', text: '#1e40af', label: 'E2 - Survey Data' },
    E3: { bg: '#fef3c7', text: '#92400e', label: 'E3 - Expert Analysis' },
    E4: { bg: '#f3f4f6', text: '#6b7280', label: 'E4 - AI Generated' },
  };
  const style = colors[quality] || colors.E4;

  return (
    <span
      className="evidence-badge"
      style={{
        background: style.bg,
        color: style.text,
        padding: '4px 10px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 500,
      }}
    >
      <Shield size={12} style={{ marginRight: 4, verticalAlign: -1 }} />
      {style.label}
    </span>
  );
}

// Quality score component
function QualityScoreBadge({
  score,
  evidence,
}: {
  score: number;
  evidence: string;
}) {
  return (
    <div className="quality-badge">
      <span className="score">{score}%</span>
      <EvidenceBadge quality={evidence} />
    </div>
  );
}

// Render stage output with appropriate renderer
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function renderStageOutput(stage: string, output: Record<string, unknown>) {
  // Cast to any to allow passing to renderers - they handle optional fields gracefully
  const outputData = output as any;

  switch (stage) {
    case 'problem_love':
      return <ProblemLoveRenderer output={outputData} />;
    case 'customer_truth':
      return <CustomerTruthRenderer output={outputData} />;
    case 'opportunity_mapping':
      return <OpportunityMappingRenderer output={outputData} />;
    case 'solution_design':
      return <SolutionDesignRenderer output={outputData} />;
    case 'validation_plan':
      return <ValidationPlanRenderer output={outputData} />;
    default:
      // Fallback to formatted JSON for unknown stages
      return <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{JSON.stringify(output, null, 2)}</pre>;
  }
}

// Stage content renderer
function StageContent({
  stage,
  stageState,
  onRunStage,
  isLoading,
  isEditing,
  editingOutput,
  onStartEdit,
  onSaveEdit,
  onCancelEdit,
  onUpdateField,
}: {
  stage: string;
  stageState: {
    status: string;
    output?: Record<string, unknown>;
    score?: number;
    coaching_messages?: string[];
    error_message?: string;
    last_error_at?: string;
    started_at?: string;
  };
  onRunStage: () => void;
  isLoading: boolean;
  isEditing: boolean;
  editingOutput: Record<string, unknown> | null;
  onStartEdit: () => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  onUpdateField: (field: string, value: unknown) => void;
}) {
  const hasOutput = stageState.output && Object.keys(stageState.output).length > 0;

  // Check for timeout (2 minutes = 120 seconds)
  const TIMEOUT_MS = 120000;
  const isTimedOut = stageState.status === 'in_progress' && stageState.started_at &&
    (Date.now() - new Date(stageState.started_at).getTime() > TIMEOUT_MS);

  // Show error state if stage failed
  if (stageState.error_message) {
    return (
      <div className="stage-error">
        <AlertCircle size={32} />
        <h3>Stage Failed</h3>
        <p className="error-message">{stageState.error_message}</p>
        {stageState.last_error_at && (
          <p className="error-time">Failed at: {new Date(stageState.last_error_at).toLocaleString()}</p>
        )}
        <button className="retry-btn" onClick={onRunStage} disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 size={18} className="spin" /> Retrying...
            </>
          ) : (
            <>
              <RefreshCw size={18} /> Retry Stage
            </>
          )}
        </button>
      </div>
    );
  }

  if (stageState.status === 'not_started') {
    return (
      <div className="stage-empty">
        <h3>Ready to Start</h3>
        <p>Click the button below to run AI analysis for this stage.</p>
        <button className="run-stage-btn" onClick={onRunStage} disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 size={18} className="spin" /> Running...
            </>
          ) : (
            <>
              <Play size={18} /> Run {stage.replace(/_/g, ' ')}
            </>
          )}
        </button>
      </div>
    );
  }

  if (stageState.status === 'in_progress') {
    // Show timeout error if stage has been running too long
    if (isTimedOut) {
      return (
        <div className="stage-error">
          <AlertCircle size={32} />
          <h3>Stage Timed Out</h3>
          <p className="error-message">The AI analysis took too long. This may be due to high server load.</p>
          <button className="retry-btn" onClick={onRunStage} disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 size={18} className="spin" /> Retrying...
              </>
            ) : (
              <>
                <RefreshCw size={18} /> Retry Stage
              </>
            )}
          </button>
        </div>
      );
    }

    return (
      <div className="stage-loading">
        <Loader2 size={32} className="spin" />
        <h3>Analyzing...</h3>
        <p>AI is working on this stage. This usually takes 30-60 seconds.</p>
      </div>
    );
  }

  if (hasOutput) {
    // Edit mode - show JSON editor
    if (isEditing && editingOutput) {
      return (
        <div className="stage-output editing">
          <div className="output-header">
            <h3>Editing: {stage.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</h3>
            <div className="output-actions">
              <button className="icon-btn cancel-edit" onClick={onCancelEdit} title="Cancel">
                <X size={16} />
              </button>
            </div>
          </div>
          <p className="edit-hint">Edit the JSON below. Changes are saved when you click Save.</p>
          <div className="json-editor-container">
            <textarea
              className="json-editor"
              value={JSON.stringify(editingOutput, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  onUpdateField('_full', parsed);
                } catch {
                  // Invalid JSON, keep the raw text
                }
              }}
              rows={20}
            />
          </div>
          <div className="edit-actions">
            <button className="secondary-btn" onClick={onCancelEdit}>
              Cancel
            </button>
            <button className="primary-btn" onClick={onSaveEdit}>
              <Check size={16} /> Save Changes
            </button>
          </div>
        </div>
      );
    }

    // View mode - use stage-specific renderer
    return (
      <div className="stage-output">
        <div className="output-header">
          <h3>{stage.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</h3>
          <div className="output-actions">
            <button className="icon-btn" onClick={onRunStage} title="Regenerate" disabled={isLoading}>
              <RefreshCw size={16} />
            </button>
            <button className="icon-btn" onClick={onStartEdit} title="Edit">
              <Edit3 size={16} />
            </button>
          </div>
        </div>

        <div className="output-content">
          {renderStageOutput(stage, stageState.output!)}
        </div>

        {stageState.score && (
          <div className="output-score">
            Stage Score: <strong>{stageState.score}/10</strong>
          </div>
        )}
      </div>
    );
  }

  return null;
}

// Convert V4 session to InceptionPack format for PackViewer
interface DiscoveryPack {
  metadata: {
    session_id: string;
    product_idea: string;
    mode: string;
    evidence_quality: string;
    created_at: string;
  };
  discovery: {
    problem_love?: Record<string, unknown>;
    customer_truth?: Record<string, unknown>;
    opportunity_mapping?: Record<string, unknown>;
    solution_design?: Record<string, unknown>;
    validation_plan?: Record<string, unknown>;
  };
  interviews: unknown[];
  patterns?: unknown;
  quality_score: number;
}

function convertV4SessionToPack(session: {
  session_id: string;
  product_idea: string;
  mode: string;
  overall_evidence_quality: string;
  created_at: string;
  quality_score: number;
  stages: Record<string, { output?: Record<string, unknown> }>;
  interviews: unknown[];
  patterns?: unknown;
}): DiscoveryPack {
  return {
    metadata: {
      session_id: session.session_id,
      product_idea: session.product_idea,
      mode: session.mode,
      evidence_quality: session.overall_evidence_quality,
      created_at: session.created_at,
    },
    discovery: {
      problem_love: session.stages.problem_love?.output,
      customer_truth: session.stages.customer_truth?.output,
      opportunity_mapping: session.stages.opportunity_mapping?.output,
      solution_design: session.stages.solution_design?.output,
      validation_plan: session.stages.validation_plan?.output,
    },
    interviews: session.interviews,
    patterns: session.patterns,
    quality_score: session.quality_score,
  };
}

export function DiscoveryViewV4({
  sessionId,
  onBack,
  onComplete,
  onContinueToExecution,
}: DiscoveryViewV4Props) {
  const {
    session,
    loading,
    error,
    runStage,
    saveStageOutput,
    approveStage,
    addInterview,
    synthesizeInterviews,
    continueToStrategy,
    refetch,
  } = useDiscoveryV4(sessionId);

  const [activeStage, setActiveStage] = useState<string>('problem_love');
  const [showInterviewForm, setShowInterviewForm] = useState(false);
  const [stageLoading, setStageLoading] = useState<string | null>(null);
  const [lifecycleLoading, setLifecycleLoading] = useState(false);
  const [lifecycleError, setLifecycleError] = useState<string | null>(null);
  const [coaching, setCoaching] = useState<{
    messages: Array<{ type: 'suggestion' | 'warning' | 'tip' | 'question'; content: string }>;
    suggestion?: string;
  } | null>(null);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editingOutput, setEditingOutput] = useState<Record<string, unknown> | null>(null);

  // Edit mode handlers
  const handleStartEdit = () => {
    const currentOutput = session?.stages[activeStage]?.output;
    if (currentOutput) {
      setEditingOutput({ ...currentOutput });
      setIsEditing(true);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingOutput) return;
    try {
      await saveStageOutput(activeStage, editingOutput);
      setIsEditing(false);
      setEditingOutput(null);
    } catch (err) {
      console.error('Failed to save stage output:', err);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditingOutput(null);
  };

  const handleUpdateField = (field: string, value: unknown) => {
    if (field === '_full') {
      // Full JSON replacement
      setEditingOutput(value as Record<string, unknown>);
    } else {
      setEditingOutput((prev) => (prev ? { ...prev, [field]: value } : null));
    }
  };

  // Set initial active stage based on session progress
  useEffect(() => {
    if (session) {
      // Find first incomplete stage
      const stages = ['problem_love', 'customer_truth', 'opportunity_mapping', 'solution_design', 'validation_plan'];
      for (const stage of stages) {
        const state = session.stages[stage];
        if (state.status !== 'completed' && state.status !== 'approved' && state.status !== 'skipped') {
          setActiveStage(stage);
          break;
        }
      }
    }
  }, [session?.session_id]);

  if (loading) {
    return (
      <div className="discovery-loading">
        <Loader2 size={48} className="spin" />
        <p>Loading discovery session...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="discovery-error">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={onBack}>Go Back</button>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="discovery-error">
        <h2>Session Not Found</h2>
        <p>The discovery session could not be found.</p>
        <button onClick={onBack}>Go Back</button>
      </div>
    );
  }

  const currentStage = session.stages[activeStage];
  const isQuickMode = session.mode === 'quick';
  const isDeepMode = session.mode === 'deep';

  const handleRunStage = async () => {
    setStageLoading(activeStage);
    try {
      await runStage(activeStage);
    } finally {
      setStageLoading(null);
    }
  };

  const handleApproveStage = async () => {
    const result = await approveStage(activeStage);
    if (result?.next_stage) {
      setActiveStage(result.next_stage);
    }
  };

  const handleAddInterview = async (interview: Interview) => {
    await addInterview(interview);
    setShowInterviewForm(false);
  };

  const handleContinueToStrategy = async () => {
    if (!session) return;

    // If we have an execution callback, use it to transition to ExecutionView with SSE
    if (onContinueToExecution) {
      setLifecycleLoading(true);
      try {
        // Start the full lifecycle in the backend
        await continueToStrategy();
        // Transition to ExecutionView which will handle SSE streaming
        onContinueToExecution(sessionId);
      } catch (err) {
        setLifecycleError(err instanceof Error ? err.message : 'Failed to start lifecycle');
        setLifecycleLoading(false);
      }
      return;
    }

    // Fallback: Convert V4 session to pack format (for backwards compatibility)
    setLifecycleLoading(true);
    setLifecycleError(null);

    try {
      await continueToStrategy();
      const pack = convertV4SessionToPack(session);
      onComplete?.(pack as unknown as Record<string, unknown>);
    } catch (err) {
      setLifecycleError(err instanceof Error ? err.message : 'Failed to generate full lifecycle');
    } finally {
      setLifecycleLoading(false);
    }
  };

  // Calculate overall progress
  const stagesComplete = Object.values(session.stages).filter(
    (s) => s.status === 'completed' || s.status === 'approved' || s.status === 'skipped'
  ).length;
  const totalStages = Object.keys(session.stages).length;
  const progressPercent = Math.round((stagesComplete / totalStages) * 100);

  return (
    <div className="discovery-view-v4">
      {/* Header */}
      <header className="discovery-header">
        <div className="header-left">
          {onBack && (
            <button className="back-btn" onClick={onBack}>
              <ArrowLeft size={20} />
            </button>
          )}
          <div className="header-titles">
            <h1>Discovery</h1>
            <p className="product-idea">
              {session.product_idea.slice(0, 60)}
              {session.product_idea.length > 60 ? '...' : ''}
            </p>
          </div>
        </div>
        <div className="header-right">
          <span className={`mode-badge mode-${session.mode}`}>
            {session.mode} mode
          </span>
          <QualityScoreBadge
            score={session.quality_score}
            evidence={session.overall_evidence_quality}
          />
        </div>
      </header>

      {/* Main Layout */}
      <div className="discovery-layout">
        {/* Sidebar */}
        <aside className="discovery-sidebar">
          <StageProgress
            session={session}
            activeStage={activeStage}
            onSelectStage={setActiveStage}
          />

          {/* Interview tracker for Deep mode */}
          {isDeepMode && (
            <div className="interview-tracker">
              <div className="tracker-header">
                <h4>Interviews</h4>
                <span className="interview-count">
                  {session.interviews.length} / 5 goal
                </span>
              </div>
              <div className="interview-progress">
                <div
                  className="interview-progress-bar"
                  style={{
                    width: `${Math.min((session.interviews.length / 5) * 100, 100)}%`,
                  }}
                />
              </div>
              <button
                className="add-interview-btn"
                onClick={() => setShowInterviewForm(true)}
              >
                <Plus size={16} />
                Add Interview
              </button>
              {session.interviews.length >= 2 && (
                <button
                  className="synthesize-btn"
                  onClick={synthesizeInterviews}
                >
                  <RefreshCw size={14} />
                  Synthesize Patterns
                </button>
              )}
            </div>
          )}

          {/* Quick actions */}
          <div className="sidebar-actions">
            <button className="action-btn" onClick={() => refetch()}>
              <RefreshCw size={14} /> Refresh
            </button>
            <button className="action-btn">
              <Download size={14} /> Export
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="discovery-main">
          {/* Stage Content */}
          <div className="stage-container">
            <StageContent
              stage={activeStage}
              stageState={currentStage}
              onRunStage={handleRunStage}
              isLoading={stageLoading === activeStage}
              isEditing={isEditing}
              editingOutput={editingOutput}
              onStartEdit={handleStartEdit}
              onSaveEdit={handleSaveEdit}
              onCancelEdit={handleCancelEdit}
              onUpdateField={handleUpdateField}
            />
          </div>

          {/* Coaching Panel */}
          {coaching && (
            <CoachingPanel
              messages={coaching.messages}
              suggestion={coaching.suggestion}
              onApplySuggestion={(_suggestion) => {
                // Apply suggestion logic - TODO: implement suggestion application
                setCoaching(null);
              }}
              onDismiss={() => setCoaching(null)}
            />
          )}

          {/* Checkpoint Controls (for Guided/Deep modes) */}
          {!isQuickMode &&
            !isEditing &&
            (currentStage.status === 'completed' ||
              currentStage.status === 'approved') && (
              <div className="checkpoint-controls">
                <p>Review the output above. Ready to continue?</p>
                <div className="checkpoint-actions">
                  <button className="secondary-btn" onClick={handleStartEdit}>
                    <Edit3 size={16} /> Edit First
                  </button>
                  <button className="primary-btn" onClick={handleApproveStage}>
                    <Check size={16} /> Approve & Continue
                  </button>
                </div>
              </div>
            )}

          {/* Auto-continue indicator (Quick mode) */}
          {isQuickMode && currentStage.status === 'in_progress' && (
            <div className="auto-continue">
              <Loader2 className="spin" />
              <p>Generating... Will continue automatically</p>
            </div>
          )}

          {/* Discovery Complete */}
          {progressPercent === 100 && (
            <div className="discovery-complete">
              <h3>Discovery Complete!</h3>
              <p>
                All stages are complete. You can now continue to full lifecycle
                generation.
              </p>
              {lifecycleError && (
                <div className="lifecycle-error">
                  <AlertCircle size={16} />
                  <span>{lifecycleError}</span>
                </div>
              )}
              <button
                className="continue-strategy-btn"
                onClick={handleContinueToStrategy}
                disabled={lifecycleLoading}
              >
                {lifecycleLoading ? (
                  <>
                    <Loader2 size={18} className="spin" />
                    Generating Lifecycle...
                  </>
                ) : (
                  <>
                    Continue to Strategy & Delivery
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </div>
          )}
        </main>
      </div>

      {/* Interview Form Modal */}
      {showInterviewForm && (
        <InterviewForm
          onSave={handleAddInterview}
          onCancel={() => setShowInterviewForm(false)}
        />
      )}

      <style>{`
        .discovery-view-v4 {
          min-height: 100vh;
          background: var(--bg-primary, #f9fafb);
        }

        .discovery-loading,
        .discovery-error {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 60vh;
          gap: 16px;
        }

        .discovery-loading p,
        .discovery-error p {
          color: var(--text-secondary, #6b7280);
        }

        .spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        /* Header */
        .discovery-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 24px;
          background: white;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .back-btn {
          padding: 8px;
          background: none;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          color: var(--text-secondary, #6b7280);
          transition: all 0.2s;
        }

        .back-btn:hover {
          background: var(--bg-hover, #f3f4f6);
          color: var(--text-primary, #1a1a2e);
        }

        .header-titles h1 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        .product-idea {
          margin: 2px 0 0;
          font-size: 13px;
          color: var(--text-secondary, #6b7280);
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .mode-badge {
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 500;
          text-transform: capitalize;
        }

        .mode-quick {
          background: #dcfce7;
          color: #166534;
        }

        .mode-guided {
          background: #dbeafe;
          color: #1e40af;
        }

        .mode-deep {
          background: #f3e8ff;
          color: #7c3aed;
        }

        .quality-badge {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .quality-badge .score {
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        /* Layout */
        .discovery-layout {
          display: grid;
          grid-template-columns: 300px 1fr;
          gap: 24px;
          padding: 24px;
          max-width: 1400px;
          margin: 0 auto;
        }

        /* Sidebar */
        .discovery-sidebar {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .interview-tracker {
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 12px;
          padding: 16px;
        }

        .tracker-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .tracker-header h4 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        .interview-count {
          font-size: 13px;
          color: var(--text-secondary, #6b7280);
        }

        .interview-progress {
          height: 6px;
          background: var(--bg-secondary, #f3f4f6);
          border-radius: 3px;
          margin-bottom: 12px;
          overflow: hidden;
        }

        .interview-progress-bar {
          height: 100%;
          background: var(--primary, #3b82f6);
          border-radius: 3px;
          transition: width 0.3s ease;
        }

        .add-interview-btn,
        .synthesize-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          width: 100%;
          padding: 10px;
          border-radius: 8px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .add-interview-btn {
          background: var(--primary, #3b82f6);
          border: none;
          color: white;
          margin-bottom: 8px;
        }

        .add-interview-btn:hover {
          background: var(--primary-dark, #2563eb);
        }

        .synthesize-btn {
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          color: var(--text-secondary, #6b7280);
        }

        .synthesize-btn:hover {
          background: var(--bg-hover, #f3f4f6);
        }

        .sidebar-actions {
          display: flex;
          gap: 8px;
        }

        .action-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          padding: 8px;
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 8px;
          font-size: 12px;
          color: var(--text-secondary, #6b7280);
          cursor: pointer;
          transition: all 0.2s;
        }

        .action-btn:hover {
          background: var(--bg-hover, #f3f4f6);
        }

        /* Main */
        .discovery-main {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .stage-container {
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 12px;
          padding: 24px;
          min-height: 400px;
        }

        .stage-empty,
        .stage-loading,
        .stage-error {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 60px 20px;
        }

        .stage-empty h3,
        .stage-loading h3,
        .stage-error h3 {
          margin: 0 0 8px 0;
          font-size: 18px;
          color: var(--text-primary, #1a1a2e);
        }

        .stage-empty p,
        .stage-loading p,
        .stage-error p {
          margin: 0 0 24px 0;
          color: var(--text-secondary, #6b7280);
        }

        .stage-error {
          background: #fef2f2;
          border-radius: 12px;
        }

        .stage-error h3 {
          color: #b91c1c;
        }

        .stage-error .error-message {
          color: #dc2626;
          max-width: 400px;
          word-break: break-word;
        }

        .stage-error .error-time {
          font-size: 12px;
          color: #9ca3af;
        }

        .stage-error .retry-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          background: #dc2626;
          border: none;
          border-radius: 8px;
          color: white;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .stage-error .retry-btn:hover:not(:disabled) {
          background: #b91c1c;
        }

        .stage-error .retry-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .lifecycle-error {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 8px;
          color: #dc2626;
          font-size: 14px;
          margin-bottom: 16px;
        }

        .run-stage-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 24px;
          background: var(--primary, #3b82f6);
          border: none;
          border-radius: 10px;
          font-size: 15px;
          font-weight: 500;
          color: white;
          cursor: pointer;
          transition: all 0.2s;
        }

        .run-stage-btn:hover:not(:disabled) {
          background: var(--primary-dark, #2563eb);
          transform: translateY(-1px);
        }

        .run-stage-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .stage-output {
          max-height: 600px;
          overflow-y: auto;
        }

        .stage-output .output-content {
          padding: 0;
          background: transparent;
        }

        .output-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .output-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        .output-actions {
          display: flex;
          gap: 8px;
        }

        .icon-btn {
          padding: 8px;
          background: none;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 6px;
          cursor: pointer;
          color: var(--text-secondary, #6b7280);
          transition: all 0.2s;
        }

        .icon-btn:hover {
          background: var(--bg-hover, #f3f4f6);
          color: var(--text-primary, #1a1a2e);
        }

        .output-content {
          padding: 16px;
          background: var(--bg-secondary, #f9fafb);
          border-radius: 8px;
          overflow-x: auto;
        }

        .output-content pre {
          margin: 0;
          font-size: 13px;
          line-height: 1.5;
          white-space: pre-wrap;
          word-break: break-word;
        }

        /* Edit mode styles */
        .stage-output.editing {
          max-height: none;
        }

        .edit-hint {
          margin: 0 0 12px 0;
          font-size: 13px;
          color: var(--text-secondary, #6b7280);
        }

        .json-editor-container {
          margin-bottom: 16px;
        }

        .json-editor {
          width: 100%;
          min-height: 300px;
          padding: 12px;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 13px;
          line-height: 1.5;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 8px;
          background: var(--bg-secondary, #f9fafb);
          resize: vertical;
        }

        .json-editor:focus {
          outline: none;
          border-color: var(--primary, #3b82f6);
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .edit-actions {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
          padding-top: 16px;
          border-top: 1px solid var(--border-color, #e5e7eb);
        }

        .cancel-edit {
          color: var(--text-error, #dc2626) !important;
          border-color: var(--text-error, #dc2626) !important;
        }

        .cancel-edit:hover {
          background: #fef2f2 !important;
        }

        .output-score {
          margin-top: 16px;
          padding: 12px 16px;
          background: var(--bg-success, #dcfce7);
          border-radius: 8px;
          font-size: 14px;
          color: var(--text-success, #166534);
        }

        /* Checkpoint Controls */
        .checkpoint-controls {
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 12px;
          padding: 20px 24px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .checkpoint-controls p {
          margin: 0;
          color: var(--text-secondary, #6b7280);
        }

        .checkpoint-actions {
          display: flex;
          gap: 12px;
        }

        .primary-btn,
        .secondary-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 18px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .primary-btn {
          background: var(--primary, #3b82f6);
          border: none;
          color: white;
        }

        .primary-btn:hover {
          background: var(--primary-dark, #2563eb);
        }

        .secondary-btn {
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          color: var(--text-secondary, #6b7280);
        }

        .secondary-btn:hover {
          background: var(--bg-hover, #f3f4f6);
        }

        /* Auto Continue */
        .auto-continue {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          padding: 16px;
          background: var(--bg-info, #eff6ff);
          border: 1px solid #bfdbfe;
          border-radius: 12px;
          color: var(--text-info, #1d4ed8);
        }

        .auto-continue p {
          margin: 0;
          font-size: 14px;
        }

        /* Discovery Complete */
        .discovery-complete {
          background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
          border: 1px solid #86efac;
          border-radius: 12px;
          padding: 24px;
          text-align: center;
        }

        .discovery-complete h3 {
          margin: 0 0 8px 0;
          font-size: 18px;
          color: #166534;
        }

        .discovery-complete p {
          margin: 0 0 20px 0;
          color: #15803d;
        }

        .continue-strategy-btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 12px 24px;
          background: #166534;
          border: none;
          border-radius: 10px;
          font-size: 15px;
          font-weight: 500;
          color: white;
          cursor: pointer;
          transition: all 0.2s;
        }

        .continue-strategy-btn:hover {
          background: #15803d;
          transform: translateY(-1px);
        }

        /* Responsive */
        @media (max-width: 900px) {
          .discovery-layout {
            grid-template-columns: 1fr;
          }

          .discovery-sidebar {
            order: 2;
          }

          .discovery-main {
            order: 1;
          }
        }

        @media (max-width: 600px) {
          .discovery-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .header-right {
            width: 100%;
            justify-content: space-between;
          }

          .checkpoint-controls {
            flex-direction: column;
            gap: 16px;
            text-align: center;
          }
        }
      `}</style>
    </div>
  );
}

export default DiscoveryViewV4;
