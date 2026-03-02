/**
 * V4 Agent Card Component
 * Agent status display with transparency info
 */

import { Check, Loader2, AlertCircle } from 'lucide-react';
import { EvidenceBadge, type EvidenceTier } from './EvidenceBadge';
import { ThinkingDots } from './ActivityIndicator';
import '../../styles/theme-v4.css';

export interface AgentInsight {
  key: string;
  value: string;
  tier?: EvidenceTier;
}

interface AgentCardProps {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  message?: string;
  insights?: AgentInsight[];
  isExpanded?: boolean;
  onToggle?: () => void;
  showThinking?: boolean;
}

export function AgentCard({
  name,
  status,
  message,
  insights = [],
  isExpanded = false,
  onToggle,
  showThinking = false,
}: AgentCardProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'var(--v4-success)';
      case 'running':
        return 'var(--v4-accent)';
      case 'error':
        return 'var(--v4-error)';
      default:
        return 'var(--v4-text-muted)';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <Check size={16} />;
      case 'running':
        return <Loader2 size={16} className="v4-spin" />;
      case 'error':
        return <AlertCircle size={16} />;
      default:
        return null;
    }
  };

  const shouldShowThinking = showThinking && status === 'running' && insights.length === 0;

  return (
    <div
      className="v4-card"
      style={{
        overflow: 'hidden',
        transition: 'all var(--v4-transition)',
      }}
    >
      {/* Header */}
      <div
        onClick={onToggle}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '14px 16px',
          cursor: onToggle ? 'pointer' : 'default',
          borderBottom: (isExpanded && insights.length > 0) || shouldShowThinking ? '1px solid var(--v4-border-subtle)' : 'none',
          transition: 'background var(--v4-transition-fast)',
        }}
        onMouseEnter={(e) => {
          if (onToggle) e.currentTarget.style.background = 'var(--v4-bg-subtle)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'transparent';
        }}
      >
        <span style={{ color: getStatusColor(), display: 'flex', alignItems: 'center' }}>{getStatusIcon()}</span>
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: '14px',
              fontWeight: 500,
              color: status === 'pending' ? 'var(--v4-text-muted)' : 'var(--v4-text)',
              fontFamily: 'var(--v4-font-display)',
            }}
          >
            {name}
          </div>
          {message && (
            <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', marginTop: '2px' }}>
              {message}
            </div>
          )}
        </div>
        {insights.length > 0 && (
          <span
            style={{
              fontSize: '12px',
              color: 'var(--v4-text-muted)',
              background: 'var(--v4-bg-subtle)',
              padding: '3px 10px',
              borderRadius: 'var(--v4-radius-full)',
              fontWeight: 500,
            }}
          >
            {insights.length} insights
          </span>
        )}
      </div>

      {/* Thinking State */}
      {shouldShowThinking && (
        <div
          className="v4-animate-fade-in"
          style={{
            padding: '16px',
            background: 'var(--v4-bg-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <ThinkingDots text="Analyzing" />
        </div>
      )}

      {/* Insights */}
      {isExpanded && insights.length > 0 && (
        <div style={{ padding: '12px 16px', background: 'var(--v4-bg-subtle)' }}>
          {insights.slice(0, 5).map((insight, i) => (
            <div
              key={i}
              className="v4-animate-slide-up"
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
                padding: '8px 0',
                borderBottom: i < Math.min(insights.length, 5) - 1 ? '1px solid var(--v4-border-subtle)' : 'none',
                animationDelay: `${i * 50}ms`,
              }}
            >
              <span
                style={{
                  width: '5px',
                  height: '5px',
                  borderRadius: '50%',
                  background: 'var(--v4-accent)',
                  marginTop: '7px',
                  flexShrink: 0,
                }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', marginBottom: '3px', fontWeight: 500 }}>
                  {insight.key}
                </div>
                <div
                  style={{
                    fontSize: '13px',
                    color: 'var(--v4-text-secondary)',
                    lineHeight: 1.5,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                  }}
                >
                  {insight.value}
                  {insight.tier && <EvidenceBadge tier={insight.tier} inline />}
                </div>
              </div>
            </div>
          ))}
          {insights.length > 5 && (
            <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', paddingTop: '8px', fontWeight: 500 }}>
              +{insights.length - 5} more insights
            </div>
          )}
        </div>
      )}

      <style>{`
        .v4-spin {
          animation: v4-spin 1s linear infinite;
        }
        @keyframes v4-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default AgentCard;
