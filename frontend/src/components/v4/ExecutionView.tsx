/**
 * V4 Execution View Component
 * Real-time agent execution with transparency features
 * Shows unified journey with Discovery as completed phase
 */

import { useEffect, useState, useMemo, useCallback } from 'react';
import { ArrowLeft, Radio, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { useSSEV4 } from '../../hooks/useSSEV4';
import { getInceptionPack, getV4TestInceptionPack, getV4TestSession, type V4DiscoverySession, type V4StageOutput } from '../../api/client';
import { JourneyTimeline, type ExecutionPhase, type DiscoveryStage } from './JourneyTimeline';
import { AgentCard } from './AgentCard';
import { ConstraintFlow } from './ConstraintFlow';
import { RevisionIndicator } from './RevisionIndicator';
import { EvidenceBadge, type EvidenceTier } from './EvidenceBadge';
import { ActivityIndicator } from './ActivityIndicator';
import { MilestoneToast, ProgressMilestoneIndicator } from './MilestoneToast';
import { InsightSkeleton, AgentSkeleton } from './LoadingSkeleton';
import { DiscoveryOutputModal } from './DiscoveryOutputModal';
import type { InceptionPack } from '../../types/api';
import '../../styles/theme-v4.css';

// Phase-specific activity messages
const PHASE_MESSAGES: Record<string, string[]> = {
  planning: [
    'Analyzing domain characteristics...',
    'Identifying key competitors...',
    'Mapping regulatory landscape...',
    'Setting research parameters...',
  ],
  discovery: [
    'Researching total addressable market...',
    'Analyzing customer segments...',
    'Mapping pain points and needs...',
    'Building competitive profiles...',
  ],
  strategy: [
    'Building business model canvas...',
    'Designing go-to-market strategy...',
    'Projecting financial scenarios...',
    'Calculating unit economics...',
  ],
  delivery: [
    'Writing product requirements...',
    'Designing system architecture...',
    'Assessing compliance requirements...',
    'Mapping technical dependencies...',
  ],
  quality: [
    'Validating cross-section consistency...',
    'Checking numerical accuracy...',
    'Calibrating confidence scores...',
    'Running final quality checks...',
  ],
};

interface ExecutionViewV4Props {
  sessionId: string;
  authToken: string;
  onComplete: (pack: InceptionPack) => void;
  onBack: () => void;
  /** If true, uses the V4 test stream endpoint (no auth required) */
  useTestEndpoint?: boolean;
}

export function ExecutionViewV4({ sessionId, authToken, onComplete, onBack, useTestEndpoint = false }: ExecutionViewV4Props) {
  const {
    isConnected,
    currentAgent,
    agentStates,
    insights,
    progress,
    isComplete,
    completionStatus,
    completedPack,
    error,
    currentPhase,
    constraintFlow,
    revisionState,
    phases,
    elapsedTime,
  } = useSSEV4(sessionId, authToken, true, useTestEndpoint);

  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [discoverySession, setDiscoverySession] = useState<V4DiscoverySession | null>(null);
  const [selectedDiscoveryStage, setSelectedDiscoveryStage] = useState<string | null>(null);

  // Fetch Discovery V4 session data on mount
  useEffect(() => {
    if (useTestEndpoint) {
      getV4TestSession(sessionId)
        .then(setDiscoverySession)
        .catch((err) => {
          console.error('Failed to fetch Discovery session:', err);
        });
    }
  }, [sessionId, useTestEndpoint]);

  // Create Discovery stages from fetched session or fallback to completed
  const completedDiscoveryStages: Record<string, DiscoveryStage> = useMemo(() => {
    if (discoverySession?.stages) {
      const stages: Record<string, DiscoveryStage> = {};
      for (const [id, stage] of Object.entries(discoverySession.stages)) {
        stages[id] = {
          id,
          status: stage.status,
          score: stage.score,
        };
      }
      return stages;
    }
    // Fallback if no session data
    return {
      problem_love: { id: 'problem_love', status: 'completed' },
      customer_truth: { id: 'customer_truth', status: 'completed' },
      opportunity_mapping: { id: 'opportunity_mapping', status: 'completed' },
      solution_design: { id: 'solution_design', status: 'completed' },
      validation_plan: { id: 'validation_plan', status: 'completed' },
    };
  }, [discoverySession]);

  // Handle clicking on a Discovery stage
  const handleDiscoveryStageClick = useCallback((stageId: string) => {
    if (discoverySession?.stages?.[stageId]) {
      setSelectedDiscoveryStage(stageId);
    }
  }, [discoverySession]);

  // Get the selected stage output for the modal
  const selectedStageOutput: V4StageOutput | null = useMemo(() => {
    if (selectedDiscoveryStage && discoverySession?.stages?.[selectedDiscoveryStage]) {
      return discoverySession.stages[selectedDiscoveryStage];
    }
    return null;
  }, [selectedDiscoveryStage, discoverySession]);

  // Convert SSE phases to JourneyTimeline format
  const executionPhases: ExecutionPhase[] = useMemo(() => {
    return phases.map(phase => ({
      id: phase.id,
      name: phase.name,
      status: phase.status,
      agents: phase.agents.map(agent => ({
        id: agent.id,
        name: agent.name,
        status: agent.status,
      })),
    }));
  }, [phases]);

  // Calculate overall journey progress (Discovery = 20%, rest = 80%)
  const journeyProgress = useMemo(() => {
    // Discovery is complete (20%)
    const discoveryPercent = 20;
    // Execution progress (80% of remaining)
    const executionPercent = (progress / 100) * 80;
    return Math.round(discoveryPercent + executionPercent);
  }, [progress]);

  // Format elapsed time as mm:ss
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const [fetchError, setFetchError] = useState<string | null>(null);

  // Handle completion - use pack from SSE if available, otherwise fetch
  useEffect(() => {
    if (isComplete && completionStatus === 'completed') {
      // If pack was included in the done event (test sessions), use it directly
      if (completedPack) {
        onComplete(completedPack as unknown as InceptionPack);
        return;
      }
      // Otherwise fetch from API - use correct endpoint based on session type
      setFetchError(null);
      const fetchPack = useTestEndpoint ? getV4TestInceptionPack : getInceptionPack;
      fetchPack(sessionId)
        .then((pack: InceptionPack) => {
          onComplete(pack);
        })
        .catch((err: unknown) => {
          console.error('Failed to fetch pack:', err);
          setFetchError(
            err instanceof Error
              ? `Failed to load pack: ${err.message}. Try refreshing the page.`
              : 'Failed to load inception pack. Try refreshing the page.'
          );
        });
    }
  }, [isComplete, completionStatus, completedPack, sessionId, onComplete, useTestEndpoint]);

  // Get current agent insights
  const currentInsights = currentAgent ? insights[currentAgent] || [] : [];

  // Get recent insights across all agents (last 10)
  const recentInsights = Object.entries(insights)
    .flatMap(([agent, agentInsights]) =>
      agentInsights.map((insight) => ({
        ...insight,
        agent,
        agentName: agentStates[agent]?.displayName || agent,
      }))
    )
    .slice(-10)
    .reverse();

  // Determine if we're in early loading state (no insights yet)
  const isEarlyLoading = progress < 15 && recentInsights.length === 0;

  // Get current phase messages for activity indicator
  const currentPhaseMessages = useMemo(() => {
    const phase = currentPhase?.toLowerCase() || 'planning';
    return PHASE_MESSAGES[phase] || PHASE_MESSAGES.planning;
  }, [currentPhase]);

  return (
    <div className="v4-root" style={{ minHeight: '100vh' }}>
      {/* Header */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 24px',
          background: 'var(--v4-surface)',
          borderBottom: '1px solid var(--v4-border)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={onBack}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              fontSize: '14px',
              color: 'var(--v4-text-secondary)',
              background: 'transparent',
              border: '1px solid var(--v4-border)',
              borderRadius: 'var(--v4-radius)',
              cursor: 'pointer',
            }}
          >
            <ArrowLeft size={16} />
            Back
          </button>
          <div>
            <h1 style={{ fontSize: '16px', fontWeight: 500, color: 'var(--v4-text)', margin: 0 }}>
              Seedform
            </h1>
            <p style={{ fontSize: '12px', color: 'var(--v4-text-secondary)', margin: '2px 0 0' }}>
              {currentPhase ? `Strategy & Delivery` : 'Generating inception pack...'}
            </p>
          </div>
          {isConnected && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                background: 'var(--v4-success-bg)',
                borderRadius: '100px',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--v4-success)',
              }}
            >
              <Radio size={12} />
              Live
            </span>
          )}
        </div>

        {/* Journey Progress */}
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', padding: '0 24px' }}>
          <div style={{ minWidth: '320px', maxWidth: '440px', width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--v4-text)', fontFamily: 'var(--v4-font-display)' }}>
                {currentPhase || 'Strategy'}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
                {journeyProgress}% complete
              </span>
            </div>
            <ProgressMilestoneIndicator
              progress={journeyProgress}
              milestones={[20, 45, 70, 100]}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--v4-text-muted)' }}>
            <Clock size={14} />
            <span style={{ fontSize: '14px', fontFamily: 'monospace' }}>{formatTime(elapsedTime)}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--v4-text)' }}>{progress}%</span>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px 24px',
            background: 'var(--v4-error-bg)',
            borderBottom: '1px solid rgba(220, 38, 38, 0.2)',
          }}
        >
          <AlertCircle size={18} style={{ color: 'var(--v4-error)' }} />
          <span style={{ fontSize: '14px', color: '#b91c1c' }}>{error}</span>
        </div>
      )}

      {/* Main Content */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '300px 1fr',
          minHeight: 'calc(100vh - 57px)',
        }}
      >
        {/* Left Sidebar: Journey Timeline */}
        <aside
          style={{
            background: 'var(--v4-surface)',
            borderRight: '1px solid var(--v4-border)',
            overflowY: 'auto',
            padding: '16px',
          }}
        >
          <JourneyTimeline
            discoveryStages={completedDiscoveryStages}
            discoveryComplete={true}
            executionPhases={executionPhases}
            currentExecutionPhase={currentPhase || undefined}
            onAgentClick={(agentId) => setExpandedAgent(expandedAgent === agentId ? null : agentId)}
            onDiscoveryStageClick={handleDiscoveryStageClick}
            currentView="execution"
            allowDiscoveryClick={!!discoverySession}
          />
        </aside>

        {/* Main Area */}
        <main style={{ padding: '24px', overflowY: 'auto' }}>
          {/* Milestone Toast */}
          <MilestoneToast progress={journeyProgress} />

          {/* Activity Indicator */}
          {!isComplete && (
            <div
              className="v4-animate-fade-in"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                background: 'var(--v4-accent-lighter)',
                borderRadius: 'var(--v4-radius-md)',
                marginBottom: '20px',
              }}
            >
              <Loader2 size={16} className="v4-spin" style={{ color: 'var(--v4-accent)' }} />
              <ActivityIndicator
                customMessages={currentPhaseMessages}
                interval={3500}
                showSpinner={false}
              />
            </div>
          )}

          {/* Revision Indicator */}
          {revisionState && (
            <div style={{ marginBottom: '20px' }}>
              <RevisionIndicator state={revisionState} />
            </div>
          )}

          {/* Early Loading State - Show skeleton */}
          {isEarlyLoading && (
            <div className="v4-animate-fade-in" style={{ marginBottom: '24px' }}>
              <div
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  color: 'var(--v4-text-muted)',
                  marginBottom: '12px',
                }}
              >
                Initializing...
              </div>
              <AgentSkeleton showInsights={true} />
            </div>
          )}

          {/* Current Agent Card */}
          {currentAgent && !isEarlyLoading && (
            <div className="v4-animate-slide-up" style={{ marginBottom: '24px' }}>
              <div
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  color: 'var(--v4-text-muted)',
                  marginBottom: '12px',
                }}
              >
                Current Agent
              </div>
              <AgentCard
                name={agentStates[currentAgent]?.displayName || currentAgent}
                status={agentStates[currentAgent]?.status || 'running'}
                message={agentStates[currentAgent]?.message}
                insights={currentInsights.map((i) => ({
                  key: i.key,
                  value: i.value,
                  tier: i.tier,
                }))}
                isExpanded={expandedAgent === currentAgent}
                onToggle={() => setExpandedAgent(expandedAgent === currentAgent ? null : currentAgent)}
                showThinking={currentInsights.length === 0}
              />
            </div>
          )}

          {/* Key Insights Section */}
          {(recentInsights.length > 0 || isEarlyLoading) && (
            <div style={{ marginBottom: '24px' }}>
              <div
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  color: 'var(--v4-text-muted)',
                  marginBottom: '12px',
                }}
              >
                Key Insights
              </div>
              {isEarlyLoading ? (
                <InsightSkeleton count={4} />
              ) : (
                <div
                  className="v4-card"
                  style={{
                    overflow: 'hidden',
                  }}
                >
                  {recentInsights.slice(0, 8).map((insight, i) => (
                    <div
                      key={i}
                      className="v4-animate-slide-up"
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '10px',
                        padding: '12px 16px',
                        borderBottom: i < Math.min(recentInsights.length, 8) - 1 ? '1px solid var(--v4-border-subtle)' : 'none',
                        animationDelay: `${i * 50}ms`,
                      }}
                    >
                      <span
                        style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          background: 'var(--v4-accent)',
                          marginTop: '6px',
                          flexShrink: 0,
                        }}
                      />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            marginBottom: '4px',
                          }}
                        >
                          <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>{insight.agentName}</span>
                          <span style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>•</span>
                          <span style={{ fontSize: '12px', color: 'var(--v4-text-secondary)' }}>{insight.key}</span>
                        </div>
                        <div
                          style={{
                            fontSize: '13px',
                            color: 'var(--v4-text)',
                            lineHeight: 1.5,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                          }}
                        >
                          {insight.value}
                          {insight.tier && <EvidenceBadge tier={insight.tier as EvidenceTier} inline />}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Constraint Flow */}
          {constraintFlow.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <ConstraintFlow items={constraintFlow} />
            </div>
          )}

          {/* Completion Message */}
          {isComplete && (
            <div
              style={{
                padding: '24px',
                background: fetchError
                  ? 'var(--v4-error-bg)'
                  : completionStatus === 'completed'
                    ? 'var(--v4-success-bg)'
                    : 'var(--v4-error-bg)',
                borderRadius: 'var(--v4-radius)',
                textAlign: 'center',
              }}
            >
              <h3
                style={{
                  fontSize: '18px',
                  fontWeight: 600,
                  color: fetchError
                    ? '#b91c1c'
                    : completionStatus === 'completed'
                      ? '#166534'
                      : '#b91c1c',
                  marginBottom: '8px',
                }}
              >
                {fetchError
                  ? 'Failed to Load Pack'
                  : completionStatus === 'completed'
                    ? 'Inception Pack Ready!'
                    : 'Generation Failed'}
              </h3>
              <p
                style={{
                  fontSize: '14px',
                  color: fetchError
                    ? '#dc2626'
                    : completionStatus === 'completed'
                      ? '#15803d'
                      : '#dc2626',
                }}
              >
                {fetchError
                  ? fetchError
                  : completionStatus === 'completed'
                    ? 'Your inception pack has been generated. Loading results...'
                    : 'Something went wrong. Please try again.'}
              </p>
              {fetchError && (
                <button
                  onClick={() => window.location.reload()}
                  style={{
                    marginTop: '12px',
                    padding: '8px 16px',
                    background: 'var(--v4-accent)',
                    color: 'white',
                    border: 'none',
                    borderRadius: 'var(--v4-radius)',
                    cursor: 'pointer',
                    fontSize: '14px',
                  }}
                >
                  Refresh Page
                </button>
              )}
            </div>
          )}
        </main>
      </div>

      {/* Discovery Output Modal */}
      {selectedDiscoveryStage && selectedStageOutput && (
        <DiscoveryOutputModal
          stageId={selectedDiscoveryStage}
          stageOutput={selectedStageOutput}
          onClose={() => setSelectedDiscoveryStage(null)}
        />
      )}

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 900px) {
          .v4-root > div {
            grid-template-columns: 1fr !important;
          }
          .v4-root aside {
            position: fixed;
            left: -300px;
            width: 300px;
            height: 100vh;
            top: 57px;
            z-index: 50;
            transition: left 0.3s ease;
          }
        }
      `}</style>
    </div>
  );
}

export default ExecutionViewV4;
