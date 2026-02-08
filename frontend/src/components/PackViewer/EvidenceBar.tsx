/**
 * EvidenceBar - displays evidence tier distribution as a stacked bar.
 */

import React from 'react';

interface EvidenceBarProps {
  distribution: Record<string, number>;
  totalClaims: number;
  evidenceScore: number;
  className?: string;
}

const TIER_COLORS: Record<string, string> = {
  E1: 'bg-green-500',
  E2: 'bg-blue-500',
  E3: 'bg-yellow-500',
  E4: 'bg-orange-500',
  E5: 'bg-red-500',
};

const TIER_ORDER = ['E1', 'E2', 'E3', 'E4', 'E5'];

export function EvidenceBar({
  distribution,
  totalClaims,
  evidenceScore,
  className = '',
}: EvidenceBarProps) {
  if (totalClaims === 0) {
    return (
      <div className={`text-gray-500 text-sm ${className}`}>
        No claims extracted yet
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    if (score >= 0.3) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-700">
          <span className="font-medium">{totalClaims}</span> claims
        </span>
        <span className={`font-medium ${getScoreColor(evidenceScore)}`}>
          Evidence Score: {(evidenceScore * 100).toFixed(0)}%
        </span>
      </div>

      {/* Stacked bar */}
      <div className="h-4 rounded-full overflow-hidden bg-gray-100 flex">
        {TIER_ORDER.map((tier) => {
          const count = distribution[tier] || 0;
          const percentage = (count / totalClaims) * 100;

          if (percentage === 0) return null;

          return (
            <div
              key={tier}
              className={`${TIER_COLORS[tier]} transition-all duration-300`}
              style={{ width: `${percentage}%` }}
              title={`${tier}: ${count} claims (${percentage.toFixed(1)}%)`}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs">
        {TIER_ORDER.map((tier) => {
          const count = distribution[tier] || 0;
          if (count === 0) return null;

          return (
            <div key={tier} className="flex items-center gap-1">
              <div className={`w-3 h-3 rounded ${TIER_COLORS[tier]}`} />
              <span className="text-gray-600">
                {tier}: {count}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default EvidenceBar;
