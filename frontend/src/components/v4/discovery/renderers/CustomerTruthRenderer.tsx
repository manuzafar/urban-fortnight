import { Users, MessageSquare, TrendingUp, AlertCircle } from 'lucide-react';
import './rendererStyles.css';

interface Interview {
  id?: string;
  interviewee_name: string;
  interviewee_role: string;
  company_type: string;
  company_size: string;
  interview_date: string;
  story_raw: string;
  key_quote: string;
  struggling_moment: string;
  emotions: string[];
  current_workaround: string;
  desired_outcome: string;
}

interface PainPattern {
  description: string;
  frequency: number;
  evidence: Array<{ interview_id?: string; quote: string }>;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

interface PatternSynthesis {
  pain_patterns: PainPattern[];
  trigger_patterns: Array<{ description: string; frequency: number }>;
  outcome_patterns: Array<{ description: string; frequency: number }>;
  contradictions: Array<{ description: string }>;
  interview_gaps: string[];
  total_interviews: number;
  evidence_quality: string;
}

interface CustomerTruthOutput {
  interviews: Interview[];
  patterns?: PatternSynthesis;
  interview_goal: number;
  interviews_completed: number;
  readiness_score: number;
}

interface CustomerTruthRendererProps {
  output: CustomerTruthOutput;
}

export function CustomerTruthRenderer({ output }: CustomerTruthRendererProps) {
  const hasInterviews = output.interviews && output.interviews.length > 0;
  const hasPatterns = output.patterns && output.patterns.pain_patterns?.length > 0;

  return (
    <div className="stage-renderer customer-truth">
      {/* Readiness Score */}
      <section className="renderer-section">
        <div className="stage-summary">
          <div className="overall-score">
            Readiness Score: <strong>{output.readiness_score}/10</strong>
          </div>
          <div className="interview-progress-summary">
            <Users size={16} />
            {output.interviews_completed || output.interviews?.length || 0} / {output.interview_goal} interviews
          </div>
        </div>
      </section>

      {/* Interviews */}
      <section className="renderer-section">
        <h4>
          <MessageSquare size={16} />
          Interviews ({output.interviews?.length || 0})
        </h4>
        {hasInterviews ? (
          <div className="interviews-list">
            {output.interviews.map((interview, i) => (
              <div key={interview.id || i} className="interview-card">
                <div className="interview-header">
                  <div className="interview-meta">
                    <span className="interview-name">{interview.interviewee_name}</span>
                    <span className="interview-role">
                      {interview.interviewee_role} at {interview.company_type} ({interview.company_size})
                    </span>
                  </div>
                  <span className="interview-date">
                    {interview.interview_date}
                  </span>
                </div>
                {interview.key_quote && (
                  <div className="interview-quote">
                    "{interview.key_quote}"
                  </div>
                )}
                {interview.struggling_moment && (
                  <p className="struggling-moment-detail">
                    <strong>Struggling moment:</strong> {interview.struggling_moment}
                  </p>
                )}
                {interview.emotions && interview.emotions.length > 0 && (
                  <div className="emotions-tags">
                    {interview.emotions.map((emotion, j) => (
                      <span key={j} className="emotion-tag">{emotion}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">
            No interviews conducted yet. Add real customer interviews for stronger evidence.
          </p>
        )}
      </section>

      {/* Patterns */}
      {hasPatterns && (
        <section className="renderer-section">
          <h4>
            <TrendingUp size={16} />
            Pain Patterns
          </h4>
          <div className="patterns-grid">
            {output.patterns!.pain_patterns.map((pattern, i) => (
              <div key={i} className="pattern-card">
                <h5>
                  {pattern.description}
                  <span className={`severity-badge severity-${pattern.severity}`}>
                    {pattern.severity}
                  </span>
                </h5>
                <span className="pattern-frequency">
                  Mentioned by {pattern.frequency} interviewees
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Trigger Patterns */}
      {output.patterns?.trigger_patterns && output.patterns.trigger_patterns.length > 0 && (
        <section className="renderer-section">
          <h4>Trigger Patterns</h4>
          <ul className="alternatives-list">
            {output.patterns.trigger_patterns.map((trigger, i) => (
              <li key={i}>
                {trigger.description} ({trigger.frequency}x mentioned)
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Outcome Patterns */}
      {output.patterns?.outcome_patterns && output.patterns.outcome_patterns.length > 0 && (
        <section className="renderer-section">
          <h4>Desired Outcomes</h4>
          <ul className="alternatives-list">
            {output.patterns.outcome_patterns.map((outcome, i) => (
              <li key={i}>
                {outcome.description} ({outcome.frequency}x mentioned)
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Contradictions */}
      {output.patterns?.contradictions && output.patterns.contradictions.length > 0 && (
        <section className="renderer-section">
          <h4>
            <AlertCircle size={16} />
            Contradictions Found
          </h4>
          <ul className="alternatives-list">
            {output.patterns.contradictions.map((c, i) => (
              <li key={i}>{c.description}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Interview Gaps */}
      {output.patterns?.interview_gaps && output.patterns.interview_gaps.length > 0 && (
        <section className="renderer-section coaching-section">
          <h4>Suggested Topics for Next Interview</h4>
          <ul className="coaching-list">
            {output.patterns.interview_gaps.map((gap, i) => (
              <li key={i}>{gap}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export default CustomerTruthRenderer;
