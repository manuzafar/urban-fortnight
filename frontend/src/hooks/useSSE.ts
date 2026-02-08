/**
 * SSE (Server-Sent Events) Hook for real-time discovery session updates.
 *
 * Provides real-time streaming of agent progress, insights, and completion
 * events during discovery session execution.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Event types from the backend
export type StreamEventType =
  | 'agent_start'
  | 'insight'
  | 'agent_complete'
  | 'progress'
  | 'error'
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
  | 'decision';

export interface StreamEvent {
  type: StreamEventType;
  agent: string | null;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface Insight {
  key: string;
  value: string;
  preview?: unknown;
}

export interface AgentState {
  status: 'pending' | 'running' | 'completed' | 'error';
  displayName: string;
  icon: string;
  phase: string;
  message?: string;
  summary?: string;
  insightsCount: number;
}

// Agent display configuration (V3.0 - 17 agents across 7 phases)
const AGENT_CONFIG: Record<string, { name: string; icon: string; phase: string }> = {
  // Planning
  planner: { name: 'Research Planner', icon: 'clipboard-list', phase: 'Planning' },

  // Discovery (parallel)
  customer_research: { name: 'Customer Research', icon: 'search', phase: 'Discovery' },
  competitive_intelligence: { name: 'Competitive Intel', icon: 'target', phase: 'Discovery' },
  persona_development: { name: 'Persona Development', icon: 'users', phase: 'Discovery' },

  // Strategy (parallel)
  business_strategy: { name: 'Business Strategy', icon: 'trending-up', phase: 'Strategy' },
  gtm_strategy: { name: 'GTM Strategy', icon: 'rocket', phase: 'Strategy' },
  financial_modeling: { name: 'Financial Model', icon: 'dollar-sign', phase: 'Strategy' },

  // Delivery (parallel)
  product_requirements: { name: 'Product Requirements', icon: 'file-text', phase: 'Delivery' },
  technical_architect: { name: 'Technical Architecture', icon: 'cpu', phase: 'Delivery' },
  legal_regulatory: { name: 'Legal Review', icon: 'shield', phase: 'Delivery' },
  risk_assessment: { name: 'Risk Assessment', icon: 'alert-triangle', phase: 'Delivery' },

  // Design (sequential)
  wireframe_agent: { name: 'Wireframes', icon: 'layout', phase: 'Design' },
  prototype_agent: { name: 'Prototype', icon: 'play-circle', phase: 'Design' },

  // Quality
  critique: { name: 'Quality Check', icon: 'check-circle', phase: 'Quality' },

  // Synthesis (parallel)
  stakeholder_agent: { name: 'Stakeholder Views', icon: 'briefcase', phase: 'Synthesis' },
  validation_agent: { name: 'Validation Playbook', icon: 'clipboard-check', phase: 'Synthesis' },
  executive_summary_agent: { name: 'Executive Summary', icon: 'file-check', phase: 'Synthesis' },

  // Legacy agent name mapping for backward compatibility
  executive_summary: { name: 'Executive Summary', icon: 'file-check', phase: 'Synthesis' },
};

// Agent execution order (V3.0 - 17 agents)
const AGENT_ORDER = [
  'planner',
  'customer_research', 'competitive_intelligence', 'persona_development',
  'business_strategy', 'gtm_strategy', 'financial_modeling',
  'product_requirements', 'technical_architect', 'legal_regulatory', 'risk_assessment',
  'wireframe_agent', 'prototype_agent',
  'critique',
  'stakeholder_agent', 'validation_agent', 'executive_summary_agent',
];

export interface UseSSEResult {
  /** Whether the SSE connection is active */
  isConnected: boolean;
  /** The currently running agent (or null if none) */
  currentAgent: string | null;
  /** Map of agent key to its current state */
  agentStates: Record<string, AgentState>;
  /** Map of agent key to its discovered insights */
  insights: Record<string, Insight[]>;
  /** Overall progress percentage (0-100) */
  progress: number;
  /** Whether the session is complete */
  isComplete: boolean;
  /** Final completion status */
  completionStatus: 'completed' | 'failed' | null;
  /** Error message if any */
  error: string | null;
  /** All received events (for debugging) */
  events: StreamEvent[];
  /** Ordered list of agent keys */
  agentOrder: string[];
  /** Manually close the connection */
  close: () => void;
}

/**
 * Hook for subscribing to SSE events for a discovery session.
 *
 * @param sessionId - The session ID to subscribe to
 * @param authToken - The auth token for authentication
 * @param enabled - Whether to enable the subscription (default: true)
 * @returns SSE state and controls
 */
export function useSSE(
  sessionId: string | null,
  authToken: string | null,
  enabled: boolean = true
): UseSSEResult {
  const [isConnected, setIsConnected] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [agentStates, setAgentStates] = useState<Record<string, AgentState>>({});
  const [insights, setInsights] = useState<Record<string, Insight[]>>({});
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [completionStatus, setCompletionStatus] = useState<'completed' | 'failed' | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<StreamEvent[]>([]);

  const eventSourceRef = useRef<EventSource | null>(null);

  // Initialize agent states
  useEffect(() => {
    const initialStates: Record<string, AgentState> = {};
    for (const agent of AGENT_ORDER) {
      const config = AGENT_CONFIG[agent] || { name: agent, icon: 'cpu', phase: 'Unknown' };
      initialStates[agent] = {
        status: 'pending',
        displayName: config.name,
        icon: config.icon,
        phase: config.phase,
        insightsCount: 0,
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

    // Reset agent states to pending
    setAgentStates((prev) => {
      const reset: Record<string, AgentState> = {};
      for (const agent of AGENT_ORDER) {
        const config = AGENT_CONFIG[agent] || { name: agent, icon: 'cpu', phase: 'Unknown' };
        reset[agent] = {
          ...prev[agent],
          status: 'pending',
          phase: config.phase,
          message: undefined,
          summary: undefined,
          insightsCount: 0,
        };
      }
      return reset;
    });

    // Create EventSource with auth token in URL (EventSource doesn't support headers)
    const url = `${API_BASE_URL}/api/discovery/session/${sessionId}/stream?token=${encodeURIComponent(authToken)}`;
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onerror = (e) => {
      console.error('SSE Error:', e);
      setIsConnected(false);

      // Don't set error if we're intentionally closing
      if (eventSource.readyState === EventSource.CLOSED) {
        return;
      }

      setError('Connection lost. Attempting to reconnect...');
    };

    // Handle different event types
    const handleEvent = (_eventType: string, data: string) => {
      try {
        const parsed = JSON.parse(data) as StreamEvent;
        setEvents((prev) => [...prev, parsed]);

        switch (parsed.type) {
          case 'agent_start': {
            const agent = parsed.agent;
            if (agent) {
              setCurrentAgent(agent);
              const config = AGENT_CONFIG[agent] || { name: agent, icon: 'cpu', phase: 'Unknown' };
              setAgentStates((prev) => ({
                ...prev,
                [agent]: {
                  status: 'running',
                  displayName: prev[agent]?.displayName || config.name,
                  icon: prev[agent]?.icon || config.icon,
                  phase: prev[agent]?.phase || config.phase,
                  message: (parsed.data.message as string) || 'Processing...',
                  insightsCount: prev[agent]?.insightsCount || 0,
                },
              }));
            }
            break;
          }

          case 'insight': {
            const agent = parsed.agent;
            if (agent) {
              const insight: Insight = {
                key: parsed.data.key as string,
                value: parsed.data.value as string,
                preview: parsed.data.preview,
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
              setAgentStates((prev) => ({
                ...prev,
                [agent]: {
                  status: 'completed',
                  displayName: prev[agent]?.displayName || config.name,
                  icon: prev[agent]?.icon || config.icon,
                  phase: prev[agent]?.phase || config.phase,
                  summary: (parsed.data.summary as string) || 'Complete',
                  insightsCount: prev[agent]?.insightsCount || 0,
                },
              }));
            }
            break;
          }

          case 'progress': {
            setProgress(parsed.data.percentage as number);
            break;
          }

          case 'error': {
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
            eventSource.close();
            setIsConnected(false);
            break;
          }

          case 'heartbeat': {
            // Just keep-alive, no action needed
            break;
          }

          // Enhanced event types - treat as insights for now
          case 'plan_ready':
          case 'competitor':
          case 'market_data':
          case 'risk':
          case 'financial':
          case 'diagram':
          case 'citation':
          case 'decision': {
            // Store as an insight for the relevant agent
            const agent = parsed.agent || 'planner';
            const insight: Insight = {
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

    // Helper to safely handle SSE events (some may not be MessageEvents)
    const safeEventHandler = (eventType: string) => (e: Event) => {
      const messageEvent = e as MessageEvent;
      // Only process if it's a MessageEvent with data
      if (messageEvent.data !== undefined && messageEvent.data !== null) {
        handleEvent(eventType, messageEvent.data);
      }
    };

    // Listen to all event types
    eventSource.addEventListener('agent_start', safeEventHandler('agent_start'));
    eventSource.addEventListener('insight', safeEventHandler('insight'));
    eventSource.addEventListener('agent_complete', safeEventHandler('agent_complete'));
    eventSource.addEventListener('progress', safeEventHandler('progress'));
    // Note: 'error' is a reserved EventSource event - use 'workflow_error' for custom errors
    eventSource.addEventListener('workflow_error', safeEventHandler('error'));
    eventSource.addEventListener('done', safeEventHandler('done'));
    eventSource.addEventListener('heartbeat', safeEventHandler('heartbeat'));

    // Enhanced event types
    eventSource.addEventListener('plan_ready', safeEventHandler('plan_ready'));
    eventSource.addEventListener('competitor', safeEventHandler('competitor'));
    eventSource.addEventListener('market_data', safeEventHandler('market_data'));
    eventSource.addEventListener('risk', safeEventHandler('risk'));
    eventSource.addEventListener('financial', safeEventHandler('financial'));
    eventSource.addEventListener('diagram', safeEventHandler('diagram'));
    eventSource.addEventListener('citation', safeEventHandler('citation'));
    eventSource.addEventListener('decision', safeEventHandler('decision'));

    // Also handle generic message events (fallback for unhandled types)
    eventSource.onmessage = (e) => {
      if (e.data !== undefined && e.data !== null) {
        handleEvent('message', e.data);
      }
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
      setIsConnected(false);
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
    error,
    events,
    agentOrder: AGENT_ORDER,
    close,
  };
}

export default useSSE;
