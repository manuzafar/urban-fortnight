/**
 * V4 Revision Indicator Component
 * Shows when quality check triggers revision loop
 */

import { RefreshCw, AlertTriangle } from 'lucide-react';
import '../../styles/theme-v4.css';

export interface RevisionState {
  isActive: boolean;
  iteration: number;
  maxIterations: number;
  agent: string;
  failedCriteria: string[];
}

interface RevisionIndicatorProps {
  state: RevisionState | null;
}

export function RevisionIndicator({ state }: RevisionIndicatorProps) {
  if (!state || !state.isActive) {
    return null;
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        padding: '14px 16px',
        background: 'var(--v4-warning-bg)',
        borderRadius: 'var(--v4-radius)',
        border: '1px solid rgba(202, 138, 4, 0.2)',
      }}
    >
      <RefreshCw
        size={18}
        style={{
          color: 'var(--v4-warning)',
          flexShrink: 0,
          animation: 'v4-spin 2s linear infinite',
        }}
      />
      <div style={{ flex: 1 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '6px',
          }}
        >
          <span
            style={{
              fontSize: '14px',
              fontWeight: 600,
              color: '#92400e',
            }}
          >
            Quality Revision {state.iteration}/{state.maxIterations}
          </span>
          <span
            style={{
              fontSize: '12px',
              padding: '2px 8px',
              background: 'rgba(202, 138, 4, 0.2)',
              color: '#78350f',
              borderRadius: '4px',
            }}
          >
            {state.agent}
          </span>
        </div>

        {state.failedCriteria.length > 0 && (
          <div style={{ marginTop: '8px' }}>
            <div
              style={{
                fontSize: '12px',
                color: '#78350f',
                marginBottom: '4px',
              }}
            >
              Improving:
            </div>
            <ul
              style={{
                margin: 0,
                paddingLeft: '18px',
                fontSize: '12px',
                color: '#92400e',
                lineHeight: 1.5,
              }}
            >
              {state.failedCriteria.slice(0, 3).map((criteria, i) => (
                <li key={i}>{criteria}</li>
              ))}
              {state.failedCriteria.length > 3 && (
                <li style={{ color: '#78350f' }}>+{state.failedCriteria.length - 3} more</li>
              )}
            </ul>
          </div>
        )}
      </div>

      <style>{`
        @keyframes v4-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

interface RevisionCompleteBannerProps {
  iteration: number;
  improvements: string[];
}

export function RevisionCompleteBanner({ iteration, improvements }: RevisionCompleteBannerProps) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        padding: '14px 16px',
        background: 'var(--v4-success-bg)',
        borderRadius: 'var(--v4-radius)',
        border: '1px solid rgba(22, 163, 74, 0.2)',
      }}
    >
      <AlertTriangle
        size={18}
        style={{
          color: 'var(--v4-success)',
          flexShrink: 0,
        }}
      />
      <div style={{ flex: 1 }}>
        <div
          style={{
            fontSize: '14px',
            fontWeight: 600,
            color: '#166534',
            marginBottom: '4px',
          }}
        >
          Revision {iteration} Complete
        </div>
        {improvements.length > 0 && (
          <div style={{ fontSize: '12px', color: '#15803d', lineHeight: 1.5 }}>
            Improved: {improvements.slice(0, 3).join(', ')}
            {improvements.length > 3 && ` +${improvements.length - 3} more`}
          </div>
        )}
      </div>
    </div>
  );
}

export default RevisionIndicator;
