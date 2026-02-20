import { useState } from 'react';
import { X, User, Building, Calendar, MessageSquare, Quote, Heart, Target } from 'lucide-react';

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

interface InterviewFormProps {
  onSave: (interview: Interview) => void;
  onCancel: () => void;
  initialData?: Partial<Interview>;
}

const EMOTIONS = [
  'Frustrated',
  'Anxious',
  'Overwhelmed',
  'Embarrassed',
  'Confused',
  'Angry',
  'Hopeless',
  'Stressed',
];

const COMPANY_TYPES = [
  { value: 'startup_seed', label: 'Startup (Seed)' },
  { value: 'startup_ab', label: 'Startup (Series A-B)' },
  { value: 'growth', label: 'Growth (Series C+)' },
  { value: 'enterprise', label: 'Enterprise' },
  { value: 'smb', label: 'Small Business' },
  { value: 'agency', label: 'Agency' },
  { value: 'other', label: 'Other' },
];

const COMPANY_SIZES = [
  { value: '1-10', label: '1-10 employees' },
  { value: '11-50', label: '11-50 employees' },
  { value: '51-200', label: '51-200 employees' },
  { value: '201-1000', label: '201-1000 employees' },
  { value: '1000+', label: '1000+ employees' },
];

export function InterviewForm({ onSave, onCancel, initialData }: InterviewFormProps) {
  const [interview, setInterview] = useState<Partial<Interview>>({
    interview_date: new Date().toISOString().split('T')[0],
    emotions: [],
    ...initialData,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateField = <K extends keyof Interview>(
    field: K,
    value: Interview[K]
  ) => {
    setInterview((prev) => ({ ...prev, [field]: value }));
    // Clear error when field is updated
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const toggleEmotion = (emotion: string) => {
    const emotions = interview.emotions || [];
    const newEmotions = emotions.includes(emotion)
      ? emotions.filter((e) => e !== emotion)
      : [...emotions, emotion];
    updateField('emotions', newEmotions);
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!interview.interviewee_name?.trim()) {
      newErrors.interviewee_name = 'Name is required';
    }
    if (!interview.interviewee_role?.trim()) {
      newErrors.interviewee_role = 'Role is required';
    }
    if (!interview.story_raw?.trim()) {
      newErrors.story_raw = 'Interview story is required';
    }
    if (!interview.struggling_moment?.trim()) {
      newErrors.struggling_moment = 'Struggling moment is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSave(interview as Interview);
    }
  };

  return (
    <div className="interview-form-overlay">
      <div className="interview-form-container">
        <form onSubmit={handleSubmit} className="interview-form">
          <div className="form-header">
            <h2>Add Interview</h2>
            <p>Record insights from a customer interview</p>
            <button
              type="button"
              className="close-btn"
              onClick={onCancel}
              aria-label="Close"
            >
              <X size={20} />
            </button>
          </div>

          <div className="form-body">
            {/* Section 1: Who */}
            <section className="form-section">
              <h3>
                <User size={18} />
                Who did you interview?
              </h3>

              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="interviewee_name">Name*</label>
                  <input
                    id="interviewee_name"
                    type="text"
                    placeholder="Sarah Johnson"
                    value={interview.interviewee_name || ''}
                    onChange={(e) =>
                      updateField('interviewee_name', e.target.value)
                    }
                    className={errors.interviewee_name ? 'error' : ''}
                  />
                  {errors.interviewee_name && (
                    <span className="error-msg">{errors.interviewee_name}</span>
                  )}
                </div>

                <div className="form-field">
                  <label htmlFor="interviewee_role">Role*</label>
                  <input
                    id="interviewee_role"
                    type="text"
                    placeholder="Product Manager"
                    value={interview.interviewee_role || ''}
                    onChange={(e) =>
                      updateField('interviewee_role', e.target.value)
                    }
                    className={errors.interviewee_role ? 'error' : ''}
                  />
                  {errors.interviewee_role && (
                    <span className="error-msg">{errors.interviewee_role}</span>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="company_type">
                    <Building size={14} />
                    Company Type
                  </label>
                  <select
                    id="company_type"
                    value={interview.company_type || ''}
                    onChange={(e) => updateField('company_type', e.target.value)}
                  >
                    <option value="">Select...</option>
                    {COMPANY_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="company_size">Company Size</label>
                  <select
                    id="company_size"
                    value={interview.company_size || ''}
                    onChange={(e) => updateField('company_size', e.target.value)}
                  >
                    <option value="">Select...</option>
                    {COMPANY_SIZES.map((size) => (
                      <option key={size.value} value={size.value}>
                        {size.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="interview_date">
                    <Calendar size={14} />
                    Interview Date
                  </label>
                  <input
                    id="interview_date"
                    type="date"
                    value={interview.interview_date || ''}
                    onChange={(e) =>
                      updateField('interview_date', e.target.value)
                    }
                  />
                </div>
              </div>
            </section>

            {/* Section 2: The Story */}
            <section className="form-section">
              <h3>
                <MessageSquare size={18} />
                The Story
              </h3>
              <p className="section-hint">
                Teresa Torres: "Tell me about the last time..."
              </p>

              <div className="form-field">
                <label htmlFor="story_raw">Interview Notes*</label>
                <textarea
                  id="story_raw"
                  placeholder="Paste or type what they told you... Include as much detail as possible about their experience."
                  rows={6}
                  value={interview.story_raw || ''}
                  onChange={(e) => updateField('story_raw', e.target.value)}
                  className={errors.story_raw ? 'error' : ''}
                />
                {errors.story_raw && (
                  <span className="error-msg">{errors.story_raw}</span>
                )}
              </div>

              <div className="form-field">
                <label htmlFor="key_quote">
                  <Quote size={14} />
                  Key Quote
                </label>
                <input
                  id="key_quote"
                  type="text"
                  placeholder="Their exact words that capture the pain..."
                  value={interview.key_quote || ''}
                  onChange={(e) => updateField('key_quote', e.target.value)}
                />
              </div>
            </section>

            {/* Section 3: Analysis */}
            <section className="form-section">
              <h3>
                <Target size={18} />
                Your Analysis
              </h3>

              <div className="form-field">
                <label htmlFor="struggling_moment">Struggling Moment*</label>
                <input
                  id="struggling_moment"
                  type="text"
                  placeholder="What was the specific moment when they struggled?"
                  value={interview.struggling_moment || ''}
                  onChange={(e) =>
                    updateField('struggling_moment', e.target.value)
                  }
                  className={errors.struggling_moment ? 'error' : ''}
                />
                {errors.struggling_moment && (
                  <span className="error-msg">{errors.struggling_moment}</span>
                )}
              </div>

              <div className="form-field">
                <label>
                  <Heart size={14} />
                  Emotions Expressed
                </label>
                <div className="emotion-chips">
                  {EMOTIONS.map((emotion) => (
                    <button
                      key={emotion}
                      type="button"
                      className={`emotion-chip ${
                        interview.emotions?.includes(emotion) ? 'selected' : ''
                      }`}
                      onClick={() => toggleEmotion(emotion)}
                    >
                      {emotion}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="current_workaround">Current Workaround</label>
                <input
                  id="current_workaround"
                  type="text"
                  placeholder="What do they do today to solve this?"
                  value={interview.current_workaround || ''}
                  onChange={(e) =>
                    updateField('current_workaround', e.target.value)
                  }
                />
              </div>

              <div className="form-field">
                <label htmlFor="desired_outcome">Desired Outcome</label>
                <input
                  id="desired_outcome"
                  type="text"
                  placeholder="What would success look like for them?"
                  value={interview.desired_outcome || ''}
                  onChange={(e) =>
                    updateField('desired_outcome', e.target.value)
                  }
                />
              </div>
            </section>
          </div>

          <div className="form-footer">
            <button type="button" className="btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Save Interview
            </button>
          </div>
        </form>
      </div>

      <style>{`
        .interview-form-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }

        .interview-form-container {
          width: 100%;
          max-width: 680px;
          max-height: 90vh;
          overflow: hidden;
          background: white;
          border-radius: 16px;
          box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
        }

        .interview-form {
          display: flex;
          flex-direction: column;
          height: 100%;
          max-height: 90vh;
        }

        .form-header {
          position: relative;
          padding: 24px 24px 20px;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
        }

        .form-header h2 {
          margin: 0 0 4px 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        .form-header p {
          margin: 0;
          font-size: 14px;
          color: var(--text-secondary, #6b7280);
        }

        .close-btn {
          position: absolute;
          top: 20px;
          right: 20px;
          padding: 8px;
          background: none;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          color: var(--text-secondary, #6b7280);
          transition: all 0.2s;
        }

        .close-btn:hover {
          background: var(--bg-hover, #f3f4f6);
          color: var(--text-primary, #1a1a2e);
        }

        .form-body {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
        }

        .form-section {
          margin-bottom: 32px;
        }

        .form-section:last-child {
          margin-bottom: 0;
        }

        .form-section h3 {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 0 0 16px 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        .section-hint {
          margin: -8px 0 16px 0;
          padding: 12px 16px;
          background: var(--bg-info, #eff6ff);
          border-radius: 8px;
          font-size: 13px;
          color: var(--text-info, #1d4ed8);
          font-style: italic;
        }

        .form-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          gap: 16px;
          margin-bottom: 16px;
        }

        .form-field {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .form-field label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          font-weight: 500;
          color: var(--text-secondary, #6b7280);
        }

        .form-field input,
        .form-field select,
        .form-field textarea {
          padding: 10px 12px;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 8px;
          font-size: 14px;
          transition: all 0.2s;
        }

        .form-field input:focus,
        .form-field select:focus,
        .form-field textarea:focus {
          outline: none;
          border-color: var(--primary, #3b82f6);
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-field input.error,
        .form-field textarea.error {
          border-color: var(--error, #ef4444);
        }

        .error-msg {
          font-size: 12px;
          color: var(--error, #ef4444);
        }

        .form-field textarea {
          resize: vertical;
          min-height: 100px;
        }

        .emotion-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .emotion-chip {
          padding: 6px 12px;
          background: var(--bg-secondary, #f3f4f6);
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 20px;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .emotion-chip:hover {
          background: var(--bg-hover, #e5e7eb);
        }

        .emotion-chip.selected {
          background: var(--primary, #3b82f6);
          border-color: var(--primary, #3b82f6);
          color: white;
        }

        .form-footer {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
          padding: 20px 24px;
          border-top: 1px solid var(--border-color, #e5e7eb);
        }

        .btn-secondary,
        .btn-primary {
          padding: 10px 20px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-secondary {
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          color: var(--text-secondary, #6b7280);
        }

        .btn-secondary:hover {
          background: var(--bg-hover, #f3f4f6);
        }

        .btn-primary {
          background: var(--primary, #3b82f6);
          border: none;
          color: white;
        }

        .btn-primary:hover {
          background: var(--primary-dark, #2563eb);
        }

        @media (max-width: 480px) {
          .interview-form-overlay {
            padding: 0;
          }

          .interview-form-container {
            max-height: 100vh;
            border-radius: 0;
          }

          .form-row {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default InterviewForm;
