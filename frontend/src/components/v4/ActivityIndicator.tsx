/**
 * V4 Activity Indicator Component
 * Rotating activity messages for loading states
 */

import { useState, useEffect, useCallback } from 'react';
import { Loader2 } from 'lucide-react';
import '../../styles/theme-v4.css';

// Activity messages by phase
const ACTIVITY_MESSAGES: Record<string, string[]> = {
  planning: [
    'Analyzing domain...',
    'Identifying competitors...',
    'Mapping regulatory landscape...',
    'Setting research scope...',
    'Preparing discovery plan...',
  ],
  discovery: [
    'Researching market size...',
    'Analyzing customer segments...',
    'Mapping pain points...',
    'Building competitive profiles...',
    'Synthesizing market data...',
  ],
  strategy: [
    'Building business model...',
    'Designing go-to-market strategy...',
    'Projecting financials...',
    'Calculating unit economics...',
    'Defining revenue streams...',
  ],
  delivery: [
    'Writing product requirements...',
    'Designing system architecture...',
    'Assessing legal requirements...',
    'Mapping technical components...',
    'Defining user stories...',
  ],
  quality: [
    'Validating outputs...',
    'Checking consistency...',
    'Calibrating confidence scores...',
    'Cross-referencing data...',
    'Finalizing quality assessment...',
  ],
  design: [
    'Designing wireframes...',
    'Building prototype...',
    'Mapping user flows...',
    'Creating screen layouts...',
  ],
  synthesis: [
    'Generating executive summary...',
    'Creating stakeholder views...',
    'Building validation playbook...',
    'Synthesizing recommendations...',
  ],
  default: [
    'Processing...',
    'Analyzing data...',
    'Generating insights...',
    'Building output...',
  ],
};

interface ActivityIndicatorProps {
  phase?: string;
  customMessages?: string[];
  interval?: number;
  showSpinner?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function ActivityIndicator({
  phase = 'default',
  customMessages,
  interval = 3000,
  showSpinner = true,
  size = 'md',
}: ActivityIndicatorProps) {
  const messages = customMessages || ACTIVITY_MESSAGES[phase.toLowerCase()] || ACTIVITY_MESSAGES.default;
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const rotateMessage = useCallback(() => {
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % messages.length);
      setIsTransitioning(false);
    }, 150);
  }, [messages.length]);

  useEffect(() => {
    const timer = setInterval(rotateMessage, interval);
    return () => clearInterval(timer);
  }, [rotateMessage, interval]);

  const sizeStyles = {
    sm: { fontSize: '12px', iconSize: 12, gap: '6px' },
    md: { fontSize: '14px', iconSize: 16, gap: '8px' },
    lg: { fontSize: '16px', iconSize: 20, gap: '10px' },
  };

  const { fontSize, iconSize, gap } = sizeStyles[size];

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap,
      }}
    >
      {showSpinner && (
        <Loader2
          size={iconSize}
          className="v4-spin"
          style={{ color: 'var(--v4-accent)' }}
        />
      )}
      <span
        style={{
          fontSize,
          color: 'var(--v4-text-secondary)',
          transition: 'opacity 150ms ease',
          opacity: isTransitioning ? 0 : 1,
        }}
      >
        {messages[currentIndex]}
      </span>
    </div>
  );
}

interface ThinkingDotsProps {
  text?: string;
  size?: 'sm' | 'md';
}

export function ThinkingDots({ text = 'Thinking', size = 'md' }: ThinkingDotsProps) {
  const dotSize = size === 'sm' ? '3px' : '4px';
  const fontSize = size === 'sm' ? '12px' : '13px';
  const gap = size === 'sm' ? '3px' : '4px';

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
      }}
    >
      {text && (
        <span style={{ fontSize, color: 'var(--v4-text-muted)' }}>{text}</span>
      )}
      <span className="v4-thinking-dots">
        <span style={{ width: dotSize, height: dotSize, marginRight: gap }} />
        <span style={{ width: dotSize, height: dotSize, marginRight: gap }} />
        <span style={{ width: dotSize, height: dotSize }} />
      </span>
    </div>
  );
}

export default ActivityIndicator;
