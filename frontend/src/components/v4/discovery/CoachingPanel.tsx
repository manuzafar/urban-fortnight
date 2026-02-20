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
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          border: 1px solid #fbbf24;
          border-radius: 12px;
          overflow: hidden;
        }

        .coaching-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
          background: rgba(251, 191, 36, 0.3);
          border-bottom: 1px solid rgba(251, 191, 36, 0.5);
        }

        .coaching-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          font-weight: 600;
          color: #92400e;
        }

        .dismiss-btn {
          padding: 4px;
          background: none;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          color: #92400e;
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
          background: #92400e;
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
          color: #92400e;
        }

        .coaching-message {
          display: flex;
          gap: 12px;
          padding: 10px 0;
          border-bottom: 1px solid rgba(251, 191, 36, 0.3);
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
          background: rgba(146, 64, 14, 0.1);
          border-radius: 6px;
          color: #92400e;
          font-size: 12px;
          font-weight: 700;
          flex-shrink: 0;
        }

        .coaching-message p {
          margin: 0;
          font-size: 13px;
          line-height: 1.5;
          color: #78350f;
        }

        .coaching-message.warning .message-icon {
          background: #fecaca;
          color: #dc2626;
        }

        .coaching-suggestion {
          margin-top: 12px;
          padding: 16px;
          background: rgba(255, 255, 255, 0.6);
          border-radius: 8px;
        }

        .suggestion-label {
          margin: 0 0 8px 0;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #92400e;
        }

        .suggestion-text {
          margin: 0 0 16px 0;
          padding: 12px;
          background: white;
          border-radius: 6px;
          font-size: 14px;
          line-height: 1.5;
          color: #1a1a2e;
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
          border-radius: 6px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .apply-btn {
          background: #92400e;
          border: none;
          color: white;
        }

        .apply-btn:hover {
          background: #78350f;
        }

        .keep-btn {
          background: transparent;
          border: 1px solid rgba(146, 64, 14, 0.3);
          color: #92400e;
        }

        .keep-btn:hover {
          background: rgba(146, 64, 14, 0.1);
        }
      `}</style>
    </div>
  );
}

export default CoachingPanel;
