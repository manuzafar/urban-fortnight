/**
 * V4 Agent Card Component
 * Agent status display with transparency info
 */

import { Check, Loader2, AlertCircle } from 'lucide-react';
import { EvidenceBadge, type EvidenceTier } from './EvidenceBadge';
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
}

export function AgentCard({
  name,
  status,
  message,
  insights = [],
  isExpanded = false,
  onToggle,
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

  return (
    <div
      style={{
        background: 'var(--v4-surface)',
        border: '1px solid var(--v4-border)',
        borderRadius: 'var(--v4-radius)',
        overflow: 'hidden',
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
          borderBottom: isExpanded && insights.length > 0 ? '1px solid var(--v4-border)' : 'none',
        }}
      >
        <span style={{ color: getStatusColor() }}>{getStatusIcon()}</span>
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: '14px',
              fontWeight: 500,
              color: status === 'pending' ? 'var(--v4-text-muted)' : 'var(--v4-text)',
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
              background: 'var(--v4-bg)',
              padding: '2px 8px',
              borderRadius: '4px',
            }}
          >
            {insights.length} insights
          </span>
        )}
      </div>

      {/* Insights */}
      {isExpanded && insights.length > 0 && (
        <div style={{ padding: '12px 16px', background: 'var(--v4-bg)' }}>
          {insights.slice(0, 5).map((insight, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
                padding: '8px 0',
                borderBottom: i < insights.length - 1 ? '1px solid var(--v4-border)' : 'none',
              }}
            >
              <span
                style={{
                  width: '4px',
                  height: '4px',
                  borderRadius: '50%',
                  background: 'var(--v4-accent)',
                  marginTop: '8px',
                  flexShrink: 0,
                }}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', marginBottom: '2px' }}>
                  {insight.key}
                </div>
                <div
                  style={{
                    fontSize: '13px',
                    color: 'var(--v4-text-secondary)',
                    lineHeight: 1.4,
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
            <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', paddingTop: '8px' }}>
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
