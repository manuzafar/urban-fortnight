import { Bot, Lightbulb, Check, X, ChevronRight } from 'lucide-react';

interface CoachingMessage {
  type: 'suggestion' | 'warning' | 'tip' | 'question';
  content: string;
}

interface CoachingPanelProps {
  messages: CoachingMessage[];
  suggestion?: string;
  onApplySuggestion?: (suggestion: string) => void;
  onDismiss?: () => void;
  isLoading?: boolean;
}

export function CoachingPanel({
  messages,
  suggestion,
  onApplySuggestion,
  onDismiss,
  isLoading,
}: CoachingPanelProps) {
  if (!messages.length && !suggestion && !isLoading) {
    return null;
  }

  return (
    <div className="coaching-panel">
      <div className="coaching-header">
        <div className="coaching-title">
          <Bot size={16} />
          <span>AI Coach</span>
        </div>
        {onDismiss && (
          <button className="dismiss-btn" onClick={onDismiss} aria-label="Dismiss">
            <X size={14} />
          </button>
        )}
      </div>

      <div className="coaching-content">
        {isLoading ? (
          <div className="coaching-loading">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <p>Analyzing your work...</p>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <div key={idx} className={`coaching-message ${msg.type}`}>
                <div className="message-icon">
                  {msg.type === 'suggestion' && <Lightbulb size={14} />}
                  {msg.type === 'warning' && <span>!</span>}
                  {msg.type === 'tip' && <ChevronRight size={14} />}
                  {msg.type === 'question' && <span>?</span>}
                </div>
                <p>{msg.content}</p>
              </div>
            ))}

            {suggestion && (
              <div className="coaching-suggestion">
                <p className="suggestion-label">Suggested improvement:</p>
                <p className="suggestion-text">{suggestion}</p>
                <div className="suggestion-actions">
                  <button
                    className="apply-btn"
                    onClick={() => onApplySuggestion?.(suggestion)}
                  >
                    <Check size={14} />
                    Apply Suggestion
                  </button>
                  <button className="keep-btn" onClick={onDismiss}>
                    Keep Mine
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <style>{`
        .coaching-panel {
          background: var(--v4-warning-light, rgba(202, 138, 4, 0.08));
          border: 1px solid var(--v4-warning, #ca8a04);
          border-radius: var(--v4-radius-lg, 12px);
          overflow: hidden;
        }

        .coaching-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
          background: rgba(202, 138, 4, 0.15);
          border-bottom: 1px solid rgba(202, 138, 4, 0.3);
        }

        .coaching-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          font-weight: 600;
          color: var(--v4-warning, #ca8a04);
        }

        .dismiss-btn {
          padding: 4px;
          background: none;
          border: none;
          border-radius: var(--v4-radius-sm, 4px);
          cursor: pointer;
          color: var(--v4-warning, #ca8a04);
          opacity: 0.7;
          transition: all 0.2s;
        }

        .dismiss-btn:hover {
          opacity: 1;
          background: rgba(0, 0, 0, 0.1);
        }

        .coaching-content {
          padding: 16px;
        }

        .coaching-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          padding: 20px 0;
        }

        .loading-dots {
          display: flex;
          gap: 6px;
        }

        .loading-dots span {
          width: 8px;
          height: 8px;
          background: var(--v4-warning, #ca8a04);
          border-radius: 50%;
          animation: bounce 1.4s ease-in-out infinite;
        }

        .loading-dots span:nth-child(1) {
          animation-delay: 0s;
        }

        .loading-dots span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .loading-dots span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes bounce {
          0%, 80%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-8px);
          }
        }

        .coaching-loading p {
          margin: 0;
          font-size: 13px;
          color: var(--v4-warning, #ca8a04);
        }

        .coaching-message {
          display: flex;
          gap: 12px;
          padding: 10px 0;
          border-bottom: 1px solid rgba(202, 138, 4, 0.2);
        }

        .coaching-message:last-child {
          border-bottom: none;
        }

        .message-icon {
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(202, 138, 4, 0.15);
          border-radius: var(--v4-radius, 6px);
          color: var(--v4-warning, #ca8a04);
          font-size: 12px;
          font-weight: 700;
          flex-shrink: 0;
        }

        .coaching-message p {
          margin: 0;
          font-size: 13px;
          line-height: 1.5;
          color: var(--v4-text, #171717);
        }

        .coaching-message.warning .message-icon {
          background: var(--v4-error-light, rgba(220, 38, 38, 0.08));
          color: var(--v4-error, #dc2626);
        }

        .coaching-suggestion {
          margin-top: 12px;
          padding: 16px;
          background: var(--v4-surface, white);
          border-radius: var(--v4-radius-md, 8px);
        }

        .suggestion-label {
          margin: 0 0 8px 0;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--v4-warning, #ca8a04);
        }

        .suggestion-text {
          margin: 0 0 16px 0;
          padding: 12px;
          background: var(--v4-bg-subtle, #f5f5f5);
          border-radius: var(--v4-radius, 6px);
          font-size: 14px;
          line-height: 1.5;
          color: var(--v4-text, #171717);
        }

        .suggestion-actions {
          display: flex;
          gap: 8px;
        }

        .apply-btn,
        .keep-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          border-radius: var(--v4-radius, 6px);
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .apply-btn {
          background: var(--v4-accent, #c2410c);
          border: none;
          color: white;
        }

        .apply-btn:hover {
          background: var(--v4-accent-hover, #9a3412);
        }

        .keep-btn {
          background: transparent;
          border: 1px solid var(--v4-border, #e5e5e5);
          color: var(--v4-text-secondary, #525252);
        }

        .keep-btn:hover {
          background: var(--v4-bg-subtle, #f5f5f5);
        }
      `}</style>
    </div>
  );
}

export default CoachingPanel;
