import { X } from 'lucide-react';

interface WelcomeModalProps {
  onStartTour: () => void;
  onSkip: () => void;
}

export function WelcomeModal({ onStartTour, onSkip }: WelcomeModalProps) {
  return (
    <div className="modal-overlay" onClick={onSkip}>
      <div className="welcome-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onSkip} aria-label="Close">
          <X size={20} />
        </button>

        <div className="welcome-icon">🎉</div>

        <h2>Your Inception Pack is Ready!</h2>

        <p>
          This pack contains <strong>7 sections</strong> designed for different
          stakeholders — from executive summary to technical architecture to
          legal review.
        </p>

        <p>
          Each section is structured so the right people can review the right parts.
        </p>

        <div className="welcome-actions">
          <button className="btn-primary" onClick={onStartTour}>
            Take a Quick Tour (30 sec)
          </button>
          <button className="btn-secondary" onClick={onSkip}>
            Skip, I'll explore
          </button>
        </div>
      </div>
    </div>
  );
}
