import { useEffect, useState } from 'react';
import type { SessionStatusResponse } from '../types/api';

interface ProgressTrackerProps {
  session: SessionStatusResponse;
  onCancel?: () => void;
}

const PHASES = [
  { id: 'customer_research', name: 'Establishing market context', description: 'Customer research & evidence gathering' },
  { id: 'business_strategy', name: 'Mapping competitive landscape', description: 'Industry analysis & positioning' },
  { id: 'product_requirements', name: 'Pressure-testing business model', description: 'Lean Canvas & financial projections' },
  { id: 'technical_architect', name: 'Structuring product decisions', description: 'PRD, epics & user stories' },
  { id: 'critique', name: 'Designing technical foundation', description: 'Architecture & tech stack' },
  { id: 'complete', name: 'Finalizing decision pack', description: 'Quality assessment & cross-validation' },
];

// Dynamic status messages that rotate to show activity
const ACTIVITY_MESSAGES = [
  { phase: -1, messages: ['Initializing discovery session', 'Warming up AI agents', 'Preparing analysis framework', 'Loading market data'] },
  { phase: 0, messages: ['Analyzing customer segments', 'Researching market trends', 'Gathering evidence', 'Validating assumptions', 'Identifying pain points', 'Exploring user behaviors'] },
  { phase: 1, messages: ['Mapping competitive landscape', 'Analyzing market position', 'Evaluating business models', 'Assessing strategic opportunities', 'Identifying market gaps'] },
  { phase: 2, messages: ['Building Lean Canvas', 'Projecting financials', 'Defining value proposition', 'Modeling revenue streams', 'Calculating market size'] },
  { phase: 3, messages: ['Structuring product requirements', 'Creating user stories', 'Defining acceptance criteria', 'Organizing epics', 'Prioritizing features'] },
  { phase: 4, messages: ['Designing architecture', 'Selecting technology stack', 'Planning infrastructure', 'Defining system components', 'Evaluating scalability'] },
  { phase: 5, messages: ['Running quality checks', 'Cross-validating outputs', 'Assessing completeness', 'Generating final pack', 'Preparing deliverables'] },
];

function getPhaseIndex(agentName: string | null): number {
  if (!agentName) return -1;
  const name = agentName.toLowerCase();
  if (name.includes('customer')) return 0;
  if (name.includes('business')) return 1;
  if (name.includes('product') || name.includes('requirement')) return 2;
  if (name.includes('technical') || name.includes('architect')) return 3;
  if (name.includes('critique') || name.includes('quality')) return 4;
  if (name.includes('complete') || name.includes('summary')) return 5;
  return -1;
}

export function ProgressTracker({ session, onCancel }: ProgressTrackerProps) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [messageIndex, setMessageIndex] = useState(0);
  const [fakeProgress, setFakeProgress] = useState(0);

  const currentPhaseIndex = getPhaseIndex(session.current_agent);
  const isComplete = session.status === 'completed';
  const isFailed = session.status === 'failed';

  // Derive activity message from phase and index
  const phaseMessages = ACTIVITY_MESSAGES.find(pm => pm.phase === currentPhaseIndex);
  const phaseMessageList = phaseMessages?.messages || ACTIVITY_MESSAGES[0].messages;
  const currentActivityMessage = phaseMessageList[messageIndex % phaseMessageList.length];

  // Derive perceived progress: use actual when >= 5%, otherwise use fake timer-based progress
  const actualProgress = session.progress_percentage;
  const perceivedProgress = actualProgress >= 5 ? actualProgress : fakeProgress;

  // Timer for elapsed time
  useEffect(() => {
    if (session.status !== 'in_progress' && session.status !== 'pending') {
      return;
    }

    const startTime = new Date(session.created_at).getTime();
    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [session.created_at, session.status]);

  // Rotate activity messages every 3 seconds
  useEffect(() => {
    if (isComplete || isFailed) return;

    const interval = setInterval(() => {
      setMessageIndex(prev => prev + 1);
    }, 3000);

    return () => clearInterval(interval);
  }, [currentPhaseIndex, isComplete, isFailed]);

  // Fake progress - shows gradual movement when actual progress is low
  useEffect(() => {
    if (isComplete || isFailed || actualProgress >= 5) return;

    const interval = setInterval(() => {
      setFakeProgress(prev => {
        if (prev >= 8) return 8;
        return prev + 0.5;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [actualProgress, isComplete, isFailed]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate estimated remaining time
  const estimatedTotal = 600; // 10 minutes
  const remainingSeconds = Math.max(0, estimatedTotal - elapsedTime);
  const remainingMinutes = Math.ceil(remainingSeconds / 60);

  // Use the higher of actual or perceived progress for display
  const displayProgress = Math.max(session.progress_percentage, perceivedProgress);

  return (
    <div className="progress-container">
      {/* Header */}
      <div className="progress-header">
        <h1 className="progress-title">
          {isFailed ? 'Discovery Failed' : isComplete ? 'Decision Pack Ready!' : 'Compressing your discovery'}
        </h1>
        <p className="progress-subtitle">
          {isFailed
            ? 'An error occurred during the discovery process'
            : isComplete
            ? 'Your inception pack is ready for review'
            : 'Building your decision-ready inception pack'}
        </p>
      </div>

      {/* Activity Status - NEW */}
      {!isComplete && !isFailed && (
        <div className="activity-status">
          <div className="activity-pulse"></div>
          <span className="activity-message">{currentActivityMessage}</span>
          <span className="activity-dots">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </span>
        </div>
      )}

      {/* Progress Bar */}
      <div className="progress-bar-section">
        <div className="progress-bar-wrapper">
          <div
            className="progress-bar"
            style={{ width: `${displayProgress}%` }}
          >
            {/* Animated shimmer even when progress is low */}
            {!isComplete && !isFailed && (
              <div className="progress-shimmer"></div>
            )}
          </div>
          {/* Show a minimum width indicator even at 0% */}
          {displayProgress === 0 && !isComplete && !isFailed && (
            <div className="progress-minimum-indicator"></div>
          )}
        </div>
        <div className="progress-meta">
          <span className="progress-percentage">{Math.round(displayProgress)}%</span>
          {!isComplete && !isFailed && (
            <span className="progress-time">~{remainingMinutes} {remainingMinutes === 1 ? 'minute' : 'minutes'} remaining</span>
          )}
        </div>
      </div>

      {/* Phases List */}
      <ul className="phases-list">
        {PHASES.map((phase, index) => {
          const isActive = currentPhaseIndex === index && !isComplete && !isFailed;
          const isCompleted = currentPhaseIndex > index || isComplete;
          const isPending = currentPhaseIndex < index && !isComplete && !isFailed;

          return (
            <li
              key={phase.id}
              className={`phase-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isPending ? 'pending' : ''}`}
            >
              <div className="phase-icon">
                {isCompleted ? (
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="9" fill="currentColor" opacity="0.2"/>
                    <path d="M6 10l3 3 5-6" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : isActive ? (
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="2" fill="none"/>
                    <circle cx="10" cy="10" r="4" fill="currentColor" className="pulse-dot"/>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="2" fill="none" opacity="0.3"/>
                  </svg>
                )}
              </div>
              <div className="phase-content">
                <div className="phase-name">{phase.name}</div>
                <div className="phase-description">{phase.description}</div>
              </div>
              {isActive && (
                <span className="active-badge">
                  <span className="active-pulse"></span>
                  Active
                </span>
              )}
            </li>
          );
        })}
      </ul>

      {/* Error Message */}
      {isFailed && session.error_message && (
        <div className="error-message">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="8" cy="8" r="6"/>
            <path d="M8 4v4M8 10h.01"/>
          </svg>
          <p>{session.error_message}</p>
        </div>
      )}

      {/* Footer */}
      <div className="progress-footer">
        <div className="session-info">
          <span className="session-id">
            Session: <strong>#{session.session_id.slice(0, 7)}</strong>
          </span>
          <span className="progress-time">Started {formatTime(elapsedTime)} ago</span>
        </div>
        {!isComplete && !isFailed && onCancel && (
          <button className="cancel-btn" onClick={onCancel}>
            Cancel Discovery
          </button>
        )}
      </div>
    </div>
  );
}
