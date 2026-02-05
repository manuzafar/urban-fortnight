import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { listSessions, deleteSession, setAuthToken } from './client';
import type { SessionListResponse } from '../types/api';

const originalFetch = globalThis.fetch;

describe('API client', () => {
  beforeEach(() => {
    setAuthToken('test-token');
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    setAuthToken(null);
  });

  describe('listSessions', () => {
    it('returns SessionListResponse with typed sessions', async () => {
      const mockResponse: SessionListResponse = {
        count: 2,
        sessions: [
          {
            id: 'sess-1',
            status: 'completed',
            product_idea: 'Test idea 1',
            progress_percentage: 100,
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-01T01:00:00Z',
          },
          {
            id: 'sess-2',
            status: 'in_progress',
            product_idea: 'Test idea 2',
            progress_percentage: 45,
            created_at: '2025-01-02T00:00:00Z',
            updated_at: '2025-01-02T01:00:00Z',
          },
        ],
      };

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await listSessions();

      expect(result.count).toBe(2);
      expect(result.sessions).toHaveLength(2);
      expect(result.sessions[0].id).toBe('sess-1');
      expect(result.sessions[0].product_idea).toBe('Test idea 1');
      expect(result.sessions[0].status).toBe('completed');
      expect(result.sessions[1].progress_percentage).toBe(45);
    });

    it('sends Authorization header when token is set', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ count: 0, sessions: [] }),
      });

      await listSessions();

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/discovery/sessions'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        }),
      );
    });

    it('normalises old format (string IDs) by fetching each session', async () => {
      // First call: listSessions returns string IDs
      // Subsequent calls: getSessionStatus for each ID
      let callCount = 0;
      globalThis.fetch = vi.fn().mockImplementation((url: string) => {
        callCount++;
        if (callCount === 1) {
          // /api/discovery/sessions — old format
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ count: 2, sessions: ['sess-a', 'sess-b'] }),
          });
        }
        // /api/discovery/session/{id} — status responses
        const id = url.includes('sess-a') ? 'sess-a' : 'sess-b';
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            session_id: id,
            status: id === 'sess-a' ? 'completed' : 'in_progress',
            current_agent: null,
            iteration: 1,
            progress_percentage: id === 'sess-a' ? 100 : 40,
            inception_pack: id === 'sess-a'
              ? { executive_summary: { product_name: 'Cool Product' } }
              : null,
            error_message: null,
            created_at: '2025-06-01T12:00:00Z',
            updated_at: '2025-06-01T13:00:00Z',
          }),
        });
      });

      const result = await listSessions();

      expect(result.count).toBe(2);
      expect(result.sessions[0].id).toBe('sess-a');
      expect(result.sessions[0].product_idea).toBe('Cool Product');
      expect(result.sessions[0].status).toBe('completed');
      expect(result.sessions[1].id).toBe('sess-b');
      expect(result.sessions[1].product_idea).toBe('sess-b'); // falls back to ID
      expect(result.sessions[1].progress_percentage).toBe(40);
    });

    it('handles fetch failure for individual sessions in old format', async () => {
      let callCount = 0;
      globalThis.fetch = vi.fn().mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ count: 1, sessions: ['sess-fail'] }),
          });
        }
        // Session detail fetch fails
        return Promise.resolve({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          json: () => Promise.resolve({ detail: 'Server error' }),
        });
      });

      const result = await listSessions();

      expect(result.count).toBe(1);
      expect(result.sessions[0].id).toBe('sess-fail');
      expect(result.sessions[0].product_idea).toBe('sess-fail');
      expect(result.sessions[0].status).toBe('pending');
    });

    it('throws on non-ok response', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: () => Promise.resolve({ detail: 'Not authenticated' }),
      });

      await expect(listSessions()).rejects.toThrow('Not authenticated');
    });
  });

  describe('deleteSession', () => {
    it('sends DELETE request with session id', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({}),
      });

      await deleteSession('sess-123');

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/discovery/session/sess-123'),
        expect.objectContaining({ method: 'DELETE' }),
      );
    });

    it('throws on failure', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ detail: 'Session not found' }),
      });

      await expect(deleteSession('sess-bad')).rejects.toThrow('Session not found');
    });
  });
});
