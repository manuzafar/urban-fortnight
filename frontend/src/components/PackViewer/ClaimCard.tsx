/**
 * ClaimCard - displays a single claim with evidence tier and links.
 */

import { useState } from 'react';
import { EvidenceBadge } from './EvidenceBadge';

interface Claim {
  claim_id: string;
  section: string;
  statement: string;
  evidence_tier: string;
  confidence: number;
  source?: string;
  depends_on: string[];
  supports: string[];
  validation_method?: string;
  validation_effort?: string;
}

interface ClaimCardProps {
  claim: Claim;
  onClaimClick?: (claimId: string) => void;
  isHighlighted?: boolean;
  className?: string;
}

const EFFORT_BADGES: Record<string, { color: string; label: string }> = {
  quick: { color: 'bg-green-100 text-green-700', label: 'Quick' },
  moderate: { color: 'bg-yellow-100 text-yellow-700', label: 'Moderate' },
  significant: { color: 'bg-red-100 text-red-700', label: 'Significant' },
};

export function ClaimCard({
  claim,
  onClaimClick,
  isHighlighted = false,
  className = '',
}: ClaimCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const hasLinks = claim.depends_on.length > 0 || claim.supports.length > 0;
  const effortBadge = claim.validation_effort ? EFFORT_BADGES[claim.validation_effort] : null;

  return (
    <div
      className={`
        border rounded-lg p-4 transition-all duration-200
        ${isHighlighted ? 'border-blue-400 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-200 bg-white'}
        ${className}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-medium text-gray-700">
            {claim.claim_id}
          </span>
          <EvidenceBadge tier={claim.evidence_tier} />
        </div>
        <div className="flex items-center gap-2">
          {effortBadge && (
            <span className={`text-xs px-2 py-0.5 rounded ${effortBadge.color}`}>
              {effortBadge.label}
            </span>
          )}
          <span className="text-xs text-gray-500">
            {Math.round(claim.confidence * 100)}% conf.
          </span>
        </div>
      </div>

      {/* Statement */}
      <p className="mt-2 text-gray-800">{claim.statement}</p>

      {/* Source */}
      {claim.source && (
        <p className="mt-2 text-sm text-gray-500">
          <span className="font-medium">Source:</span>{' '}
          {claim.source.startsWith('http') ? (
            <a
              href={claim.source}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {new URL(claim.source).hostname}
            </a>
          ) : (
            claim.source
          )}
        </p>
      )}

      {/* Validation method */}
      {claim.validation_method && (
        <p className="mt-2 text-sm text-gray-600">
          <span className="font-medium">Validation:</span> {claim.validation_method}
        </p>
      )}

      {/* Links (expandable) */}
      {hasLinks && (
        <div className="mt-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <svg
              className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            {claim.depends_on.length + claim.supports.length} linked claims
          </button>

          {isExpanded && (
            <div className="mt-2 pl-4 border-l-2 border-gray-200 space-y-2">
              {claim.depends_on.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase">Depends on:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {claim.depends_on.map((id) => (
                      <button
                        key={id}
                        onClick={() => onClaimClick?.(id)}
                        className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-0.5 rounded font-mono"
                      >
                        {id}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {claim.supports.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase">Supports:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {claim.supports.map((id) => (
                      <button
                        key={id}
                        onClick={() => onClaimClick?.(id)}
                        className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-0.5 rounded font-mono"
                      >
                        {id}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Section tag */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-400">{claim.section}</span>
      </div>
    </div>
  );
}

/**
 * ClaimList - displays a list of claims with filtering.
 */
interface ClaimListProps {
  claims: Claim[];
  onClaimClick?: (claimId: string) => void;
  highlightedClaimId?: string;
  filterTier?: string;
  className?: string;
}

export function ClaimList({
  claims,
  onClaimClick,
  highlightedClaimId,
  filterTier,
  className = '',
}: ClaimListProps) {
  const filteredClaims = filterTier
    ? claims.filter((c) => c.evidence_tier === filterTier)
    : claims;

  if (filteredClaims.length === 0) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
        No claims {filterTier ? `with tier ${filterTier}` : 'available'}
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {filteredClaims.map((claim) => (
        <ClaimCard
          key={claim.claim_id}
          claim={claim}
          onClaimClick={onClaimClick}
          isHighlighted={claim.claim_id === highlightedClaimId}
        />
      ))}
    </div>
  );
}

export default ClaimCard;
