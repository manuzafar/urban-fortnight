import { ExportDropdown } from './ExportDropdown';

interface StickyHeaderProps {
  productName: string;
  activeIndex: number;
  totalSlides: number;
  onExportJson: () => void;
  sessionId: string;
  currentSection: string;
  onNewDiscovery: () => void;
  onNavigate: (index: number) => void;
}

export function StickyHeader({
  productName,
  activeIndex,
  totalSlides,
  onExportJson,
  sessionId,
  currentSection,
  onNewDiscovery,
  onNavigate,
}: StickyHeaderProps) {
  return (
    <header className="slide-header">
      <div className="slide-header-left">
        <span className="slide-header-logo">🌱</span>
        <h1 className="slide-header-title">{productName}</h1>
      </div>

      <div className="slide-header-center">
        <div className="progress-dots">
          {Array.from({ length: totalSlides }).map((_, i) => (
            <button
              key={i}
              className={`progress-dot ${i === activeIndex ? 'active' : ''} ${i < activeIndex ? 'completed' : ''}`}
              onClick={() => onNavigate(i)}
              aria-label={`Go to slide ${i + 1}`}
            />
          ))}
        </div>
        <span className="progress-text">{activeIndex + 1} / {totalSlides}</span>
      </div>

      <div className="slide-header-right">
        <a
          href="https://calendly.com/seedcraft/feedback"
          target="_blank"
          rel="noopener noreferrer"
          className="slide-header-feedback feedback-btn"
        >
          Feedback
        </a>
        <ExportDropdown
          sessionId={sessionId}
          currentSection={currentSection}
          onExportJson={onExportJson}
        />
        <button className="action-btn primary" onClick={onNewDiscovery}>
          New Discovery
        </button>
      </div>
    </header>
  );
}
