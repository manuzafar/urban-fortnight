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
