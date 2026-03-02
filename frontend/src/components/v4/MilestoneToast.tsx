/**
 * V4 Milestone Toast Component
 * Brief celebration toasts at progress milestones
 */

import { useState, useEffect, useCallback } from 'react';
import { CheckCircle, Sparkles, Target, Award, Rocket } from 'lucide-react';
import '../../styles/theme-v4.css';

interface Milestone {
  progress: number;
  title: string;
  description: string;
  icon: 'check' | 'sparkle' | 'target' | 'award' | 'rocket';
}

const DEFAULT_MILESTONES: Milestone[] = [
  { progress: 25, title: 'Discovery Complete', description: 'Market research gathered', icon: 'check' },
  { progress: 50, title: 'Strategy Defined', description: 'Business model built', icon: 'target' },
  { progress: 75, title: 'Requirements Ready', description: 'Product spec finalized', icon: 'sparkle' },
  { progress: 100, title: 'Pack Complete!', description: 'Your inception pack is ready', icon: 'rocket' },
];

interface MilestoneToastProps {
  progress: number;
  milestones?: Milestone[];
  duration?: number;
}

export function MilestoneToast({
  progress,
  milestones = DEFAULT_MILESTONES,
  duration = 3000,
}: MilestoneToastProps) {
  const [visibleMilestone, setVisibleMilestone] = useState<Milestone | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [shownMilestones, setShownMilestones] = useState<Set<number>>(new Set());

  const showMilestone = useCallback((milestone: Milestone) => {
    setVisibleMilestone(milestone);
    setIsAnimating(true);

    setTimeout(() => {
      setIsAnimating(false);
    }, duration - 300);

    setTimeout(() => {
      setVisibleMilestone(null);
    }, duration);
  }, [duration]);

  useEffect(() => {
    // Check if we've crossed a milestone
    const milestone = milestones.find(
      (m) => progress >= m.progress && !shownMilestones.has(m.progress)
    );

    if (milestone) {
      setShownMilestones((prev) => new Set([...prev, milestone.progress]));
      showMilestone(milestone);
    }
  }, [progress, milestones, shownMilestones, showMilestone]);

  if (!visibleMilestone) return null;

  const getIcon = () => {
    switch (visibleMilestone.icon) {
      case 'check':
        return <CheckCircle size={20} />;
      case 'sparkle':
        return <Sparkles size={20} />;
      case 'target':
        return <Target size={20} />;
      case 'award':
        return <Award size={20} />;
      case 'rocket':
        return <Rocket size={20} />;
      default:
        return <CheckCircle size={20} />;
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        zIndex: 1000,
        animation: isAnimating
          ? 'v4-slide-up 0.3s ease forwards'
          : 'v4-fade-out 0.3s ease forwards',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 16px',
          background: 'var(--v4-surface)',
          border: '1px solid var(--v4-border)',
          borderRadius: 'var(--v4-radius-lg)',
          boxShadow: 'var(--v4-shadow-lg)',
        }}
      >
        <div
          style={{
            width: '36px',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--v4-success-light)',
            borderRadius: '50%',
            color: 'var(--v4-success)',
          }}
        >
          {getIcon()}
        </div>
        <div>
          <div
            style={{
              fontSize: '14px',
              fontWeight: 600,
              color: 'var(--v4-text)',
              fontFamily: 'var(--v4-font-display)',
            }}
          >
            {visibleMilestone.title}
          </div>
          <div
            style={{
              fontSize: '12px',
              color: 'var(--v4-text-muted)',
              marginTop: '2px',
            }}
          >
            {visibleMilestone.description}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes v4-fade-out {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(8px); }
        }
      `}</style>
    </div>
  );
}

interface ProgressMilestoneIndicatorProps {
  progress: number;
  milestones?: number[];
}

export function ProgressMilestoneIndicator({
  progress,
  milestones = [25, 50, 75, 100],
}: ProgressMilestoneIndicatorProps) {
  return (
    <div style={{ position: 'relative', height: '12px' }}>
      {/* Progress bar track */}
      <div
        style={{
          position: 'absolute',
          top: '4px',
          left: 0,
          right: 0,
          height: '4px',
          background: 'var(--v4-bg-subtle)',
          borderRadius: '2px',
        }}
      />
      {/* Progress bar fill */}
      <div
        style={{
          position: 'absolute',
          top: '4px',
          left: 0,
          width: `${progress}%`,
          height: '4px',
          background: 'linear-gradient(90deg, var(--v4-accent), var(--v4-accent-hover))',
          borderRadius: '2px',
          transition: 'width 0.5s ease-out',
        }}
      />
      {/* Milestone markers */}
      {milestones.map((milestone) => (
        <div
          key={milestone}
          style={{
            position: 'absolute',
            left: `${milestone}%`,
            top: 0,
            transform: 'translateX(-50%)',
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: progress >= milestone ? 'var(--v4-accent)' : 'var(--v4-surface)',
            border: `2px solid ${progress >= milestone ? 'var(--v4-accent)' : 'var(--v4-border)'}`,
            transition: 'all 0.3s ease',
          }}
        >
          {progress >= milestone && (
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '4px',
                height: '4px',
                borderRadius: '50%',
                background: 'white',
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
}

export default MilestoneToast;
