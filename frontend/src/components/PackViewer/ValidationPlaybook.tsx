/**
 * ValidationPlaybook - displays validation experiments for E4/E5 claims.
 */

import React, { useState } from 'react';
import { EvidenceBadge } from './EvidenceBadge';

interface Experiment {
  experiment_id: string;
  hypothesis_claim_id: string;
  experiment_name: string;
  target_profile: string;
  specific_instructions: string;
  success_criteria: string;
  failure_criteria: string;
  upgrade_path: string[];
  effort_level: string;
  priority: string;
  sample_size?: string;
  timeline?: string;
}

interface ValidationPlaybookProps {
  playbook: {
    experiments: Experiment[];
    prioritization_rationale?: string;
    quick_wins?: string[];
    critical_path?: string[];
  };
  onClaimClick?: (claimId: string) => void;
  className?: string;
}

const EFFORT_CONFIG: Record<string, { color: string; label: string }> = {
  quick: { color: 'bg-green-100 text-green-700 border-green-200', label: 'Quick Win' },
  moderate: { color: 'bg-yellow-100 text-yellow-700 border-yellow-200', label: 'Moderate' },
  significant: { color: 'bg-red-100 text-red-700 border-red-200', label: 'Significant' },
};

const PRIORITY_CONFIG: Record<string, { color: string; label: string; order: number }> = {
  critical: { color: 'bg-red-500 text-white', label: 'Critical', order: 1 },
  high: { color: 'bg-orange-500 text-white', label: 'High', order: 2 },
  medium: { color: 'bg-yellow-500 text-white', label: 'Medium', order: 3 },
  low: { color: 'bg-gray-400 text-white', label: 'Low', order: 4 },
};

export function ValidationPlaybook({
  playbook,
  onClaimClick,
  className = '',
}: ValidationPlaybookProps) {
  const [expandedExperiment, setExpandedExperiment] = useState<string | null>(null);
  const [filterEffort, setFilterEffort] = useState<string | null>(null);

  if (!playbook?.experiments?.length) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
        No validation experiments available
      </div>
    );
  }

  const experiments = playbook.experiments;
  const filteredExperiments = filterEffort
    ? experiments.filter((e) => e.effort_level === filterEffort)
    : experiments;

  // Sort by priority
  const sortedExperiments = [...filteredExperiments].sort((a, b) => {
    const orderA = PRIORITY_CONFIG[a.priority]?.order || 99;
    const orderB = PRIORITY_CONFIG[b.priority]?.order || 99;
    return orderA - orderB;
  });

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Validation Playbook</h3>
          <p className="text-sm text-gray-600">
            {experiments.length} experiments to validate key assumptions
          </p>
        </div>

        {/* Effort filter */}
        <div className="flex gap-2">
          <button
            onClick={() => setFilterEffort(null)}
            className={`px-3 py-1 text-sm rounded-lg border transition-colors ${
              filterEffort === null
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'
            }`}
          >
            All
          </button>
          {Object.entries(EFFORT_CONFIG).map(([key, config]) => (
            <button
              key={key}
              onClick={() => setFilterEffort(filterEffort === key ? null : key)}
              className={`px-3 py-1 text-sm rounded-lg border transition-colors ${
                filterEffort === key
                  ? config.color
                  : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'
              }`}
            >
              {config.label}
            </button>
          ))}
        </div>
      </div>

      {/* Prioritization rationale */}
      {playbook.prioritization_rationale && (
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-1">Prioritization Rationale</h4>
          <p className="text-sm text-blue-700">{playbook.prioritization_rationale}</p>
        </div>
      )}

      {/* Quick wins callout */}
      {playbook.quick_wins && playbook.quick_wins.length > 0 && (
        <div className="bg-green-50 border border-green-100 rounded-lg p-4">
          <h4 className="font-medium text-green-800 mb-2">🚀 Quick Wins</h4>
          <ul className="list-disc list-inside text-sm text-green-700 space-y-1">
            {playbook.quick_wins.map((win, i) => (
              <li key={i}>{win}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Experiments list */}
      <div className="space-y-4">
        {sortedExperiments.map((experiment) => {
          const isExpanded = expandedExperiment === experiment.experiment_id;
          const effortConfig = EFFORT_CONFIG[experiment.effort_level] || EFFORT_CONFIG.moderate;
          const priorityConfig = PRIORITY_CONFIG[experiment.priority] || PRIORITY_CONFIG.medium;

          return (
            <div
              key={experiment.experiment_id}
              className="border rounded-lg overflow-hidden bg-white"
            >
              {/* Experiment header */}
              <button
                onClick={() => setExpandedExperiment(isExpanded ? null : experiment.experiment_id)}
                className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 text-xs font-medium rounded ${priorityConfig.color}`}>
                    {priorityConfig.label}
                  </span>
                  <span className="font-medium text-gray-900">{experiment.experiment_name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onClaimClick?.(experiment.hypothesis_claim_id);
                    }}
                    className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-0.5 rounded font-mono"
                  >
                    {experiment.hypothesis_claim_id}
                  </button>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded border ${effortConfig.color}`}>
                    {effortConfig.label}
                  </span>
                  <svg
                    className={`w-5 h-5 text-gray-400 transition-transform ${
                      isExpanded ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              </button>

              {/* Experiment details */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-0 border-t border-gray-100">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    {/* Target profile */}
                    <div>
                      <h5 className="text-xs font-medium text-gray-500 uppercase mb-1">
                        Target Profile
                      </h5>
                      <p className="text-sm text-gray-800">{experiment.target_profile}</p>
                    </div>

                    {/* Sample size & timeline */}
                    {(experiment.sample_size || experiment.timeline) && (
                      <div className="flex gap-4">
                        {experiment.sample_size && (
                          <div>
                            <h5 className="text-xs font-medium text-gray-500 uppercase mb-1">
                              Sample Size
                            </h5>
                            <p className="text-sm text-gray-800">{experiment.sample_size}</p>
                          </div>
                        )}
                        {experiment.timeline && (
                          <div>
                            <h5 className="text-xs font-medium text-gray-500 uppercase mb-1">
                              Timeline
                            </h5>
                            <p className="text-sm text-gray-800">{experiment.timeline}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Instructions */}
                  <div className="mt-4">
                    <h5 className="text-xs font-medium text-gray-500 uppercase mb-1">
                      Specific Instructions
                    </h5>
                    <p className="text-sm text-gray-800 whitespace-pre-line">
                      {experiment.specific_instructions}
                    </p>
                  </div>

                  {/* Success/Failure criteria */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div className="bg-green-50 rounded-lg p-3">
                      <h5 className="text-xs font-medium text-green-700 uppercase mb-1">
                        ✓ Success Criteria
                      </h5>
                      <p className="text-sm text-green-800">{experiment.success_criteria}</p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-3">
                      <h5 className="text-xs font-medium text-red-700 uppercase mb-1">
                        ✗ Failure Criteria
                      </h5>
                      <p className="text-sm text-red-800">{experiment.failure_criteria}</p>
                    </div>
                  </div>

                  {/* Upgrade path */}
                  {experiment.upgrade_path?.length > 0 && (
                    <div className="mt-4">
                      <h5 className="text-xs font-medium text-gray-500 uppercase mb-1">
                        Claims Upgraded if Validated
                      </h5>
                      <div className="flex flex-wrap gap-1">
                        {experiment.upgrade_path.map((claimId) => (
                          <button
                            key={claimId}
                            onClick={() => onClaimClick?.(claimId)}
                            className="text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 px-2 py-1 rounded font-mono transition-colors"
                          >
                            {claimId}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {filteredExperiments.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          No experiments match the selected filter
        </div>
      )}
    </div>
  );
}

export default ValidationPlaybook;
