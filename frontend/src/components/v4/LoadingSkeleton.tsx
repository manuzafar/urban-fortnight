/**
 * V4 Loading Skeleton Component
 * Shimmer effect placeholder for loading content
 */

import '../../styles/theme-v4.css';

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  className?: string;
}

export function Skeleton({ width = '100%', height = '20px', borderRadius = 'var(--v4-radius)', className = '' }: SkeletonProps) {
  return (
    <div
      className={`v4-shimmer ${className}`}
      style={{
        width,
        height,
        borderRadius,
      }}
    />
  );
}

interface SkeletonTextProps {
  lines?: number;
  className?: string;
}

export function SkeletonText({ lines = 3, className = '' }: SkeletonTextProps) {
  return (
    <div className={className} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height="14px"
          width={i === lines - 1 ? '70%' : '100%'}
        />
      ))}
    </div>
  );
}

interface SkeletonCardProps {
  hasHeader?: boolean;
  hasImage?: boolean;
  lines?: number;
}

export function SkeletonCard({ hasHeader = true, hasImage = false, lines = 3 }: SkeletonCardProps) {
  return (
    <div
      className="v4-card v4-animate-fade-in"
      style={{
        padding: 'var(--v4-space-5)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--v4-space-4)',
      }}
    >
      {hasImage && (
        <Skeleton height="120px" borderRadius="var(--v4-radius-md)" />
      )}
      {hasHeader && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--v4-space-3)' }}>
          <Skeleton width="40px" height="40px" borderRadius="50%" />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <Skeleton height="14px" width="60%" />
            <Skeleton height="12px" width="40%" />
          </div>
        </div>
      )}
      <SkeletonText lines={lines} />
    </div>
  );
}

interface InsightSkeletonProps {
  count?: number;
}

export function InsightSkeleton({ count = 3 }: InsightSkeletonProps) {
  return (
    <div
      className="v4-card v4-animate-fade-in"
      style={{
        overflow: 'hidden',
      }}
    >
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 'var(--v4-space-3)',
            padding: 'var(--v4-space-3) var(--v4-space-4)',
            borderBottom: i < count - 1 ? '1px solid var(--v4-border-subtle)' : 'none',
          }}
        >
          <Skeleton width="6px" height="6px" borderRadius="50%" />
          <div style={{ flex: 1 }}>
            <Skeleton height="12px" width="30%" />
            <div style={{ marginTop: '8px' }}>
              <Skeleton height="14px" width="90%" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

interface AgentSkeletonProps {
  showInsights?: boolean;
}

export function AgentSkeleton({ showInsights = true }: AgentSkeletonProps) {
  return (
    <div className="v4-card v4-animate-fade-in">
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--v4-space-3)',
          padding: 'var(--v4-space-4) var(--v4-space-4)',
          borderBottom: showInsights ? '1px solid var(--v4-border-subtle)' : 'none',
        }}
      >
        <Skeleton width="24px" height="24px" borderRadius="50%" />
        <div style={{ flex: 1 }}>
          <Skeleton height="14px" width="40%" />
          <div style={{ marginTop: '6px' }}>
            <Skeleton height="12px" width="60%" />
          </div>
        </div>
        <Skeleton width="60px" height="20px" borderRadius="var(--v4-radius-sm)" />
      </div>
      {showInsights && (
        <div style={{ padding: 'var(--v4-space-3) var(--v4-space-4)', background: 'var(--v4-bg-subtle)' }}>
          {Array.from({ length: 2 }).map((_, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 'var(--v4-space-2)',
                padding: 'var(--v4-space-2) 0',
              }}
            >
              <Skeleton width="4px" height="4px" borderRadius="50%" />
              <div style={{ flex: 1 }}>
                <Skeleton height="12px" width="25%" />
                <div style={{ marginTop: '4px' }}>
                  <Skeleton height="13px" width="80%" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface LoadingSkeletonProps {
  variant?: 'card' | 'text' | 'insight' | 'agent';
  count?: number;
}

export function LoadingSkeleton({ variant = 'card', count = 1 }: LoadingSkeletonProps) {
  const items = Array.from({ length: count });

  switch (variant) {
    case 'text':
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--v4-space-4)' }}>
          {items.map((_, i) => (
            <SkeletonText key={i} lines={3} />
          ))}
        </div>
      );
    case 'insight':
      return <InsightSkeleton count={count} />;
    case 'agent':
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--v4-space-4)' }}>
          {items.map((_, i) => (
            <AgentSkeleton key={i} />
          ))}
        </div>
      );
    case 'card':
    default:
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--v4-space-4)' }}>
          {items.map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      );
  }
}

export default LoadingSkeleton;
