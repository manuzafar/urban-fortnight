/**
 * V4 Evidence Badge Component
 * Displays E1-E4 evidence tier indicators
 */

import '../../styles/theme-v4.css';

export type EvidenceTier = 'E1' | 'E2' | 'E3' | 'E4';

interface EvidenceBadgeProps {
  tier: EvidenceTier;
  inline?: boolean;
  showLabel?: boolean;
}

const tierConfig: Record<EvidenceTier, { bg: string; text: string; label: string }> = {
  E1: {
    bg: 'var(--v4-e1-bg)',
    text: 'var(--v4-e1-text)',
    label: 'Validated data',
  },
  E2: {
    bg: 'var(--v4-e2-bg)',
    text: 'var(--v4-e2-text)',
    label: 'Strong inference',
  },
  E3: {
    bg: 'var(--v4-e3-bg)',
    text: 'var(--v4-e3-text)',
    label: 'Needs validation',
  },
  E4: {
    bg: 'var(--v4-e4-bg)',
    text: 'var(--v4-e4-text)',
    label: 'Hypothesis',
  },
};

export function EvidenceBadge({ tier, inline = false, showLabel = false }: EvidenceBadgeProps) {
  const config = tierConfig[tier];

  const baseStyle: React.CSSProperties = {
    display: inline ? 'inline' : 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: inline ? '1px 5px' : '2px 6px',
    background: config.bg,
    borderRadius: '3px',
    fontSize: inline ? '10px' : '10px',
    fontWeight: 600,
    color: config.text,
    marginLeft: inline ? '3px' : 0,
  };

  return (
    <span style={baseStyle}>
      {tier}
      {showLabel && <span style={{ fontWeight: 400 }}>{config.label}</span>}
    </span>
  );
}

interface EvidenceLegendProps {
  compact?: boolean;
}

export function EvidenceLegend({ compact = false }: EvidenceLegendProps) {
  const tiers: EvidenceTier[] = ['E1', 'E2', 'E3', 'E4'];

  return (
    <div
      style={{
        padding: compact ? '12px' : '16px',
        background: 'var(--v4-bg)',
        borderRadius: 'var(--v4-radius)',
      }}
    >
      <div
        style={{
          fontSize: '11px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: 'var(--v4-text-muted)',
          marginBottom: '12px',
        }}
      >
        Evidence Tiers
      </div>
      {tiers.map((tier) => (
        <div
          key={tier}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px',
            color: 'var(--v4-text-secondary)',
            marginBottom: tier !== 'E4' ? '6px' : 0,
          }}
        >
          <EvidenceBadge tier={tier} />
          <span>{tierConfig[tier].label}</span>
        </div>
      ))}
    </div>
  );
}

export default EvidenceBadge;
