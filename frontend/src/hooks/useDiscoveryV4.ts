import { useState, useEffect, useCallback } from 'react';

// Types
interface StageState {
  status: 'not_started' | 'in_progress' | 'completed' | 'approved' | 'skipped';
  output?: Record<string, unknown>;
  output_source?: 'ai_generated' | 'user_edited' | 'user_created';
  user_notes?: string;
  coaching_messages?: string[];
  score?: number;
  started_at?: string;
  completed_at?: string;
  approved_at?: string;
}

export interface Interview {
  id?: string;
  interviewee_name: string;
  interviewee_role: string;
  company_type: string;
  company_size: string;
  interview_date: string;
  story_raw: string;
  key_quote: string;
  struggling_moment: string;
  emotions: string[];
  current_workaround: string;
  desired_outcome: string;
  ai_pain_points?: string[];
  ai_triggers?: string[];
  ai_goals?: string[];
}

interface PatternSynthesis {
  pain_patterns: Array<{
    description: string;
    frequency: number;
    evidence: Array<{ interview_id: string; quote: string }>;
    severity: string;
  }>;
  trigger_patterns: Array<{
    description: string;
    frequency: number;
    evidence: Array<{ interview_id: string; quote: string }>;
  }>;
  outcome_patterns: Array<{
    description: string;
    frequency: number;
    evidence: Array<{ interview_id: string; quote: string }>;
  }>;
  contradictions: Array<{
    description: string;
    interview_a: string;
    interview_b: string;
    resolution_suggestion?: string;
  }>;
  interview_gaps: string[];
  total_interviews: number;
  evidence_quality: 'E1' | 'E2' | 'E3' | 'E4';
}

interface DiscoverySessionV4 {
  session_id: string;
  user_id: string;
  mode: 'quick' | 'guided' | 'deep';
  product_idea: string;
  industry?: string;
  target_market?: string;
  stages: Record<string, StageState>;
  interviews: Interview[];
  patterns?: PatternSynthesis;
  four_forces?: Record<string, unknown>;
  opportunity_tree?: Record<string, unknown>;
  overall_evidence_quality: 'E1' | 'E2' | 'E3' | 'E4';
  quality_score: number;
  created_at: string;
  updated_at: string;
}

interface CoachingResult {
  acknowledgment: string;
  improvements: Array<{
    area: string;
    suggestion: string;
    example?: string;
  }>;
  next_steps: string[];
  encouragement: string;
}

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Get auth token from localStorage
function getAuthToken(): string | null {
  // Try to get from Supabase session storage
  const supabaseKey = Object.keys(localStorage).find(key =>
    key.startsWith('sb-') && key.endsWith('-auth-token')
  );
  if (supabaseKey) {
    try {
      const data = JSON.parse(localStorage.getItem(supabaseKey) || '{}');
      return data.access_token || null;
    } catch {
      return null;
    }
  }
  return null;
}

// API client helper
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export function useDiscoveryV4(sessionId: string | null) {
  const [session, setSession] = useState<DiscoverySessionV4 | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Fetch session
  const fetchSession = useCallback(async () => {
    if (!sessionId) {
      setLoading(false);
      return;
    }

    try {
      const data = await apiRequest<DiscoverySessionV4>(
        `/api/discovery/v4/sessions/${sessionId}`
      );
      setSession(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch session');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Initial fetch
  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  // Polling for updates during stage execution
  useEffect(() => {
    if (!session) return;

    const hasActiveStage = Object.values(session.stages).some(
      (s) => s.status === 'in_progress'
    );

    if (hasActiveStage && !pollingInterval) {
      const interval = setInterval(fetchSession, 2000);
      setPollingInterval(interval);
    } else if (!hasActiveStage && pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }

    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [session, pollingInterval, fetchSession]);

  // Stage operations
  const runStage = useCallback(
    async (stage: string, forceRegenerate = false) => {
      if (!sessionId) return;

      await apiRequest(`/api/discovery/v4/sessions/${sessionId}/stages/${stage}/run`, {
        method: 'POST',
        body: JSON.stringify({ force_regenerate: forceRegenerate }),
      });

      await fetchSession();
    },
    [sessionId, fetchSession]
  );

  const saveStageOutput = useCallback(
    async (
      stage: string,
      output: Record<string, unknown>,
      source: 'user_edited' | 'user_created' = 'user_edited',
      notes?: string
    ) => {
      if (!sessionId) return;

      await apiRequest(`/api/discovery/v4/sessions/${sessionId}/stages/${stage}/output`, {
        method: 'PUT',
        body: JSON.stringify({ output, source, notes }),
      });

      await fetchSession();
    },
    [sessionId, fetchSession]
  );

  const approveStage = useCallback(
    async (stage: string) => {
      if (!sessionId) return;

      const result = await apiRequest<{ next_stage: string | null }>(
        `/api/discovery/v4/sessions/${sessionId}/stages/${stage}/approve`,
        { method: 'POST' }
      );

      await fetchSession();
      return result;
    },
    [sessionId, fetchSession]
  );

  const skipStage = useCallback(
    async (stage: string) => {
      if (!sessionId) return;

      await apiRequest(`/api/discovery/v4/sessions/${sessionId}/stages/${stage}/skip`, {
        method: 'POST',
      });

      await fetchSession();
    },
    [sessionId, fetchSession]
  );

  // Interview operations
  const addInterview = useCallback(
    async (interview: Interview) => {
      if (!sessionId) return;

      const result = await apiRequest<Interview>(
        `/api/discovery/v4/sessions/${sessionId}/interviews`,
        {
          method: 'POST',
          body: JSON.stringify(interview),
        }
      );

      await fetchSession();
      return result;
    },
    [sessionId, fetchSession]
  );

  const updateInterview = useCallback(
    async (interviewId: string, interview: Interview) => {
      if (!sessionId) return;

      await apiRequest(
        `/api/discovery/v4/sessions/${sessionId}/interviews/${interviewId}`,
        {
          method: 'PUT',
          body: JSON.stringify(interview),
        }
      );

      await fetchSession();
    },
    [sessionId, fetchSession]
  );

  const deleteInterview = useCallback(
    async (interviewId: string) => {
      if (!sessionId) return;

      await apiRequest(
        `/api/discovery/v4/sessions/${sessionId}/interviews/${interviewId}`,
        { method: 'DELETE' }
      );

      await fetchSession();
    },
    [sessionId, fetchSession]
  );

  const synthesizeInterviews = useCallback(async () => {
    if (!sessionId) return;

    const patterns = await apiRequest<PatternSynthesis>(
      `/api/discovery/v4/sessions/${sessionId}/interviews/synthesize`,
      { method: 'POST' }
    );

    await fetchSession();
    return patterns;
  }, [sessionId, fetchSession]);

  const getInterviewGuide = useCallback(async () => {
    if (!sessionId) return;

    return apiRequest<Record<string, unknown>>(
      `/api/discovery/v4/sessions/${sessionId}/interview-guide`
    );
  }, [sessionId]);

  // AI assistance
  const getCoaching = useCallback(
    async (stage: string, context: Record<string, unknown> = {}): Promise<CoachingResult | null> => {
      if (!sessionId) return null;

      return apiRequest<CoachingResult>(
        `/api/discovery/v4/sessions/${sessionId}/stages/${stage}/ai-assist`,
        {
          method: 'POST',
          body: JSON.stringify({
            assistance_type: 'coaching',
            context,
          }),
        }
      );
    },
    [sessionId]
  );

  const checkTarpit = useCallback(
    async (problem: string, solution?: string) => {
      if (!sessionId) return;

      const params = new URLSearchParams({ problem });
      if (solution) params.append('solution', solution);

      return apiRequest<Record<string, unknown>>(
        `/api/discovery/v4/sessions/${sessionId}/tarpit-check?${params}`,
        { method: 'POST' }
      );
    },
    [sessionId]
  );

  // Continue to full lifecycle
  const continueToStrategy = useCallback(async () => {
    if (!sessionId) return;

    return apiRequest<{ status: string; message: string }>(
      `/api/discovery/v4/sessions/${sessionId}/continue-to-strategy`,
      { method: 'POST' }
    );
  }, [sessionId]);

  // Export
  const exportDiscovery = useCallback(
    async (format: 'json' | 'pdf' | 'notion' = 'json') => {
      if (!sessionId) return;

      return apiRequest<Record<string, unknown>>(
        `/api/discovery/v4/sessions/${sessionId}/export?format=${format}`
      );
    },
    [sessionId]
  );

  return {
    session,
    loading,
    error,
    // Stage operations
    runStage,
    saveStageOutput,
    approveStage,
    skipStage,
    // Interview operations
    addInterview,
    updateInterview,
    deleteInterview,
    synthesizeInterviews,
    getInterviewGuide,
    // AI assistance
    getCoaching,
    checkTarpit,
    // Lifecycle
    continueToStrategy,
    exportDiscovery,
    // Utility
    refetch: fetchSession,
  };
}

export default useDiscoveryV4;
