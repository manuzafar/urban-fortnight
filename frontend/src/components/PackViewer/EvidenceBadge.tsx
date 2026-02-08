/**
 * EvidenceBadge - displays evidence tier with color coding.
 *
 * E1 (Primary Research) - Green
 * E2 (Verified Source) - Blue
 * E3 (Industry Data) - Yellow
 * E4 (Hypothesis) - Orange
 * E5 (Assumption) - Red
 */

import React from 'react';

interface EvidenceBadgeProps {
  tier: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const TIER_CONFIG: Record<string, { color: string; bgColor: string; label: string; description: string }> = {
  E1: {
    color: 'text-green-800',
    bgColor: 'bg-green-100 border-green-200',
    label: 'E1',
    description: 'Primary Research',
  },
  E2: {
    color: 'text-blue-800',
    bgColor: 'bg-blue-100 border-blue-200',
    label: 'E2',
    description: 'Verified Source',
  },
  E3: {
    color: 'text-yellow-800',
    bgColor: 'bg-yellow-100 border-yellow-200',
    label: 'E3',
    description: 'Industry Data',
  },
  E4: {
    color: 'text-orange-800',
    bgColor: 'bg-orange-100 border-orange-200',
    label: 'E4',
    description: 'Hypothesis',
  },
  E5: {
    color: 'text-red-800',
    bgColor: 'bg-red-100 border-red-200',
    label: 'E5',
    description: 'Assumption',
  },
};

const SIZE_CLASSES = {
  sm: 'text-xs px-1.5 py-0.5',
  md: 'text-sm px-2 py-1',
  lg: 'text-base px-3 py-1.5',
};

export function EvidenceBadge({
  tier,
  showLabel = false,
  size = 'sm',
  className = '',
}: EvidenceBadgeProps) {
  const config = TIER_CONFIG[tier] || TIER_CONFIG.E4;

  return (
    <span
      className={`
        inline-flex items-center gap-1 rounded border font-medium
        ${config.bgColor} ${config.color}
        ${SIZE_CLASSES[size]}
        ${className}
      `}
      title={config.description}
    >
      <span>{config.label}</span>
      {showLabel && <span className="opacity-75">({config.description})</span>}
    </span>
  );
}

/**
 * EvidenceBadgeLegend - shows all evidence tiers with descriptions.
 */
export function EvidenceBadgeLegend({ className = '' }: { className?: string }) {
  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {Object.entries(TIER_CONFIG).map(([tier, config]) => (
        <div key={tier} className="flex items-center gap-1 text-sm">
          <EvidenceBadge tier={tier} />
          <span className="text-gray-600">{config.description}</span>
        </div>
      ))}
    </div>
  );
}

export default EvidenceBadge;
