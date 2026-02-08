/**
 * StakeholderViewSelector - displays tailored views for different stakeholders.
 */

import React, { useState } from 'react';
import { ObjectionCard } from './ObjectionCard';

interface Objection {
  objection: string;
  response: string;
  supporting_claim_ids: string[];
}

interface StakeholderView {
  stakeholder_role: string;
  tailored_summary: string;
  key_question_answered?: string;
  key_questions_answered?: string[];  // New field from Prompt Library
  anticipated_objections: Objection[];
  evidence_confidence: string;
  key_metrics?: string[];
  key_metrics_for_role?: string[];  // New field from Prompt Library
  decision_criteria?: string[];
  decision_recommendation?: string;  // New field from Prompt Library
}

interface StakeholderViewSelectorProps {
  views: StakeholderView[];
  onClaimClick?: (claimId: string) => void;
  className?: string;
}

const ROLE_ICONS: Record<string, string> = {
  CFO: '💰',
  CISO: '🔒',
  ARB: '🏛️',
  'VP Product': '📦',
  CTO: '⚙️',
  CEO: '👔',
  'VP Engineering': '🔧',
  'VP Sales': '📈',
};

const ROLE_COLORS: Record<string, string> = {
  CFO: 'border-green-400 bg-green-50',
  CISO: 'border-red-400 bg-red-50',
  ARB: 'border-purple-400 bg-purple-50',
  'VP Product': 'border-blue-400 bg-blue-50',
  CTO: 'border-orange-400 bg-orange-50',
  CEO: 'border-gray-400 bg-gray-50',
  'VP Engineering': 'border-yellow-400 bg-yellow-50',
  'VP Sales': 'border-teal-400 bg-teal-50',
};

const CONFIDENCE_COLORS: Record<string, string> = {
  high: 'text-green-600 bg-green-100',
  medium: 'text-yellow-600 bg-yellow-100',
  low: 'text-red-600 bg-red-100',
};

export function StakeholderViewSelector({
  views,
  onClaimClick,
  className = '',
}: StakeholderViewSelectorProps) {
  const [activeView, setActiveView] = useState(0);

  if (!views?.length) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
        No stakeholder views available
      </div>
    );
  }

  const currentView = views[activeView];
  const roleColor = ROLE_COLORS[currentView.stakeholder_role] || 'border-gray-400 bg-gray-50';
  const confidenceColor = CONFIDENCE_COLORS[currentView.evidence_confidence] || CONFIDENCE_COLORS.medium;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Role selector tabs */}
      <div className="flex gap-2 flex-wrap">
        {views.map((view, index) => {
          const icon = ROLE_ICONS[view.stakeholder_role] || '👤';
          const isActive = index === activeView;

          return (
            <button
              key={view.stakeholder_role}
              onClick={() => setActiveView(index)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all
                ${isActive
                  ? ROLE_COLORS[view.stakeholder_role] || 'border-gray-400 bg-gray-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
                }
              `}
            >
              <span className="text-lg">{icon}</span>
              <span className={`font-medium ${isActive ? 'text-gray-900' : 'text-gray-600'}`}>
                {view.stakeholder_role}
              </span>
            </button>
          );
        })}
      </div>

      {/* View content */}
      <div className={`border-2 rounded-lg p-6 ${roleColor}`}>
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <span>{ROLE_ICONS[currentView.stakeholder_role] || '👤'}</span>
              {currentView.stakeholder_role} View
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Tailored briefing for {currentView.stakeholder_role} stakeholders
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${confidenceColor}`}>
            {currentView.evidence_confidence} confidence
          </span>
        </div>

        {/* Key questions - support both singular and plural field names */}
        {(currentView.key_question_answered || currentView.key_questions_answered) && (
          <div className="bg-white/80 rounded-lg p-4 mb-4">
            <h4 className="font-medium text-gray-700 mb-1">Key Questions Answered</h4>
            {currentView.key_questions_answered && currentView.key_questions_answered.length > 0 ? (
              <ul className="list-disc list-inside space-y-1">
                {currentView.key_questions_answered.map((q, i) => (
                  <li key={i} className="text-gray-800 italic">{q}</li>
                ))}
              </ul>
            ) : currentView.key_question_answered ? (
              <p className="text-gray-800 italic">"{currentView.key_question_answered}"</p>
            ) : null}
          </div>
        )}

        {/* Summary */}
        <div className="mb-6">
          <h4 className="font-medium text-gray-700 mb-2">Executive Summary</h4>
          <p className="text-gray-800 whitespace-pre-line leading-relaxed">
            {currentView.tailored_summary}
          </p>
        </div>

        {/* Key metrics - support both field names */}
        {((currentView.key_metrics && currentView.key_metrics.length > 0) ||
          (currentView.key_metrics_for_role && currentView.key_metrics_for_role.length > 0)) && (
          <div className="mb-6">
            <h4 className="font-medium text-gray-700 mb-2">Key Metrics</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {(currentView.key_metrics_for_role || currentView.key_metrics || []).map((metric, i) => (
                <div key={i} className="bg-white/80 rounded px-3 py-2 text-sm">
                  {metric}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Decision recommendation */}
        {currentView.decision_recommendation && (
          <div className="mb-6 bg-white/80 rounded-lg p-4 border-l-4 border-indigo-500">
            <h4 className="font-medium text-gray-700 mb-1">Decision Recommendation</h4>
            <p className="text-gray-800">{currentView.decision_recommendation}</p>
          </div>
        )}

        {/* Decision criteria */}
        {currentView.decision_criteria && currentView.decision_criteria.length > 0 && (
          <div className="mb-6">
            <h4 className="font-medium text-gray-700 mb-2">Decision Criteria</h4>
            <ul className="list-disc list-inside space-y-1">
              {currentView.decision_criteria.map((criterion, i) => (
                <li key={i} className="text-gray-800 text-sm">{criterion}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Objections */}
        {currentView.anticipated_objections?.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-700 mb-3">
              Anticipated Objections ({currentView.anticipated_objections.length})
            </h4>
            <div className="space-y-3">
              {currentView.anticipated_objections.map((objection, i) => (
                <ObjectionCard
                  key={i}
                  objection={objection}
                  onClaimClick={onClaimClick}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default StakeholderViewSelector;
