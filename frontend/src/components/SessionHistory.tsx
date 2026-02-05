import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Eye, Trash2, Clock, PackageOpen } from 'lucide-react';
import { listSessions, getSessionStatus, deleteSession } from '../api/client';
import type { SessionSummary, InceptionPack, SessionStatus } from '../types/api';

interface SessionHistoryProps {
  onBack: () => void;
  onViewPack: (pack: InceptionPack) => void;
}

const STATUS_LABELS: Record<SessionStatus, string> = {
  completed: 'Completed',
  in_progress: 'In Progress',
  pending: 'Pending',
  failed: 'Failed',
};

const STATUS_CLASSES: Record<SessionStatus, string> = {
  completed: 'session-status-completed',
  in_progress: 'session-status-in-progress',
  pending: 'session-status-pending',
  failed: 'session-status-failed',
};

function formatDate(iso: string): string {
  const date = new Date(iso);
  if (isNaN(date.getTime())) return 'Unknown date';
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

export function SessionHistory({ onBack, onViewPack }: SessionHistoryProps) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingPackId, setLoadingPackId] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listSessions();
      setSessions(data.sessions);
    } catch {
      setError('Failed to load sessions.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleViewPack = useCallback(
    async (sessionId: string) => {
      setLoadingPackId(sessionId);
      try {
        const status = await getSessionStatus(sessionId);
        if (status.inception_pack) {
          onViewPack(status.inception_pack as InceptionPack);
        } else {
          setError('Inception pack not available for this session.');
        }
      } catch {
        setError('Failed to load inception pack.');
      } finally {
        setLoadingPackId(null);
      }
    },
    [onViewPack],
  );

  const handleDelete = useCallback(
    async (sessionId: string) => {
      if (!window.confirm('Delete this session? This cannot be undone.')) return;
      try {
        await deleteSession(sessionId);
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      } catch {
        setError('Failed to delete session.');
      }
    },
    [],
  );

  // Loading skeleton
  if (loading) {
    return (
      <div className="session-history">
        <div className="session-history-header">
          <button className="session-back-btn" onClick={onBack}>
            <ArrowLeft size={18} />
            Back
          </button>
          <h1 className="session-history-title">My Sessions</h1>
        </div>
        <div className="session-grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="session-card session-card-skeleton">
              <div className="skeleton-line skeleton-title" />
              <div className="skeleton-line skeleton-short" />
              <div className="skeleton-line skeleton-bar" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="session-history">
      <div className="session-history-header">
        <button className="session-back-btn" onClick={onBack}>
          <ArrowLeft size={18} />
          Back
        </button>
        <h1 className="session-history-title">My Sessions</h1>
      </div>

      {error && (
        <div className="session-error">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="session-empty">
          <PackageOpen size={48} strokeWidth={1.5} />
          <h2>No sessions yet</h2>
          <p>Start a discovery to see your sessions here.</p>
          <button className="btn-start" onClick={onBack}>
            Start Discovery
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M6 12l4-4-4-4" />
            </svg>
          </button>
        </div>
      ) : (
        <div className="session-grid">
          {sessions.map((s) => (
            <div key={s.id} className="session-card">
              <div className="session-card-top">
                <span className={`session-status-badge ${STATUS_CLASSES[s.status]}`}>
                  {STATUS_LABELS[s.status]}
                </span>
                <div className="session-card-date">
                  <Clock size={13} />
                  {formatDate(s.created_at)}
                </div>
              </div>

              <h3 className="session-card-idea">{s.product_idea}</h3>

              {s.status === 'in_progress' && (
                <div className="session-progress-bar">
                  <div
                    className="session-progress-fill"
                    style={{ width: `${s.progress_percentage}%` }}
                  />
                </div>
              )}

              <div className="session-card-actions">
                {s.status === 'completed' && (
                  <button
                    className="session-action-btn session-action-view"
                    onClick={() => handleViewPack(s.id)}
                    disabled={loadingPackId === s.id}
                  >
                    <Eye size={15} />
                    {loadingPackId === s.id ? 'Loading...' : 'View Pack'}
                  </button>
                )}
                <button
                  className="session-action-btn session-action-delete"
                  onClick={() => handleDelete(s.id)}
                >
                  <Trash2 size={15} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
