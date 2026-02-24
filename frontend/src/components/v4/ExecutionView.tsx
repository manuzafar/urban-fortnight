/**
 * V4 Execution View Component
 * Real-time agent execution with transparency features
 * Shows unified journey with Discovery as completed phase
 */

import { useEffect, useState, useMemo } from 'react';
import { ArrowLeft, Radio, Clock, AlertCircle, Check } from 'lucide-react';
import { useSSEV4 } from '../../hooks/useSSEV4';
import { getInceptionPack } from '../../api/client';
import { JourneyTimeline, type ExecutionPhase, type DiscoveryStage } from './JourneyTimeline';
import { AgentCard } from './AgentCard';
import { ConstraintFlow } from './ConstraintFlow';
import { RevisionIndicator } from './RevisionIndicator';
import { EvidenceBadge, type EvidenceTier } from './EvidenceBadge';
import type { InceptionPack } from '../../types/api';
import '../../styles/theme-v4.css';

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
    error,
    currentPhase,
    constraintFlow,
    revisionState,
    phases,
    elapsedTime,
  } = useSSEV4(sessionId, authToken, true, useTestEndpoint);

  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  // Create completed Discovery stages for JourneyTimeline
  const completedDiscoveryStages: Record<string, DiscoveryStage> = useMemo(() => ({
    problem_love: { id: 'problem_love', status: 'completed' },
    customer_truth: { id: 'customer_truth', status: 'completed' },
    opportunity_mapping: { id: 'opportunity_mapping', status: 'completed' },
    solution_design: { id: 'solution_design', status: 'completed' },
    validation_plan: { id: 'validation_plan', status: 'completed' },
  }), []);

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

  // Fetch pack when complete
  useEffect(() => {
    if (isComplete && completionStatus === 'completed') {
      getInceptionPack(sessionId)
        .then((pack: InceptionPack) => {
          onComplete(pack);
        })
        .catch((err: unknown) => {
          console.error('Failed to fetch pack:', err);
        });
    }
  }, [isComplete, completionStatus, sessionId, onComplete]);

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
          <div style={{ minWidth: '280px', maxWidth: '400px' }}>
            <div style={{ fontSize: '12px', fontWeight: 500, color: 'var(--v4-text-secondary)', textAlign: 'center', marginBottom: '4px' }}>
              Journey: {currentPhase || 'Strategy'} ({journeyProgress}%)
            </div>
            <div style={{ position: 'relative', height: '6px', background: 'var(--v4-bg)', borderRadius: '3px' }}>
              <div
                style={{
                  height: '100%',
                  background: 'var(--v4-accent)',
                  borderRadius: '3px',
                  width: `${journeyProgress}%`,
                  transition: 'width 0.3s ease',
                }}
              />
              {/* Phase markers */}
              <div style={{ position: 'absolute', top: '-3px', left: '0%', transform: 'translateX(-50%)' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--v4-success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Check size={8} color="white" />
                </div>
              </div>
              <div style={{ position: 'absolute', top: '-3px', left: '20%', transform: 'translateX(-50%)', width: '12px', height: '12px', borderRadius: '50%', background: journeyProgress >= 20 ? 'var(--v4-accent)' : 'var(--v4-surface)', border: '2px solid ' + (journeyProgress >= 20 ? 'var(--v4-accent)' : 'var(--v4-border)') }} />
              <div style={{ position: 'absolute', top: '-3px', left: '45%', transform: 'translateX(-50%)', width: '12px', height: '12px', borderRadius: '50%', background: journeyProgress >= 45 ? 'var(--v4-accent)' : 'var(--v4-surface)', border: '2px solid ' + (journeyProgress >= 45 ? 'var(--v4-accent)' : 'var(--v4-border)') }} />
              <div style={{ position: 'absolute', top: '-3px', left: '70%', transform: 'translateX(-50%)', width: '12px', height: '12px', borderRadius: '50%', background: journeyProgress >= 70 ? 'var(--v4-accent)' : 'var(--v4-surface)', border: '2px solid ' + (journeyProgress >= 70 ? 'var(--v4-accent)' : 'var(--v4-border)') }} />
              <div style={{ position: 'absolute', top: '-3px', left: '90%', transform: 'translateX(-50%)', width: '12px', height: '12px', borderRadius: '50%', background: journeyProgress >= 90 ? 'var(--v4-accent)' : 'var(--v4-surface)', border: '2px solid ' + (journeyProgress >= 90 ? 'var(--v4-accent)' : 'var(--v4-border)') }} />
            </div>
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
            currentView="execution"
          />
        </aside>

        {/* Main Area */}
        <main style={{ padding: '24px', overflowY: 'auto' }}>
          {/* Revision Indicator */}
          {revisionState && (
            <div style={{ marginBottom: '20px' }}>
              <RevisionIndicator state={revisionState} />
            </div>
          )}

          {/* Current Agent Card */}
          {currentAgent && (
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
              />
            </div>
          )}

          {/* Key Insights Section */}
          {recentInsights.length > 0 && (
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
              <div
                style={{
                  background: 'var(--v4-surface)',
                  border: '1px solid var(--v4-border)',
                  borderRadius: 'var(--v4-radius)',
                  overflow: 'hidden',
                }}
              >
                {recentInsights.slice(0, 8).map((insight, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '10px',
                      padding: '12px 16px',
                      borderBottom: i < Math.min(recentInsights.length, 8) - 1 ? '1px solid var(--v4-border)' : 'none',
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
                background: completionStatus === 'completed' ? 'var(--v4-success-bg)' : 'var(--v4-error-bg)',
                borderRadius: 'var(--v4-radius)',
                textAlign: 'center',
              }}
            >
              <h3
                style={{
                  fontSize: '18px',
                  fontWeight: 600,
                  color: completionStatus === 'completed' ? '#166534' : '#b91c1c',
                  marginBottom: '8px',
                }}
              >
                {completionStatus === 'completed' ? 'Inception Pack Ready!' : 'Generation Failed'}
              </h3>
              <p
                style={{
                  fontSize: '14px',
                  color: completionStatus === 'completed' ? '#15803d' : '#dc2626',
                }}
              >
                {completionStatus === 'completed'
                  ? 'Your inception pack has been generated. Loading results...'
                  : 'Something went wrong. Please try again.'}
              </p>
            </div>
          )}
        </main>
      </div>

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
