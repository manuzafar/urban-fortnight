import { MessageSquare, Calendar } from 'lucide-react';

interface FeedbackBannerProps {
  calendlyUrl?: string;
  typeformUrl?: string;
}

// Default URLs - replace with actual links
const DEFAULT_CALENDLY_URL = 'https://calendly.com/seedcraft/feedback';
const DEFAULT_TYPEFORM_URL = 'https://seedcraft.typeform.com/feedback';

export function FeedbackBanner({
  calendlyUrl = DEFAULT_CALENDLY_URL,
  typeformUrl = DEFAULT_TYPEFORM_URL,
}: FeedbackBannerProps) {
  return (
    <div className="feedback-banner">
      <span className="feedback-banner-text">
        This is a beta. Your feedback shapes the product.
      </span>
      <div className="feedback-banner-actions">
        <a
          href={calendlyUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="feedback-link"
        >
          <Calendar size={14} />
          Schedule 15 min
        </a>
        <a
          href={typeformUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="feedback-link"
        >
          <MessageSquare size={14} />
          Quick feedback
        </a>
      </div>
    </div>
  );
}
