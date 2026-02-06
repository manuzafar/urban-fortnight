import { useRef, useState, useEffect } from 'react';
import { StickyHeader } from './StickyHeader';
import { Slide } from './Slide';
import { SlideNav } from './SlideNav';
import { WelcomeModal } from './WelcomeModal';
import { OnboardingTour } from './OnboardingTour';
import type { InceptionPack } from '../types/api';
import '../styles/slide-viewer.css';

interface SlideViewerProps {
  pack: InceptionPack;
  onNewDiscovery: () => void;
}

export const SECTIONS = [
  { key: 'executive_summary', title: 'Executive Summary', icon: '📋', color: '#667eea' },
  { key: 'customer_research', title: 'Customer Research', icon: '🔍', color: '#f093fb' },
  { key: 'business_case', title: 'Business Case', icon: '💰', color: '#4facfe' },
  { key: 'product_requirements_document', title: 'Product Requirements', icon: '📝', color: '#43e97b' },
  { key: 'technical_architecture', title: 'Technical Architecture', icon: '🏗️', color: '#fa709a' },
  { key: 'legal_regulatory_review', title: 'Legal & Regulatory', icon: '⚖️', color: '#a8edea' },
  { key: 'quality_assessment', title: 'Quality Assessment', icon: '✅', color: '#ffecd2' },
] as const;

const TOUR_STORAGE_KEY = 'seedcraft_tour_completed';

function getInitialShowWelcome(): boolean {
  try {
    return !localStorage.getItem(TOUR_STORAGE_KEY);
  } catch {
    return false;
  }
}

export function SlideViewer({ pack, onNewDiscovery }: SlideViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [showWelcome, setShowWelcome] = useState(getInitialShowWelcome);
  const [runTour, setRunTour] = useState(false);

  // Track scroll position to update active section
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const slideHeight = container.clientHeight;
      const scrollTop = container.scrollTop;
      const index = Math.round(scrollTop / slideHeight);
      setActiveIndex(Math.min(index, SECTIONS.length - 1));
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (index: number) => {
    const container = containerRef.current;
    if (!container) return;
    const slideHeight = container.clientHeight;
    container.scrollTo({ top: index * slideHeight, behavior: 'smooth' });
  };

  const handleStartTour = () => {
    setShowWelcome(false);
    setTimeout(() => setRunTour(true), 100);
  };

  const handleSkipTour = () => {
    setShowWelcome(false);
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
  };

  const handleTourComplete = () => {
    setRunTour(false);
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
  };

  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(pack, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inception-pack-${pack.metadata.session_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {showWelcome && (
        <WelcomeModal onStartTour={handleStartTour} onSkip={handleSkipTour} />
      )}

      <OnboardingTour run={runTour} onComplete={handleTourComplete} />

      <div className="slide-viewer">
        <StickyHeader
          productName={pack.executive_summary?.product_name || 'Inception Pack'}
          activeIndex={activeIndex}
          totalSlides={SECTIONS.length}
          onExportJson={handleDownloadJson}
          sessionId={pack.metadata?.session_id || ''}
          currentSection={SECTIONS[activeIndex].key}
          onNewDiscovery={onNewDiscovery}
          onNavigate={scrollToSection}
        />

        <div className="slide-container" ref={containerRef}>
          {SECTIONS.map((section, index) => (
            <Slide
              key={section.key}
              index={index}
              total={SECTIONS.length}
              title={section.title}
              icon={section.icon}
              accentColor={section.color}
              data={pack[section.key as keyof InceptionPack]}
              sectionKey={section.key}
            />
          ))}
        </div>

        <SlideNav
          sections={SECTIONS}
          activeIndex={activeIndex}
          onNavigate={scrollToSection}
        />
      </div>
    </>
  );
}
