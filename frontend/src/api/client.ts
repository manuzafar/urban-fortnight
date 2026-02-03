/**
 * API Client for Product Discovery Multi-Agent System
 */

import type {
  DiscoveryRequest,
  DiscoveryResponse,
  SessionStatusResponse,
  InceptionPack,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
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
export async function listSessions(): Promise<{
  count: number;
  sessions: string[];
}> {
  return fetchApi('/api/discovery/sessions');
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
