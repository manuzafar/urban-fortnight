/**
 * ObjectionCard - displays an anticipated objection with response and claim links.
 */

import { useState } from 'react';

interface Objection {
  objection: string;
  response: string;
  supporting_claim_ids: string[];
}

interface ObjectionCardProps {
  objection: Objection;
  onClaimClick?: (claimId: string) => void;
  className?: string;
}

export function ObjectionCard({
  objection,
  onClaimClick,
  className = '',
}: ObjectionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
      {/* Objection header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-start justify-between text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-start gap-3">
          <span className="text-red-500 text-lg mt-0.5">⚠️</span>
          <span className="font-medium text-gray-800">{objection.objection}</span>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ${
            isExpanded ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Response (expandable) */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-0 border-t border-gray-100">
          <div className="mt-3">
            <div className="flex items-start gap-3">
              <span className="text-green-500 text-lg">✓</span>
              <div className="flex-1">
                <span className="text-xs font-medium text-gray-500 uppercase">Response</span>
                <p className="text-gray-700 mt-1">{objection.response}</p>
              </div>
            </div>
          </div>

          {/* Supporting claims */}
          {objection.supporting_claim_ids?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <span className="text-xs font-medium text-gray-500">Supporting Evidence:</span>
              <div className="flex flex-wrap gap-1 mt-2">
                {objection.supporting_claim_ids.map((claimId) => (
                  <button
                    key={claimId}
                    onClick={(e) => {
                      e.stopPropagation();
                      onClaimClick?.(claimId);
                    }}
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
}

/**
 * ObjectionList - displays a list of objections.
 */
interface ObjectionListProps {
  objections: Objection[];
  onClaimClick?: (claimId: string) => void;
  className?: string;
}

export function ObjectionList({
  objections,
  onClaimClick,
  className = '',
}: ObjectionListProps) {
  if (!objections?.length) {
    return (
      <div className={`p-4 text-center text-gray-500 text-sm ${className}`}>
        No objections identified
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {objections.map((objection, index) => (
        <ObjectionCard
          key={index}
          objection={objection}
          onClaimClick={onClaimClick}
        />
      ))}
    </div>
  );
}

export default ObjectionCard;
