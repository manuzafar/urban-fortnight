import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SessionHistory } from './SessionHistory';
import * as api from '../api/client';
import type { SessionSummary, InceptionPack } from '../types/api';

vi.mock('../api/client');

const mockedApi = vi.mocked(api);

function makeSession(overrides: Partial<SessionSummary> = {}): SessionSummary {
  return {
    id: 'sess-1',
    status: 'completed',
    product_idea: 'AI-powered gardening app',
    progress_percentage: 100,
    created_at: '2025-06-01T12:00:00Z',
    updated_at: '2025-06-01T13:00:00Z',
    ...overrides,
  };
}

const fakePack = {
  executive_summary: { product_name: 'GardenAI' },
  metadata: { session_id: 'sess-1' },
} as unknown as InceptionPack;

describe('SessionHistory', () => {
  const onBack = vi.fn();
  const onViewPack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ─── Loading state ──────────────────────────────────────────────────
  it('renders skeleton cards while loading', () => {
    mockedApi.listSessions.mockReturnValue(new Promise(() => {})); // never resolves
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    expect(screen.getByText('My Sessions')).toBeInTheDocument();
    expect(document.querySelectorAll('.session-card-skeleton')).toHaveLength(3);
  });

  // ─── Empty state ────────────────────────────────────────────────────
  it('renders empty state when there are no sessions', async () => {
    mockedApi.listSessions.mockResolvedValue({ count: 0, sessions: [] });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => {
      expect(screen.getByText('No sessions yet')).toBeInTheDocument();
    });
    expect(screen.getByText('Start a discovery to see your sessions here.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start discovery/i })).toBeInTheDocument();
  });

  it('calls onBack when empty-state CTA is clicked', async () => {
    const user = userEvent.setup();
    mockedApi.listSessions.mockResolvedValue({ count: 0, sessions: [] });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('No sessions yet'));
    await user.click(screen.getByRole('button', { name: /start discovery/i }));
    expect(onBack).toHaveBeenCalledTimes(1);
  });

  // ─── Error state ────────────────────────────────────────────────────
  it('shows error message when fetching sessions fails', async () => {
    mockedApi.listSessions.mockRejectedValue(new Error('Network error'));
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load sessions.')).toBeInTheDocument();
    });
  });

  it('dismisses error when dismiss button is clicked', async () => {
    const user = userEvent.setup();
    mockedApi.listSessions.mockRejectedValue(new Error('fail'));
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('Failed to load sessions.'));
    await user.click(screen.getByText('Dismiss'));
    expect(screen.queryByText('Failed to load sessions.')).not.toBeInTheDocument();
  });

  // ─── Rendering sessions ────────────────────────────────────────────
  it('renders session cards with correct data', async () => {
    const sessions = [
      makeSession({ id: 's1', product_idea: 'Idea Alpha', status: 'completed' }),
      makeSession({ id: 's2', product_idea: 'Idea Beta', status: 'in_progress', progress_percentage: 45 }),
      makeSession({ id: 's3', product_idea: 'Idea Gamma', status: 'pending' }),
      makeSession({ id: 's4', product_idea: 'Idea Delta', status: 'failed' }),
    ];
    mockedApi.listSessions.mockResolvedValue({ count: 4, sessions });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => {
      expect(screen.getByText('Idea Alpha')).toBeInTheDocument();
    });

    // All four cards render
    expect(screen.getByText('Idea Beta')).toBeInTheDocument();
    expect(screen.getByText('Idea Gamma')).toBeInTheDocument();
    expect(screen.getByText('Idea Delta')).toBeInTheDocument();

    // Status badges
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  it('shows progress bar only for in-progress sessions', async () => {
    const sessions = [
      makeSession({ id: 's1', status: 'completed' }),
      makeSession({ id: 's2', status: 'in_progress', progress_percentage: 60 }),
    ];
    mockedApi.listSessions.mockResolvedValue({ count: 2, sessions });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('Completed'));

    const progressBars = document.querySelectorAll('.session-progress-bar');
    expect(progressBars).toHaveLength(1);

    const fill = document.querySelector('.session-progress-fill') as HTMLElement;
    expect(fill.style.width).toBe('60%');
  });

  it('shows View Pack button only for completed sessions', async () => {
    const sessions = [
      makeSession({ id: 's1', status: 'completed', product_idea: 'Complete' }),
      makeSession({ id: 's2', status: 'in_progress', product_idea: 'InProg' }),
      makeSession({ id: 's3', status: 'failed', product_idea: 'Fail' }),
    ];
    mockedApi.listSessions.mockResolvedValue({ count: 3, sessions });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('Complete'));

    const viewButtons = screen.getAllByText('View Pack');
    expect(viewButtons).toHaveLength(1);

    // Every card has a Delete button
    const deleteButtons = screen.getAllByText('Delete');
    expect(deleteButtons).toHaveLength(3);
  });

  // ─── View Pack ──────────────────────────────────────────────────────
  it('fetches pack and calls onViewPack when View Pack is clicked', async () => {
    const user = userEvent.setup();
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ id: 'sess-1', status: 'completed' })],
    });
    mockedApi.getSessionStatus.mockResolvedValue({
      session_id: 'sess-1',
      status: 'completed',
      current_agent: null,
      iteration: 1,
      progress_percentage: 100,
      inception_pack: fakePack,
      error_message: null,
      created_at: '2025-06-01T12:00:00Z',
      updated_at: '2025-06-01T13:00:00Z',
    });

    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('View Pack'));
    await user.click(screen.getByText('View Pack'));

    await waitFor(() => {
      expect(mockedApi.getSessionStatus).toHaveBeenCalledWith('sess-1');
      expect(onViewPack).toHaveBeenCalledWith(fakePack);
    });
  });

  it('shows error when pack is not available', async () => {
    const user = userEvent.setup();
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ id: 'sess-1', status: 'completed' })],
    });
    mockedApi.getSessionStatus.mockResolvedValue({
      session_id: 'sess-1',
      status: 'completed',
      current_agent: null,
      iteration: 1,
      progress_percentage: 100,
      inception_pack: null,
      error_message: null,
      created_at: '2025-06-01T12:00:00Z',
      updated_at: '2025-06-01T13:00:00Z',
    });

    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('View Pack'));
    await user.click(screen.getByText('View Pack'));

    await waitFor(() => {
      expect(screen.getByText('Inception pack not available for this session.')).toBeInTheDocument();
    });
    expect(onViewPack).not.toHaveBeenCalled();
  });

  it('shows error when fetching pack fails', async () => {
    const user = userEvent.setup();
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ id: 'sess-1', status: 'completed' })],
    });
    mockedApi.getSessionStatus.mockRejectedValue(new Error('Server error'));

    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('View Pack'));
    await user.click(screen.getByText('View Pack'));

    await waitFor(() => {
      expect(screen.getByText('Failed to load inception pack.')).toBeInTheDocument();
    });
  });

  it('shows Loading... text on View Pack button while fetching', async () => {
    const user = userEvent.setup();
    let resolvePack!: (value: unknown) => void;
    const packPromise = new Promise((resolve) => { resolvePack = resolve; });

    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ id: 'sess-1', status: 'completed' })],
    });
    mockedApi.getSessionStatus.mockReturnValue(packPromise as ReturnType<typeof api.getSessionStatus>);

    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('View Pack'));
    await user.click(screen.getByText('View Pack'));

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Resolve to clean up
    resolvePack({
      session_id: 'sess-1',
      status: 'completed',
      inception_pack: fakePack,
      current_agent: null,
      iteration: 1,
      progress_percentage: 100,
      error_message: null,
      created_at: '2025-06-01T12:00:00Z',
      updated_at: '2025-06-01T13:00:00Z',
    });

    await waitFor(() => {
      expect(screen.getByText('View Pack')).toBeInTheDocument();
    });
  });

  // ─── Delete ─────────────────────────────────────────────────────────
  it('deletes session after user confirms', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    mockedApi.deleteSession.mockResolvedValue(undefined);
    mockedApi.listSessions.mockResolvedValue({
      count: 2,
      sessions: [
        makeSession({ id: 's1', product_idea: 'Keep this' }),
        makeSession({ id: 's2', product_idea: 'Delete this' }),
      ],
    });

    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('Keep this'));

    const deleteButtons = screen.getAllByText('Delete');
    // Click the second card's delete button
    await user.click(deleteButtons[1]);

    expect(window.confirm).toHaveBeenCalledWith('Delete this session? This cannot be undone.');
    expect(mockedApi.deleteSession).toHaveBeenCalledWith('s2');

    await waitFor(() => {
      expect(screen.queryByText('Delete this')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Keep this')).toBeInTheDocument();
  });

  it('does not delete when user cancels confirmation', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(false);
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ id: 's1', product_idea: 'My session' })],
    });

    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('My session'));
    await user.click(screen.getByText('Delete'));

    expect(mockedApi.deleteSession).not.toHaveBeenCalled();
    expect(screen.getByText('My session')).toBeInTheDocument();
  });

  it('shows error when delete fails', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    mockedApi.deleteSession.mockRejectedValue(new Error('fail'));
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ id: 's1', product_idea: 'My session' })],
    });

    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('My session'));
    await user.click(screen.getByText('Delete'));

    await waitFor(() => {
      expect(screen.getByText('Failed to delete session.')).toBeInTheDocument();
    });
    // Card stays
    expect(screen.getByText('My session')).toBeInTheDocument();
  });

  // ─── Back button ────────────────────────────────────────────────────
  it('calls onBack when back button is clicked', async () => {
    const user = userEvent.setup();
    mockedApi.listSessions.mockResolvedValue({ count: 0, sessions: [] });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('No sessions yet'));
    await user.click(screen.getByText('Back'));
    expect(onBack).toHaveBeenCalledTimes(1);
  });

  // ─── Date formatting ───────────────────────────────────────────────
  it('formats the created_at date', async () => {
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ created_at: '2025-12-25T15:30:00Z' })],
    });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => {
      // The exact format depends on locale, but it should contain "Dec" and "25"
      const dateElements = document.querySelectorAll('.session-card-date');
      expect(dateElements).toHaveLength(1);
      const text = dateElements[0].textContent || '';
      expect(text).toContain('Dec');
      expect(text).toContain('25');
      expect(text).toContain('2025');
    });
  });

  it('shows "Unknown date" for invalid date strings', async () => {
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ created_at: 'not-a-date' })],
    });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => {
      const dateEl = document.querySelector('.session-card-date');
      expect(dateEl?.textContent).toContain('Unknown date');
    });
  });

  // ─── Status badge CSS classes ───────────────────────────────────────
  it('applies correct CSS class per status', async () => {
    const sessions = [
      makeSession({ id: 's1', status: 'completed' }),
      makeSession({ id: 's2', status: 'in_progress' }),
      makeSession({ id: 's3', status: 'pending' }),
      makeSession({ id: 's4', status: 'failed' }),
    ];
    mockedApi.listSessions.mockResolvedValue({ count: 4, sessions });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => screen.getByText('Completed'));

    expect(screen.getByText('Completed').className).toContain('session-status-completed');
    expect(screen.getByText('In Progress').className).toContain('session-status-in-progress');
    expect(screen.getByText('Pending').className).toContain('session-status-pending');
    expect(screen.getByText('Failed').className).toContain('session-status-failed');
  });

  // ─── Product idea line-clamp ────────────────────────────────────────
  it('applies clamp class to product idea', async () => {
    mockedApi.listSessions.mockResolvedValue({
      count: 1,
      sessions: [makeSession({ product_idea: 'A very long product idea that should be clamped to two lines' })],
    });
    render(<SessionHistory onBack={onBack} onViewPack={onViewPack} />);

    await waitFor(() => {
      const heading = screen.getByText('A very long product idea that should be clamped to two lines');
      expect(heading.className).toContain('session-card-idea');
    });
  });
});
