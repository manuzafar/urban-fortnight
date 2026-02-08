/**
 * EvidenceDistributionChart - displays evidence tier distribution as a chart.
 */

import React from 'react';

interface EvidenceDistributionChartProps {
  distribution: Record<string, number>;
  totalClaims: number;
  evidenceScore: number;
  showDetails?: boolean;
  className?: string;
}

const TIER_CONFIG: Record<string, { color: string; bgColor: string; label: string; description: string; weight: number }> = {
  E1: {
    color: '#22c55e',
    bgColor: 'bg-green-500',
    label: 'E1',
    description: 'Primary Research',
    weight: 1.0,
  },
  E2: {
    color: '#3b82f6',
    bgColor: 'bg-blue-500',
    label: 'E2',
    description: 'Verified Source',
    weight: 0.85,
  },
  E3: {
    color: '#eab308',
    bgColor: 'bg-yellow-500',
    label: 'E3',
    description: 'Industry Data',
    weight: 0.6,
  },
  E4: {
    color: '#f97316',
    bgColor: 'bg-orange-500',
    label: 'E4',
    description: 'Hypothesis',
    weight: 0.3,
  },
  E5: {
    color: '#ef4444',
    bgColor: 'bg-red-500',
    label: 'E5',
    description: 'Assumption',
    weight: 0.1,
  },
};

const TIER_ORDER = ['E1', 'E2', 'E3', 'E4', 'E5'];

export function EvidenceDistributionChart({
  distribution,
  totalClaims,
  evidenceScore,
  showDetails = true,
  className = '',
}: EvidenceDistributionChartProps) {
  if (totalClaims === 0) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
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

  const getScoreLabel = (score: number) => {
    if (score >= 0.7) return 'Strong Evidence';
    if (score >= 0.5) return 'Moderate Evidence';
    if (score >= 0.3) return 'Weak Evidence';
    return 'Needs Validation';
  };

  const maxCount = Math.max(...Object.values(distribution), 1);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Score header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Evidence Distribution</h3>
          <p className="text-sm text-gray-600">{totalClaims} total claims analyzed</p>
        </div>
        <div className="text-right">
          <div className={`text-3xl font-bold ${getScoreColor(evidenceScore)}`}>
            {Math.round(evidenceScore * 100)}%
          </div>
          <div className="text-sm text-gray-500">{getScoreLabel(evidenceScore)}</div>
        </div>
      </div>

      {/* Bar chart */}
      <div className="space-y-3">
        {TIER_ORDER.map((tier) => {
          const count = distribution[tier] || 0;
          const percentage = totalClaims > 0 ? (count / totalClaims) * 100 : 0;
          const barWidth = maxCount > 0 ? (count / maxCount) * 100 : 0;
          const config = TIER_CONFIG[tier];

          return (
            <div key={tier} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-4 h-4 rounded ${config.bgColor}`}
                  />
                  <span className="font-medium">{config.label}</span>
                  <span className="text-gray-500">({config.description})</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{count}</span>
                  <span className="text-gray-400">({percentage.toFixed(1)}%)</span>
                </div>
              </div>
              <div className="h-6 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${config.bgColor} transition-all duration-500 rounded-full`}
                  style={{ width: `${barWidth}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Details section */}
      {showDetails && (
        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          {/* Grounded vs Ungrounded */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Evidence Quality</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Grounded (E1-E3)</span>
                <span className="font-medium text-green-600">
                  {(distribution['E1'] || 0) + (distribution['E2'] || 0) + (distribution['E3'] || 0)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Needs Validation (E4-E5)</span>
                <span className="font-medium text-orange-600">
                  {(distribution['E4'] || 0) + (distribution['E5'] || 0)}
                </span>
              </div>
            </div>
          </div>

          {/* Score breakdown */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Score Calculation</h4>
            <p className="text-xs text-gray-500 mb-2">
              Weighted average: E1=100%, E2=85%, E3=60%, E4=30%, E5=10%
            </p>
            <div className="text-sm">
              <span className="text-gray-600">Weighted Score: </span>
              <span className={`font-medium ${getScoreColor(evidenceScore)}`}>
                {(evidenceScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {evidenceScore < 0.5 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-medium text-yellow-800 mb-1">📋 Recommendation</h4>
          <p className="text-sm text-yellow-700">
            Evidence score is below 50%. Run validation experiments on high-priority E4/E5 claims
            before proceeding with implementation.
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * EvidenceScoreBadge - compact badge showing evidence score.
 */
interface EvidenceScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function EvidenceScoreBadge({
  score,
  size = 'md',
  className = '',
}: EvidenceScoreBadgeProps) {
  const getColor = (s: number) => {
    if (s >= 0.7) return 'bg-green-100 text-green-700 border-green-200';
    if (s >= 0.5) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    if (s >= 0.3) return 'bg-orange-100 text-orange-700 border-orange-200';
    return 'bg-red-100 text-red-700 border-red-200';
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1 rounded-full border font-medium
        ${getColor(score)}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      <span>{Math.round(score * 100)}%</span>
      <span className="opacity-75">evidence</span>
    </span>
  );
}

export default EvidenceDistributionChart;
