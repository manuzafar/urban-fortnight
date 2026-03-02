import { FlaskConical, PlayCircle, CheckCircle, XCircle, Clock } from 'lucide-react';
import './rendererStyles.css';

interface ValidationExperiment {
  rung: number;
  name: string;
  hypothesis: string;
  success_criteria: string;
  failure_criteria: string;
  target_participants: string;
  method: string;
  timeline: string;
  status: 'todo' | 'in_progress' | 'completed' | 'passed' | 'failed';
}

interface ValidationPlanOutput {
  current_rung: number;
  experiments: ValidationExperiment[];
  next_experiment?: ValidationExperiment;
  validation_summary?: string;
}

interface ValidationPlanRendererProps {
  output: ValidationPlanOutput;
}

const RUNG_NAMES: Record<number, string> = {
  1: 'Talk to Customers',
  2: 'Show Interest',
  3: 'Manual Value',
  4: 'Automated Value',
  5: 'Sustainable Business',
};

export function ValidationPlanRenderer({ output }: ValidationPlanRendererProps) {
  // Group experiments by rung
  const experimentsByRung: Record<number, ValidationExperiment[]> = {};
  output.experiments?.forEach((exp) => {
    if (!experimentsByRung[exp.rung]) {
      experimentsByRung[exp.rung] = [];
    }
    experimentsByRung[exp.rung].push(exp);
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'passed':
        return <CheckCircle size={16} className="status-icon-success" />;
      case 'failed':
        return <XCircle size={16} className="status-icon-error" />;
      case 'in_progress':
        return <PlayCircle size={16} className="status-icon-info" />;
      default:
        return <Clock size={16} className="status-icon-muted" />;
    }
  };

  return (
    <div className="stage-renderer validation-plan">
      {/* Current Rung */}
      <section className="renderer-section">
        <div className="stage-summary">
          <div className="overall-score">
            Current Validation Rung: <strong>{output.current_rung}/5</strong>
          </div>
          <div className="recommendation proceed">
            <FlaskConical size={16} />
            {RUNG_NAMES[output.current_rung] || `Rung ${output.current_rung}`}
          </div>
        </div>
      </section>

      {/* Next Experiment */}
      {output.next_experiment && (
        <section className="renderer-section">
          <h4>
            <PlayCircle size={16} />
            Next Experiment
          </h4>
          <div className="experiment-card next">
            <div className="experiment-header">
              <span className="experiment-name">{output.next_experiment.name}</span>
              <span className={`experiment-status status-${output.next_experiment.status}`}>
                {output.next_experiment.status.replace('_', ' ')}
              </span>
            </div>
            <div className="experiment-details">
              <div className="experiment-detail">
                <label>Hypothesis</label>
                <span>{output.next_experiment.hypothesis}</span>
              </div>
              <div className="experiment-detail">
                <label>Success Criteria</label>
                <span>{output.next_experiment.success_criteria}</span>
              </div>
              <div className="experiment-detail">
                <label>Method</label>
                <span>{output.next_experiment.method}</span>
              </div>
              <div className="experiment-detail">
                <label>Timeline</label>
                <span>{output.next_experiment.timeline}</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Validation Ladder */}
      <section className="renderer-section">
        <h4>
          <FlaskConical size={16} />
          Validation Ladder
        </h4>

        <div className="validation-ladder">
          {[1, 2, 3, 4, 5].map((rung) => {
            const rungExperiments = experimentsByRung[rung] || [];
            const isCurrentRung = rung === output.current_rung;
            const isPastRung = rung < output.current_rung;

            return (
              <div key={rung} className={`rung-section ${isCurrentRung ? 'current' : ''} ${isPastRung ? 'past' : ''}`}>
                <div className="rung-header">
                  <span className="rung-number">
                    {rung}
                  </span>
                  <span className="rung-title">{RUNG_NAMES[rung]}</span>
                </div>

                {rungExperiments.length > 0 ? (
                  rungExperiments.map((exp, i) => (
                    <div
                      key={i}
                      className={`experiment-card ${exp === output.next_experiment ? 'next' : ''}`}
                    >
                      <div className="experiment-header">
                        <span className="experiment-name">
                          {getStatusIcon(exp.status)}
                          <span className="experiment-name-text">{exp.name}</span>
                        </span>
                        <span className={`experiment-status status-${exp.status}`}>
                          {exp.status.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="experiment-details">
                        <div className="experiment-detail">
                          <label>Hypothesis</label>
                          <span>{exp.hypothesis}</span>
                        </div>
                        <div className="experiment-detail">
                          <label>Success</label>
                          <span>{exp.success_criteria}</span>
                        </div>
                        <div className="experiment-detail">
                          <label>Participants</label>
                          <span>{exp.target_participants}</span>
                        </div>
                        <div className="experiment-detail">
                          <label>Timeline</label>
                          <span>{exp.timeline}</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="empty-state rung-empty-state">
                    No experiments planned for this rung yet
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Validation Summary */}
      {output.validation_summary && (
        <section className="renderer-section coaching-section">
          <h4>Validation Strategy Summary</h4>
          <p className="analysis-text validation-summary-text">
            {output.validation_summary}
          </p>
        </section>
      )}
    </div>
  );
}

export default ValidationPlanRenderer;
