/**
 * V4 Quality Score Component
 * Displays quality score with visual bar and status
 */

import '../../styles/theme-v4.css';

interface QualityScoreProps {
  score: number;
  totalSections?: number;
  completedSections?: number;
  compact?: boolean;
}

export function QualityScore({
  score,
  totalSections = 16,
  completedSections = 16,
  compact = false,
}: QualityScoreProps) {
  const getScoreColor = () => {
    if (score >= 80) return 'var(--v4-success)';
    if (score >= 60) return 'var(--v4-warning)';
    return 'var(--v4-error)';
  };

  const getStatusLabel = () => {
    if (score >= 80) return 'Decision-ready';
    if (score >= 60) return 'Needs review';
    return 'Incomplete';
  };

  if (compact) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            fontSize: '20px',
            fontWeight: 700,
            letterSpacing: '-0.02em',
            color: getScoreColor(),
          }}
        >
          {score}%
        </span>
        <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
          {getStatusLabel()}
        </span>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', borderBottom: '1px solid var(--v4-border)' }}>
      <div
        style={{
          fontSize: '11px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: 'var(--v4-text-muted)',
          marginBottom: '8px',
        }}
      >
        Quality Score
      </div>
      <div
        style={{
          fontSize: '48px',
          fontWeight: 700,
          letterSpacing: '-0.03em',
          lineHeight: 1,
          marginBottom: '8px',
        }}
      >
        {score}%
      </div>
      <div
        style={{
          height: '4px',
          background: 'var(--v4-bg)',
          borderRadius: '2px',
          marginBottom: '8px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            background: getScoreColor(),
            borderRadius: '2px',
            width: `${score}%`,
            transition: 'width 0.3s ease',
          }}
        />
      </div>
      <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
        {getStatusLabel()} · {completedSections}/{totalSections} sections
      </div>
    </div>
  );
}

export default QualityScore;
