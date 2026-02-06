/**
 * API Client for Product Discovery Multi-Agent System
 */

import type {
  DiscoveryRequest,
  DiscoveryResponse,
  SessionStatusResponse,
  SessionListResponse,
  InceptionPack,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Module-level auth token, set by App.tsx when session changes
let _authToken: string | null = null;

/**
 * Set the auth token for API requests.
 * Called from App.tsx whenever the Supabase session changes.
 */
export function setAuthToken(token: string | null) {
  _authToken = token;
}

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  status: number;
  statusText: string;

  constructor(status: number, statusText: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
  }
}

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (_authToken) {
    headers['Authorization'] = `Bearer ${_authToken}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      response.statusText,
      errorData.detail || errorData.message || 'An error occurred'
    );
  }

  return response.json();
}

/**
 * Health check endpoint
 */
export async function checkHealth(): Promise<{
  status: string;
  timestamp: string;
  version: string;
  environment: string;
  active_sessions: number;
}> {
  return fetchApi('/api/health');
}

/**
 * Start a new product discovery session
 */
export async function startDiscovery(
  request: DiscoveryRequest
): Promise<DiscoveryResponse> {
  return fetchApi('/api/discovery/start', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Get the status of a discovery session
 */
export async function getSessionStatus(
  sessionId: string
): Promise<SessionStatusResponse> {
  return fetchApi(`/api/discovery/session/${sessionId}`);
}

/**
 * Get just the inception pack for a completed session
 */
export async function getInceptionPack(
  sessionId: string
): Promise<InceptionPack> {
  return fetchApi(`/api/discovery/session/${sessionId}/pack`);
}

/**
 * Delete a discovery session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await fetchApi(`/api/discovery/session/${sessionId}`, {
    method: 'DELETE',
  });
}

/**
 * List all active sessions
 */
export async function listSessions(): Promise<SessionListResponse> {
  const raw = await fetchApi<{ count: number; sessions: (string | SessionListResponse['sessions'][number])[] }>('/api/discovery/sessions');

  // Backend may return plain ID strings (old format) or full objects (new format).
  // Normalise to full objects by fetching details for any string entries.
  if (raw.sessions.length === 0 || typeof raw.sessions[0] !== 'string') {
    return raw as SessionListResponse;
  }

  const ids = raw.sessions as string[];
  const detailed = await Promise.all(
    ids.map(async (id) => {
      try {
        const s = await getSessionStatus(id);
        // product_idea is not in SessionStatusResponse, so derive a title:
        // use the product name from the inception pack, or fall back to the session ID.
        const packName = s.inception_pack?.executive_summary?.product_name;
        return {
          id: s.session_id,
          status: s.status,
          product_idea: packName || s.session_id,
          progress_percentage: s.progress_percentage,
          created_at: s.created_at,
          updated_at: s.updated_at,
        };
      } catch {
        return {
          id,
          status: 'pending' as const,
          product_idea: id,
          progress_percentage: 0,
          created_at: '',
          updated_at: '',
        };
      }
    }),
  );

  return { count: detailed.length, sessions: detailed };
}

/**
 * Poll session status until completion or failure
 */
export function pollSessionStatus(
  sessionId: string,
  onUpdate: (status: SessionStatusResponse) => void,
  intervalMs: number = 3000
): () => void {
  let isPolling = true;

  const poll = async () => {
    while (isPolling) {
      try {
        const status = await getSessionStatus(sessionId);
        onUpdate(status);

        if (status.status === 'completed' || status.status === 'failed') {
          isPolling = false;
          break;
        }
      } catch (error) {
        console.error('Polling error:', error);
      }

      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
  };

  poll();

  // Return cleanup function
  return () => {
    isPolling = false;
  };
}

/**
 * Export inception pack as PDF
 */
export async function exportPdf(
  sessionId: string,
  section?: string
): Promise<Blob> {
  const url = `${API_BASE_URL}/api/discovery/session/${sessionId}/export/pdf${section ? `?section=${section}` : ''}`;

  const headers: Record<string, string> = {};
  if (_authToken) {
    headers['Authorization'] = `Bearer ${_authToken}`;
  }

  const response = await fetch(url, { headers });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      response.statusText,
      errorData.detail || errorData.message || 'Failed to export PDF'
    );
  }

  return response.blob();
}

/**
 * Export inception pack as DOCX
 */
export async function exportDocx(
  sessionId: string,
  section?: string
): Promise<Blob> {
  const url = `${API_BASE_URL}/api/discovery/session/${sessionId}/export/docx${section ? `?section=${section}` : ''}`;

  const headers: Record<string, string> = {};
  if (_authToken) {
    headers['Authorization'] = `Bearer ${_authToken}`;
  }

  const response = await fetch(url, { headers });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      response.statusText,
      errorData.detail || errorData.message || 'Failed to export DOCX'
    );
  }

  return response.blob();
}
