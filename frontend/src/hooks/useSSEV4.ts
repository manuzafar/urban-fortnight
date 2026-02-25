/**
 * V4 SSE (Server-Sent Events) Hook for real-time discovery session updates.
 *
 * Enhanced version with transparency features:
 * - Phase tracking with parallel execution grouping
 * - Constraint flow visualization
 * - Revision loop state tracking
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { ConstraintFlowItem } from '../components/v4/ConstraintFlow';
import type { RevisionState } from '../components/v4/RevisionIndicator';
import type { Phase, Agent } from '../components/v4/PhaseTimeline';
import type { EvidenceTier } from '../components/v4/EvidenceBadge';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Event types from the backend (extended for V4)
export type StreamEventTypeV4 =
  | 'agent_start'
  | 'insight'
  | 'agent_complete'
  | 'progress'
  | 'workflow_error'
  | 'done'
  | 'heartbeat'
  // Enhanced event types
  | 'plan_ready'
  | 'competitor'
  | 'market_data'
  | 'risk'
  | 'financial'
  | 'diagram'
  | 'citation'
  | 'decision'
  // V4 new event types for transparency
  | 'phase_start'
  | 'phase_complete'
  | 'constraint_injected'
  | 'revision_started'
  | 'revision_complete'
  | 'parallel_start';

export interface StreamEventV4 {
  type: StreamEventTypeV4;
  agent: string | null;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface InsightV4 {
  key: string;
  value: string;
  preview?: unknown;
  tier?: EvidenceTier;
}

export interface AgentStateV4 {
  status: 'pending' | 'running' | 'completed' | 'error';
  displayName: string;
  icon: string;
  phase: string;
  message?: string;
  summary?: string;
  insightsCount: number;
  isParallel?: boolean;
}

// Phase configuration with agents
const PHASE_CONFIG: { id: string; name: string; agents: string[]; parallel: boolean }[] = [
  { id: 'planning', name: 'Planning', agents: ['planner'], parallel: false },
  {
    id: 'discovery',
    name: 'Discovery',
    agents: ['customer_research', 'competitive_intelligence', 'persona_development'],
    parallel: true,
  },
  {
    id: 'strategy',
    name: 'Strategy',
    agents: ['business_strategy', 'gtm_strategy', 'financial_modeling'],
    parallel: true,
  },
  {
    id: 'delivery',
    name: 'Delivery',
    agents: ['product_requirements', 'technical_architect', 'legal_regulatory', 'risk_assessment'],
    parallel: true,
  },
  { id: 'design', name: 'Design', agents: ['wireframe_agent', 'prototype_agent'], parallel: false },
  { id: 'quality', name: 'Quality', agents: ['critique'], parallel: false },
  {
    id: 'synthesis',
    name: 'Synthesis',
    agents: ['stakeholder_agent', 'validation_agent', 'executive_summary_agent'],
    parallel: true,
  },
];

// Agent display configuration
const AGENT_CONFIG: Record<string, { name: string; icon: string; phase: string }> = {
  planner: { name: 'Research Planner', icon: 'clipboard-list', phase: 'Planning' },
  customer_research: { name: 'Customer Research', icon: 'search', phase: 'Discovery' },
  competitive_intelligence: { name: 'Competitive Intel', icon: 'target', phase: 'Discovery' },
  persona_development: { name: 'Persona Development', icon: 'users', phase: 'Discovery' },
  business_strategy: { name: 'Business Strategy', icon: 'trending-up', phase: 'Strategy' },
  gtm_strategy: { name: 'GTM Strategy', icon: 'rocket', phase: 'Strategy' },
  financial_modeling: { name: 'Financial Model', icon: 'dollar-sign', phase: 'Strategy' },
  product_requirements: { name: 'Product Requirements', icon: 'file-text', phase: 'Delivery' },
  technical_architect: { name: 'Technical Architecture', icon: 'cpu', phase: 'Delivery' },
  legal_regulatory: { name: 'Legal Review', icon: 'shield', phase: 'Delivery' },
  risk_assessment: { name: 'Risk Assessment', icon: 'alert-triangle', phase: 'Delivery' },
  wireframe_agent: { name: 'Wireframes', icon: 'layout', phase: 'Design' },
  prototype_agent: { name: 'Prototype', icon: 'play-circle', phase: 'Design' },
  critique: { name: 'Quality Check', icon: 'check-circle', phase: 'Quality' },
  stakeholder_agent: { name: 'Stakeholder Views', icon: 'briefcase', phase: 'Synthesis' },
  validation_agent: { name: 'Validation Playbook', icon: 'clipboard-check', phase: 'Synthesis' },
  executive_summary_agent: { name: 'Executive Summary', icon: 'file-check', phase: 'Synthesis' },
  executive_summary: { name: 'Executive Summary', icon: 'file-check', phase: 'Synthesis' },
};

// Flat agent order
const AGENT_ORDER = PHASE_CONFIG.flatMap((p) => p.agents);

export interface UseSSEV4Result {
  /** Whether the SSE connection is active */
  isConnected: boolean;
  /** The currently running agent (or null if none) */
  currentAgent: string | null;
  /** Map of agent key to its current state */
  agentStates: Record<string, AgentStateV4>;
  /** Map of agent key to its discovered insights */
  insights: Record<string, InsightV4[]>;
  /** Overall progress percentage (0-100) */
  progress: number;
  /** Whether the session is complete */
  isComplete: boolean;
  /** Final completion status */
  completionStatus: 'completed' | 'failed' | null;
  /** Completed inception pack (included in done event for test sessions) */
  completedPack: Record<string, unknown> | null;
  /** Error message if any */
  error: string | null;
  /** All received events (for debugging) */
  events: StreamEventV4[];
  /** Ordered list of agent keys */
  agentOrder: string[];
  /** Manually close the connection */
  close: () => void;

  // V4 Transparency fields
  /** Current phase ID */
  currentPhase: string | null;
  /** Agents running in parallel */
  parallelAgents: string[];
  /** Constraint flow items */
  constraintFlow: ConstraintFlowItem[];
  /** Revision state */
  revisionState: RevisionState | null;
  /** Phases for timeline display */
  phases: Phase[];
  /** Elapsed time in seconds */
  elapsedTime: number;
}

/**
 * V4 Hook for subscribing to SSE events for a discovery session.
 * Enhanced with transparency features for the V4 UI.
 *
 * @param sessionId - The session ID to connect to
 * @param authToken - The auth token for authenticated endpoints
 * @param enabled - Whether the hook should connect
 * @param useTestEndpoint - If true, uses the V4 test stream endpoint (no auth required)
 */
export function useSSEV4(
  sessionId: string | null,
  authToken: string | null,
  enabled: boolean = true,
  useTestEndpoint: boolean = false
): UseSSEV4Result {
  const [isConnected, setIsConnected] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [agentStates, setAgentStates] = useState<Record<string, AgentStateV4>>({});
  const [insights, setInsights] = useState<Record<string, InsightV4[]>>({});
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [completionStatus, setCompletionStatus] = useState<'completed' | 'failed' | null>(null);
  const [completedPack, setCompletedPack] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<StreamEventV4[]>([]);

  // V4 Transparency state
  const [currentPhase, setCurrentPhase] = useState<string | null>(null);
  const [parallelAgents, setParallelAgents] = useState<string[]>([]);
  const [constraintFlow, setConstraintFlow] = useState<ConstraintFlowItem[]>([]);
  const [revisionState, setRevisionState] = useState<RevisionState | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  const eventSourceRef = useRef<EventSource | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number | null>(null);

  // Build phases for timeline display
  const phases: Phase[] = PHASE_CONFIG.map((phaseConfig) => {
    const phaseAgents: Agent[] = phaseConfig.agents.map((agentId) => {
      const state = agentStates[agentId];
      const config = AGENT_CONFIG[agentId] || { name: agentId, icon: 'cpu', phase: 'Unknown' };
      return {
        id: agentId,
        name: state?.displayName || config.name,
        status: state?.status || 'pending',
        isParallel: phaseConfig.parallel,
      };
    });

    // Determine phase status
    let phaseStatus: Phase['status'] = 'pending';
    const hasRunning = phaseAgents.some((a) => a.status === 'running');
    const allCompleted = phaseAgents.every((a) => a.status === 'completed');
    const hasError = phaseAgents.some((a) => a.status === 'error');

    if (hasError) phaseStatus = 'error';
    else if (allCompleted) phaseStatus = 'completed';
    else if (hasRunning || phaseAgents.some((a) => a.status === 'completed')) phaseStatus = 'running';

    return {
      id: phaseConfig.id,
      name: phaseConfig.name,
      agents: phaseAgents,
      status: phaseStatus,
    };
  });

  // Initialize agent states
  useEffect(() => {
    const initialStates: Record<string, AgentStateV4> = {};
    for (const agent of AGENT_ORDER) {
      const config = AGENT_CONFIG[agent] || { name: agent, icon: 'cpu', phase: 'Unknown' };
      const phaseConfig = PHASE_CONFIG.find((p) => p.agents.includes(agent));
      initialStates[agent] = {
        status: 'pending',
        displayName: config.name,
        icon: config.icon,
        phase: config.phase,
        insightsCount: 0,
        isParallel: phaseConfig?.parallel,
      };
    }
    setAgentStates(initialStates);
  }, []);

  const close = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!sessionId || !authToken || !enabled) {
      return;
    }

    // Reset state on new session
    setIsComplete(false);
    setCompletionStatus(null);
    setError(null);
    setProgress(0);
    setCurrentAgent(null);
    setEvents([]);
    setInsights({});
    setCurrentPhase(null);
    setParallelAgents([]);
    setConstraintFlow([]);
    setRevisionState(null);
    setElapsedTime(0);

    // Start timer
    startTimeRef.current = Date.now();
    timerRef.current = setInterval(() => {
      if (startTimeRef.current) {
        setElapsedTime(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }
    }, 1000);

    // Reset agent states to pending
    setAgentStates((prev) => {
      const reset: Record<string, AgentStateV4> = {};
      for (const agent of AGENT_ORDER) {
        const config = AGENT_CONFIG[agent] || { name: agent, icon: 'cpu', phase: 'Unknown' };
        const phaseConfig = PHASE_CONFIG.find((p) => p.agents.includes(agent));
        reset[agent] = {
          ...prev[agent],
          status: 'pending',
          phase: config.phase,
          message: undefined,
          summary: undefined,
          insightsCount: 0,
          isParallel: phaseConfig?.parallel,
        };
      }
      return reset;
    });

    // Create EventSource with appropriate endpoint
    // For V4 test sessions, use the test stream endpoint (no auth required)
    // For regular sessions, use the authenticated endpoint
    const url = useTestEndpoint
      ? `${API_BASE_URL}/api/discovery/v4/test/sessions/${sessionId}/stream`
      : `${API_BASE_URL}/api/discovery/session/${sessionId}/stream?token=${encodeURIComponent(authToken)}`;
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onerror = (e) => {
      console.error('SSE Error:', e);
      setIsConnected(false);

      if (eventSource.readyState === EventSource.CLOSED) {
        return;
      }

      setError('Connection lost. Attempting to reconnect...');
    };

    // Handle different event types
    const handleEvent = (_eventType: string, data: string) => {
      try {
        const parsed = JSON.parse(data) as StreamEventV4;
        setEvents((prev) => [...prev, parsed]);

        switch (parsed.type) {
          case 'agent_start': {
            const agent = parsed.agent;
            if (agent) {
              setCurrentAgent(agent);
              const config = AGENT_CONFIG[agent] || { name: agent, icon: 'cpu', phase: 'Unknown' };
              const phaseConfig = PHASE_CONFIG.find((p) => p.agents.includes(agent));

              // Update current phase
              if (phaseConfig) {
                setCurrentPhase(phaseConfig.id);
              }

              setAgentStates((prev) => ({
                ...prev,
                [agent]: {
                  status: 'running',
                  displayName: prev[agent]?.displayName || config.name,
                  icon: prev[agent]?.icon || config.icon,
                  phase: prev[agent]?.phase || config.phase,
                  message: (parsed.data.message as string) || 'Processing...',
                  insightsCount: prev[agent]?.insightsCount || 0,
                  isParallel: phaseConfig?.parallel,
                },
              }));
            }
            break;
          }

          case 'insight': {
            const agent = parsed.agent;
            if (agent) {
              const insight: InsightV4 = {
                key: parsed.data.key as string,
                value: parsed.data.value as string,
                preview: parsed.data.preview,
                tier: parsed.data.tier as EvidenceTier | undefined,
              };
              setInsights((prev) => ({
                ...prev,
                [agent]: [...(prev[agent] || []), insight],
              }));
              setAgentStates((prev) => ({
                ...prev,
                [agent]: {
                  ...prev[agent],
                  insightsCount: (prev[agent]?.insightsCount || 0) + 1,
                },
              }));
            }
            break;
          }

          case 'agent_complete': {
            const agent = parsed.agent;
            if (agent) {
              const config = AGENT_CONFIG[agent] || { name: agent, icon: 'cpu', phase: 'Unknown' };
              const phaseConfig = PHASE_CONFIG.find((p) => p.agents.includes(agent));
              setAgentStates((prev) => ({
                ...prev,
                [agent]: {
                  status: 'completed',
                  displayName: prev[agent]?.displayName || config.name,
                  icon: prev[agent]?.icon || config.icon,
                  phase: prev[agent]?.phase || config.phase,
                  summary: (parsed.data.summary as string) || 'Complete',
                  insightsCount: prev[agent]?.insightsCount || 0,
                  isParallel: phaseConfig?.parallel,
                },
              }));
            }
            break;
          }

          case 'progress': {
            setProgress(parsed.data.percentage as number);
            break;
          }

          case 'workflow_error': {
            setError(parsed.data.message as string);
            if (parsed.agent) {
              setAgentStates((prev) => ({
                ...prev,
                [parsed.agent!]: {
                  ...prev[parsed.agent!],
                  status: 'error',
                },
              }));
            }
            break;
          }

          case 'done': {
            setIsComplete(true);
            setCompletionStatus(parsed.data.status as 'completed' | 'failed');
            setProgress(100);
            // Capture the pack if included in the done event (for test sessions)
            if (parsed.data.pack) {
              setCompletedPack(parsed.data.pack as Record<string, unknown>);
            }
            eventSource.close();
            setIsConnected(false);
            if (timerRef.current) {
              clearInterval(timerRef.current);
            }
            break;
          }

          case 'heartbeat': {
            // Keep-alive, no action needed
            break;
          }

          // V4 new event types
          case 'phase_start': {
            setCurrentPhase(parsed.data.phase as string);
            const agents = parsed.data.agents as string[] | undefined;
            if (agents) {
              setParallelAgents(agents);
            }
            break;
          }

          case 'phase_complete': {
            // Phase completed, clear parallel agents
            setParallelAgents([]);
            break;
          }

          case 'constraint_injected': {
            const constraintItem: ConstraintFlowItem = {
              id: `constraint-${Date.now()}`,
              fromAgent: parsed.data.from_agent as string,
              fromPhase: parsed.data.from_phase as string,
              toAgents: parsed.data.to_agents as string[],
              toPhase: parsed.data.to_phase as string,
              constraintType: parsed.data.constraint_type as string,
              summary: parsed.data.summary as string,
              timestamp: parsed.timestamp,
            };
            setConstraintFlow((prev) => [...prev, constraintItem]);
            break;
          }

          case 'revision_started': {
            setRevisionState({
              isActive: true,
              iteration: parsed.data.iteration as number,
              maxIterations: parsed.data.max_iterations as number,
              agent: parsed.data.agent as string,
              failedCriteria: parsed.data.failed_criteria as string[],
            });
            break;
          }

          case 'revision_complete': {
            setRevisionState(null);
            break;
          }

          case 'parallel_start': {
            const agents = parsed.data.agents as string[];
            setParallelAgents(agents);
            break;
          }

          // Enhanced event types - treat as insights
          case 'plan_ready':
          case 'competitor':
          case 'market_data':
          case 'risk':
          case 'financial':
          case 'diagram':
          case 'citation':
          case 'decision': {
            const agent = parsed.agent || 'planner';
            const insight: InsightV4 = {
              key: parsed.type,
              value: JSON.stringify(parsed.data),
              preview: parsed.data,
            };
            setInsights((prev) => ({
              ...prev,
              [agent]: [...(prev[agent] || []), insight],
            }));
            break;
          }
        }
      } catch (e) {
        console.error('Error parsing SSE event:', e, data);
      }
    };

    // Helper to safely handle SSE events
    const safeEventHandler = (eventType: string) => (e: Event) => {
      const messageEvent = e as MessageEvent;
      if (messageEvent.data !== undefined && messageEvent.data !== null) {
        handleEvent(eventType, messageEvent.data);
      }
    };

    // Listen to all event types
    const eventTypes: StreamEventTypeV4[] = [
      'agent_start',
      'insight',
      'agent_complete',
      'progress',
      'workflow_error',
      'done',
      'heartbeat',
      'plan_ready',
      'competitor',
      'market_data',
      'risk',
      'financial',
      'diagram',
      'citation',
      'decision',
      'phase_start',
      'phase_complete',
      'constraint_injected',
      'revision_started',
      'revision_complete',
      'parallel_start',
    ];

    eventTypes.forEach((type) => {
      eventSource.addEventListener(type, safeEventHandler(type));
    });

    // Generic message handler
    eventSource.onmessage = (e) => {
      if (e.data !== undefined && e.data !== null) {
        handleEvent('message', e.data);
      }
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [sessionId, authToken, enabled]);

  return {
    isConnected,
    currentAgent,
    agentStates,
    insights,
    progress,
    isComplete,
    completionStatus,
    completedPack,
    error,
    events,
    agentOrder: AGENT_ORDER,
    close,
    // V4 fields
    currentPhase,
    parallelAgents,
    constraintFlow,
    revisionState,
    phases,
    elapsedTime,
  };
}

export default useSSEV4;
