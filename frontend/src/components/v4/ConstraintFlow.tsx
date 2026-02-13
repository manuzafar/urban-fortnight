/**
 * V4 Constraint Flow Component
 * Shows how outputs from one phase influence downstream agents
 */

import { ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import '../../styles/theme-v4.css';

export interface ConstraintFlowItem {
  id: string;
  fromAgent: string;
  fromPhase: string;
  toAgents: string[];
  toPhase: string;
  constraintType: string;
  summary: string;
  timestamp: string;
}

interface ConstraintFlowProps {
  items: ConstraintFlowItem[];
  maxVisible?: number;
}

export function ConstraintFlow({ items, maxVisible = 5 }: ConstraintFlowProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (items.length === 0) {
    return null;
  }

  const visibleItems = isExpanded ? items : items.slice(-maxVisible);
  const hiddenCount = items.length - maxVisible;

  return (
    <div
      style={{
        background: 'var(--v4-surface)',
        border: '1px solid var(--v4-border)',
        borderRadius: 'var(--v4-radius)',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          borderBottom: '1px solid var(--v4-border)',
          background: 'var(--v4-bg)',
        }}
      >
        <div
          style={{
            fontSize: '11px',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: 'var(--v4-text-muted)',
          }}
        >
          Constraint Flow
        </div>
        <span
          style={{
            fontSize: '12px',
            color: 'var(--v4-text-muted)',
            background: 'var(--v4-surface)',
            padding: '2px 8px',
            borderRadius: '4px',
          }}
        >
          {items.length} constraints
        </span>
      </div>

      <div style={{ padding: '12px 16px' }}>
        {hiddenCount > 0 && !isExpanded && (
          <button
            onClick={() => setIsExpanded(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              width: '100%',
              padding: '8px',
              marginBottom: '8px',
              fontSize: '12px',
              color: 'var(--v4-text-muted)',
              background: 'var(--v4-bg)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            <ChevronUp size={14} />
            Show {hiddenCount} earlier constraints
          </button>
        )}

        {visibleItems.map((item, i) => (
          <div
            key={item.id}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              padding: '10px 0',
              borderBottom: i < visibleItems.length - 1 ? '1px solid var(--v4-border)' : 'none',
            }}
          >
            {/* Flow indicator */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
              <span
                style={{
                  padding: '2px 6px',
                  background: 'var(--v4-info-bg)',
                  color: 'var(--v4-info)',
                  borderRadius: '3px',
                  fontWeight: 500,
                }}
              >
                {item.fromPhase}
              </span>
              <ArrowRight size={14} style={{ color: 'var(--v4-text-muted)' }} />
              <span
                style={{
                  padding: '2px 6px',
                  background: 'var(--v4-accent-light)',
                  color: 'var(--v4-accent)',
                  borderRadius: '3px',
                  fontWeight: 500,
                }}
              >
                {item.toPhase}
              </span>
            </div>

            {/* Summary */}
            <div style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', lineHeight: 1.5 }}>
              <span style={{ fontWeight: 500, color: 'var(--v4-text)' }}>{item.fromAgent}</span>
              {' → '}
              {item.toAgents.length > 2
                ? `${item.toAgents.slice(0, 2).join(', ')} +${item.toAgents.length - 2}`
                : item.toAgents.join(', ')}
              : {item.summary}
            </div>

            {/* Constraint type badge */}
            <div style={{ display: 'flex', gap: '6px', marginTop: '2px' }}>
              <span
                style={{
                  fontSize: '10px',
                  fontWeight: 500,
                  textTransform: 'uppercase',
                  padding: '2px 6px',
                  background: 'var(--v4-bg)',
                  color: 'var(--v4-text-muted)',
                  borderRadius: '3px',
                }}
              >
                {item.constraintType}
              </span>
            </div>
          </div>
        ))}

        {isExpanded && hiddenCount > 0 && (
          <button
            onClick={() => setIsExpanded(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              width: '100%',
              padding: '8px',
              marginTop: '8px',
              fontSize: '12px',
              color: 'var(--v4-text-muted)',
              background: 'var(--v4-bg)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            <ChevronDown size={14} />
            Show less
          </button>
        )}
      </div>
    </div>
  );
}

export default ConstraintFlow;
