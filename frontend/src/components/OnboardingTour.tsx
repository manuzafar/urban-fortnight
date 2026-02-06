import Joyride, { STATUS } from 'react-joyride';
import type { Step, CallBackProps } from 'react-joyride';

const TOUR_STEPS: Step[] = [
  {
    target: '.results-nav',
    content: 'Your inception pack has 7 sections. Use this navigation to jump between them — from Executive Summary to Quality Assessment.',
    disableBeacon: true,
    placement: 'right',
  },
  {
    target: '.results-nav-item:nth-child(1)',
    content: 'Start with the Executive Summary — a decision-ready brief for stakeholders who need the big picture.',
    placement: 'right',
  },
  {
    target: '.results-nav-item:nth-child(4)',
    content: 'The PRD section contains detailed requirements, user stories, and epics for your product team.',
    placement: 'right',
  },
  {
    target: '.results-nav-item:nth-child(5)',
    content: 'Technical Architecture outlines the system design, tech stack, and integration points.',
    placement: 'right',
  },
  {
    target: '[data-tour="export-button"]',
    content: 'Export your pack as PDF or Word to share with stakeholders. You can export the full pack or just the current section.',
    placement: 'bottom',
  },
  {
    target: '.feedback-banner',
    content: 'We\'d love your feedback! Schedule a quick call or share your thoughts to help us improve.',
    placement: 'bottom',
  },
];

interface OnboardingTourProps {
  run: boolean;
  onComplete: () => void;
}

export function OnboardingTour({ run, onComplete }: OnboardingTourProps) {
  const handleCallback = (data: CallBackProps) => {
    const { status } = data;
    if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
      onComplete();
    }
  };

  return (
    <Joyride
      steps={TOUR_STEPS}
      run={run}
      continuous
      showProgress
      showSkipButton
      scrollToFirstStep
      disableScrolling={false}
      callback={handleCallback}
      locale={{
        back: 'Back',
        close: 'Close',
        last: 'Done',
        next: 'Next',
        skip: 'Skip tour',
      }}
      styles={{
        options: {
          arrowColor: '#1a1a2e',
          backgroundColor: '#1a1a2e',
          overlayColor: 'rgba(0, 0, 0, 0.7)',
          primaryColor: '#667eea',
          textColor: '#e9ecf5',
          zIndex: 10000,
        },
        tooltip: {
          borderRadius: 12,
          padding: 20,
        },
        tooltipTitle: {
          fontSize: 16,
          fontWeight: 600,
        },
        tooltipContent: {
          fontSize: 14,
          lineHeight: 1.6,
        },
        buttonNext: {
          backgroundColor: '#667eea',
          borderRadius: 8,
          color: 'white',
          fontWeight: 600,
          padding: '10px 20px',
        },
        buttonBack: {
          color: '#e9ecf5',
          marginRight: 10,
        },
        buttonSkip: {
          color: 'rgba(233, 236, 245, 0.6)',
        },
        spotlight: {
          borderRadius: 8,
        },
      }}
    />
  );
}
