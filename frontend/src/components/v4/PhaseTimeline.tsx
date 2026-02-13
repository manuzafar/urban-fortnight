/**
 * V4 Phase Timeline Component
 * Pipeline phase visualization for execution view
 */

import { Check, Circle, AlertCircle, Loader2 } from 'lucide-react';
import '../../styles/theme-v4.css';

export interface Agent {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  isParallel?: boolean;
}

export interface Phase {
  id: string;
  name: string;
  agents: Agent[];
  status: 'pending' | 'running' | 'completed' | 'error';
}

interface PhaseTimelineProps {
  phases: Phase[];
  currentPhase: string | null;
  onAgentClick?: (agentId: string) => void;
}

export function PhaseTimeline({ phases, currentPhase, onAgentClick }: PhaseTimelineProps) {
  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'completed':
        return <Check size={12} />;
      case 'running':
        return <Loader2 size={12} className="v4-spin" />;
      case 'error':
        return <AlertCircle size={12} />;
      default:
        return <Circle size={12} />;
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'completed':
        return 'var(--v4-success)';
      case 'running':
        return 'var(--v4-accent)';
      case 'error':
        return 'var(--v4-error)';
      default:
        return 'var(--v4-text-muted)';
    }
  };

  return (
    <div style={{ padding: '16px' }}>
      <div
        style={{
          fontSize: '11px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: 'var(--v4-text-muted)',
          marginBottom: '16px',
        }}
      >
        Phase Timeline
      </div>
      {phases.map((phase, phaseIndex) => {
        const isCurrentPhase = phase.id === currentPhase;
        const hasRunningAgents = phase.agents.some((a) => a.status === 'running');
        const parallelAgents = phase.agents.filter((a) => a.isParallel);
        const hasParallel = parallelAgents.length > 1;

        return (
          <div key={phase.id} style={{ marginBottom: phaseIndex < phases.length - 1 ? '8px' : 0 }}>
            {/* Phase Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '10px 12px',
                background: isCurrentPhase ? 'var(--v4-bg)' : 'transparent',
                borderRadius: 'var(--v4-radius)',
                borderLeft: isCurrentPhase ? '3px solid var(--v4-accent)' : '3px solid transparent',
              }}
            >
              <span
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background:
                    phase.status === 'completed'
                      ? 'var(--v4-success)'
                      : phase.status === 'running'
                      ? 'var(--v4-accent)'
                      : 'var(--v4-border)',
                  color: phase.status !== 'pending' ? 'white' : 'var(--v4-text-muted)',
                  marginRight: '10px',
                }}
              >
                {phase.status === 'completed' ? (
                  <Check size={12} />
                ) : phase.status === 'running' ? (
                  <Loader2 size={12} className="v4-spin" />
                ) : (
                  <span style={{ fontSize: '10px', fontWeight: 600 }}>{phaseIndex + 1}</span>
                )}
              </span>
              <span
                style={{
                  fontSize: '14px',
                  fontWeight: isCurrentPhase ? 600 : 400,
                  color: phase.status === 'pending' ? 'var(--v4-text-muted)' : 'var(--v4-text)',
                }}
              >
                {phase.name}
              </span>
              {hasParallel && hasRunningAgents && (
                <span
                  style={{
                    marginLeft: 'auto',
                    fontSize: '10px',
                    padding: '2px 6px',
                    background: 'var(--v4-accent-light)',
                    color: 'var(--v4-accent)',
                    borderRadius: '3px',
                    fontWeight: 500,
                  }}
                >
                  parallel
                </span>
              )}
            </div>

            {/* Agents List */}
            {(isCurrentPhase || phase.status === 'completed' || phase.status === 'running') && (
              <div style={{ marginLeft: '20px', paddingLeft: '22px', borderLeft: '1px solid var(--v4-border)' }}>
                {hasParallel ? (
                  // Group parallel agents
                  <div
                    style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '4px',
                      padding: '8px 0',
                    }}
                  >
                    {phase.agents.map((agent) => (
                      <div
                        key={agent.id}
                        onClick={() => onAgentClick?.(agent.id)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '6px 10px',
                          fontSize: '12px',
                          color: getStatusColor(agent.status),
                          background: agent.status === 'running' ? 'var(--v4-accent-light)' : 'var(--v4-bg)',
                          borderRadius: '4px',
                          cursor: onAgentClick ? 'pointer' : 'default',
                        }}
                      >
                        {getStatusIcon(agent.status)}
                        <span>{agent.name}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  // Sequential agents
                  phase.agents.map((agent) => (
                    <div
                      key={agent.id}
                      onClick={() => onAgentClick?.(agent.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '8px 0',
                        fontSize: '13px',
                        color: agent.status === 'pending' ? 'var(--v4-text-muted)' : 'var(--v4-text-secondary)',
                        cursor: onAgentClick ? 'pointer' : 'default',
                      }}
                    >
                      <span style={{ color: getStatusColor(agent.status) }}>{getStatusIcon(agent.status)}</span>
                      <span>{agent.name}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        );
      })}

      <style>{`
        .v4-spin {
          animation: v4-spin 1s linear infinite;
        }
        @keyframes v4-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default PhaseTimeline;
