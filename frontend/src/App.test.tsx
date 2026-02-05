import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';
import * as api from './api/client';
import * as useAuthModule from './hooks/useAuth';
import type { AuthContextType } from './contexts/authTypes';
import type { User, Session } from '@supabase/supabase-js';

vi.mock('./api/client');
vi.mock('./hooks/useAuth');

const mockedApi = vi.mocked(api);
const mockedUseAuth = vi.mocked(useAuthModule.useAuth);

const fakeUser = {
  id: 'u-1',
  email: 'test@example.com',
  user_metadata: { full_name: 'Test User', avatar_url: '' },
} as unknown as User;

const fakeSession = {
  access_token: 'tok-123',
} as unknown as Session;

function setupAuth(overrides: Partial<AuthContextType> = {}) {
  mockedUseAuth.mockReturnValue({
    user: fakeUser,
    session: fakeSession,
    isLoading: false,
    signInWithGoogle: vi.fn(),
    signOut: vi.fn(),
    getAccessToken: () => 'tok-123',
    ...overrides,
  });
}

describe('App – Session History integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    mockedApi.checkHealth.mockResolvedValue({
      status: 'ok',
      timestamp: '',
      version: '',
      environment: '',
      active_sessions: 0,
    });
  });

  it('shows My Sessions nav pill when user is logged in', () => {
    setupAuth();
    render(<App />);
    expect(screen.getByText('My Sessions')).toBeInTheDocument();
  });

  it('does not show My Sessions when user is not logged in', () => {
    setupAuth({ user: null, session: null });
    render(<App />);
    expect(screen.queryByText('My Sessions')).not.toBeInTheDocument();
  });

  it('navigates to sessions page when My Sessions is clicked', async () => {
    const user = userEvent.setup();
    setupAuth();
    mockedApi.listSessions.mockResolvedValue({ count: 0, sessions: [] });
    render(<App />);

    await user.click(screen.getByText('My Sessions'));

    await waitFor(() => {
      expect(screen.getByText('No sessions yet')).toBeInTheDocument();
    });
    // The header should still be visible on the sessions page
    expect(screen.getByText('Seedcraft')).toBeInTheDocument();
  });

  it('navigates back to landing from sessions page', async () => {
    const user = userEvent.setup();
    setupAuth();
    mockedApi.listSessions.mockResolvedValue({ count: 0, sessions: [] });
    render(<App />);

    await user.click(screen.getByText('My Sessions'));
    await waitFor(() => screen.getByText('No sessions yet'));

    await user.click(screen.getByText('Back'));

    // Should be back on landing — the sessions empty state should be gone,
    // and the header "Start Discovery" button (with class btn-start) should be visible
    await waitFor(() => {
      expect(screen.queryByText('No sessions yet')).not.toBeInTheDocument();
      const headerBtn = document.querySelector('.btn-start');
      expect(headerBtn).toBeInTheDocument();
    });
  });

  it('opens completed session pack in result view', async () => {
    const user = userEvent.setup();
    setupAuth();

    const fakePack = {
      executive_summary: { product_name: 'TestProd', tagline: 'tag' },
      metadata: { session_id: 'sess-1' },
    };

    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [{
        id: 'sess-1',
        status: 'completed',
        product_idea: 'Test Idea',
        progress_percentage: 100,
        created_at: '2025-06-01T12:00:00Z',
        updated_at: '2025-06-01T13:00:00Z',
      }],
    });

    mockedApi.getSessionStatus.mockResolvedValue({
      session_id: 'sess-1',
      status: 'completed',
      current_agent: null,
      iteration: 1,
      progress_percentage: 100,
      inception_pack: fakePack as any,
      error_message: null,
      created_at: '2025-06-01T12:00:00Z',
      updated_at: '2025-06-01T13:00:00Z',
    });

    render(<App />);

    // Navigate to sessions
    await user.click(screen.getByText('My Sessions'));
    await waitFor(() => screen.getByText('Test Idea'));

    // Click View Pack
    await user.click(screen.getByText('View Pack'));

    // Should navigate to result view — the header should not be showing (result view hides it)
    await waitFor(() => {
      expect(screen.queryByText('My Sessions')).not.toBeInTheDocument();
    });
  });

  it('keeps header with My Sessions visible on sessions page', async () => {
    const user = userEvent.setup();
    setupAuth();
    mockedApi.listSessions.mockResolvedValue({ count: 0, sessions: [] });
    render(<App />);

    await user.click(screen.getByText('My Sessions'));

    // Wait for the session history page to render
    await waitFor(() => {
      expect(screen.getByText('No sessions yet')).toBeInTheDocument();
    });

    // Header should still be visible with the brand and the nav pill
    expect(screen.getByText('Seedcraft')).toBeInTheDocument();
    // "My Sessions" appears both as the nav pill and the page h1 title
    const mySessionsElements = screen.getAllByText('My Sessions');
    expect(mySessionsElements.length).toBeGreaterThanOrEqual(2);
  });
});
