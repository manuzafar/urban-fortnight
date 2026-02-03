import { useEffect, useState } from 'react';
import {
  Users,
  TrendingUp,
  FileText,
  Cpu,
  CheckCircle2,
  Loader2,
  Circle,
  XCircle,
  RefreshCw,
} from 'lucide-react';
import type { SessionStatusResponse } from '../types/api';

interface ProgressTrackerProps {
  session: SessionStatusResponse;
  onCancel?: () => void;
}

const AGENTS = [
  { id: 'customer_research', name: 'Customer Research Agent', icon: Users },
  { id: 'business_strategy', name: 'Business Strategy Agent', icon: TrendingUp },
  { id: 'product_requirements', name: 'Product Requirements Agent', icon: FileText },
  { id: 'technical_architect', name: 'Technical Architect Agent', icon: Cpu },
  { id: 'critique', name: 'Critique Agent', icon: CheckCircle2 },
];

function getAgentIndex(agentName: string | null): number {
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

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const currentAgentIndex = getAgentIndex(session.current_agent);
  const isComplete = session.status === 'completed';
  const isFailed = session.status === 'failed';

  return (
    <div className={`progress-tracker ${session.status}`}>
      <div className="progress-header">
        <div className="progress-title">
          {isFailed ? (
            <XCircle className="status-icon error" size={24} />
          ) : isComplete ? (
            <CheckCircle2 className="status-icon success" size={24} />
          ) : (
            <Loader2 className="status-icon spinning" size={24} />
          )}
          <div>
            <h3>
              {isFailed
                ? 'Discovery Failed'
                : isComplete
                ? 'Discovery Complete!'
                : 'Discovery in Progress'}
            </h3>
            <span className="session-id">Session: {session.session_id}</span>
          </div>
        </div>

        <div className="progress-stats">
          <div className="stat">
            <span className="stat-value">{formatTime(elapsedTime)}</span>
            <span className="stat-label">Elapsed</span>
          </div>
          {session.iteration > 1 && (
            <div className="stat">
              <RefreshCw size={14} />
              <span className="stat-value">{session.iteration}</span>
              <span className="stat-label">Iteration</span>
            </div>
          )}
        </div>
      </div>

      <div className="progress-bar-container">
        <div
          className="progress-bar"
          style={{ width: `${session.progress_percentage}%` }}
        />
        <span className="progress-percentage">{session.progress_percentage}%</span>
      </div>

      <div className="agents-list">
        {AGENTS.map((agent, index) => {
          const Icon = agent.icon;
          const isActive = currentAgentIndex === index;
          const isCompleted = currentAgentIndex > index || isComplete;
          const isPending = currentAgentIndex < index && !isComplete;

          return (
            <div
              key={agent.id}
              className={`agent-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isPending ? 'pending' : ''}`}
            >
              <div className="agent-status">
                {isCompleted ? (
                  <CheckCircle2 size={20} className="check" />
                ) : isActive ? (
                  <Loader2 size={20} className="spinning" />
                ) : (
                  <Circle size={20} />
                )}
              </div>
              <Icon size={18} className="agent-icon" />
              <span className="agent-name">{agent.name}</span>
            </div>
          );
        })}
      </div>

      {isFailed && session.error_message && (
        <div className="error-message">
          <XCircle size={16} />
          <p>{session.error_message}</p>
        </div>
      )}

      {!isComplete && !isFailed && onCancel && (
        <button className="cancel-button" onClick={onCancel}>
          Cancel Discovery
        </button>
      )}
    </div>
  );
}
