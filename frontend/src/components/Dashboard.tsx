/**
 * Dashboard Component
 *
 * Main dashboard view with:
 * - History sidebar showing past sessions
 * - Large prompt input with pack type selector
 * - Recent packs grid
 */

import { useState, useEffect, useCallback } from 'react';
import {
  History,
  Plus,
  ChevronRight,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Sparkles,
  Package,
} from 'lucide-react';
import { listSessions, deleteSession, getInceptionPack } from '../api/client';
import type { InceptionPack, DiscoveryRequest } from '../types/api';
import './Dashboard.css';

export interface DashboardProps {
  onStartDiscovery: (request: DiscoveryRequest) => void;
  onViewPack: (pack: InceptionPack, sessionId: string) => void;
  isLoading: boolean;
}

type PackType = 'full' | 'research' | 'compliance' | 'technical';

const PACK_TYPES: { value: PackType; label: string; description: string }[] = [
  { value: 'full', label: 'Full Pack', description: 'Complete inception pack with all sections' },
  { value: 'research', label: 'Research Only', description: 'Customer research and market analysis' },
  { value: 'compliance', label: 'Compliance', description: 'Legal and regulatory review focus' },
  { value: 'technical', label: 'Technical', description: 'Architecture and PRD focus' },
];

interface SessionItem {
  id: string;
  status: string;
  product_idea: string;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

export function Dashboard({ onStartDiscovery, onViewPack, isLoading }: DashboardProps) {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [productIdea, setProductIdea] = useState('');
  const [packType, setPackType] = useState<PackType>('full');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [loadingPackId, setLoadingPackId] = useState<string | null>(null);

  // Fetch sessions on mount
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await listSessions();
        setSessions(response.sessions || []);
      } catch (error) {
        console.error('Failed to fetch sessions:', error);
      } finally {
        setSessionsLoading(false);
      }
    };
    fetchSessions();
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (!productIdea.trim() || productIdea.length < 10) return;

      onStartDiscovery({
        product_idea: productIdea.trim(),
        // Pack type would be used in future for different generation modes
      });
    },
    [productIdea, onStartDiscovery]
  );

  const handleDeleteSession = useCallback(async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this session?')) return;

    setDeletingId(sessionId);
    try {
      await deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (error) {
      console.error('Failed to delete session:', error);
    } finally {
      setDeletingId(null);
    }
  }, []);

  const handleViewSession = useCallback(
    async (session: SessionItem) => {
      if (session.status !== 'completed') return;

      setLoadingPackId(session.id);
      try {
        const pack = await getInceptionPack(session.id);
        onViewPack(pack, session.id);
      } catch (error) {
        console.error('Failed to load pack:', error);
      } finally {
        setLoadingPackId(null);
      }
    },
    [onViewPack]
  );

  const recentCompletedSessions = sessions
    .filter((s) => s.status === 'completed')
    .slice(0, 6);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={14} className="status-icon completed" />;
      case 'failed':
        return <XCircle size={14} className="status-icon failed" />;
      case 'in_progress':
        return <Loader2 size={14} className="status-icon in-progress spin" />;
      default:
        return <Clock size={14} className="status-icon pending" />;
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const truncate = (text: string, maxLength: number) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className={`dashboard ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* History Sidebar */}
      <aside className="dashboard-sidebar">
        <div className="sidebar-header">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <History size={18} />
            {!sidebarCollapsed && <span>History</span>}
          </button>
        </div>

        {!sidebarCollapsed && (
          <div className="sidebar-content">
            {sessionsLoading ? (
              <div className="sidebar-loading">
                <Loader2 size={20} className="spin" />
              </div>
            ) : sessions.length === 0 ? (
              <div className="sidebar-empty">
                <p>No sessions yet</p>
                <p className="muted">Your discovery sessions will appear here</p>
              </div>
            ) : (
              <ul className="session-list">
                {sessions.map((session) => (
                  <li
                    key={session.id}
                    className={`session-item ${session.status}`}
                    onClick={() => handleViewSession(session)}
                  >
                    <div className="session-status">
                      {loadingPackId === session.id ? (
                        <Loader2 size={14} className="spin" />
                      ) : (
                        getStatusIcon(session.status)
                      )}
                    </div>
                    <div className="session-info">
                      <span className="session-title">
                        {truncate(session.product_idea, 30)}
                      </span>
                      <span className="session-date">{formatDate(session.created_at)}</span>
                    </div>
                    <button
                      className="session-delete"
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      disabled={deletingId === session.id}
                      title="Delete session"
                    >
                      {deletingId === session.id ? (
                        <Loader2 size={12} className="spin" />
                      ) : (
                        <Trash2 size={12} />
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <button
              className="new-session-btn"
              onClick={() => setProductIdea('')}
            >
              <Plus size={16} />
              <span>New Discovery</span>
            </button>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="dashboard-content">
          {/* Prompt Section */}
          <section className="prompt-section">
            <div className="prompt-header">
              <Sparkles size={24} className="prompt-icon" />
              <h1>What product are you exploring?</h1>
              <p className="prompt-subtitle">
                Describe your product idea and we'll generate a comprehensive inception pack
              </p>
            </div>

            <form onSubmit={handleSubmit} className="prompt-form">
              <div className="prompt-input-wrapper">
                <textarea
                  className="prompt-textarea"
                  value={productIdea}
                  onChange={(e) => setProductIdea(e.target.value)}
                  placeholder="Describe your product idea in detail... Include target market, key features, and any constraints."
                  rows={4}
                  maxLength={5000}
                />
                <div className="prompt-meta">
                  <span className="char-count">{productIdea.length} / 5000</span>
                </div>
              </div>

              <div className="prompt-options">
                <div className="pack-type-selector">
                  <label>Pack Type</label>
                  <select
                    value={packType}
                    onChange={(e) => setPackType(e.target.value as PackType)}
                    className="pack-type-select"
                  >
                    {PACK_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  <p className="pack-type-description">
                    {PACK_TYPES.find((t) => t.value === packType)?.description}
                  </p>
                </div>

                <button
                  type="submit"
                  className="generate-btn"
                  disabled={isLoading || productIdea.length < 10}
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={18} className="spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <span>Generate Pack</span>
                      <ChevronRight size={18} />
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>

          {/* Recent Packs Section */}
          {recentCompletedSessions.length > 0 && (
            <section className="recent-section">
              <div className="recent-header">
                <Package size={18} />
                <h2>Recent Packs</h2>
              </div>

              <div className="recent-grid">
                {recentCompletedSessions.map((session) => (
                  <button
                    key={session.id}
                    className="recent-card"
                    onClick={() => handleViewSession(session)}
                    disabled={loadingPackId === session.id}
                  >
                    {loadingPackId === session.id ? (
                      <div className="card-loading">
                        <Loader2 size={24} className="spin" />
                      </div>
                    ) : (
                      <>
                        <div className="card-icon">
                          <CheckCircle size={20} />
                        </div>
                        <h3 className="card-title">
                          {truncate(session.product_idea, 40)}
                        </h3>
                        <span className="card-date">{formatDate(session.created_at)}</span>
                      </>
                    )}
                  </button>
                ))}
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
