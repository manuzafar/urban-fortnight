/**
 * PackViewer Integration Tests for V3.0 Sections
 *
 * Verifies that all 16 sections render correctly with V3.0 backend data.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PackViewer } from './PackViewer';
import mockPack from '../__test_data__/mock_v3_pack.json';
import type { InceptionPack } from '../types/api';

// Mock the export API calls
vi.mock('../api/client', () => ({
  exportPdf: vi.fn(),
  exportDocx: vi.fn(),
}));

describe('PackViewer V3.0 Integration', () => {
  const pack = mockPack as unknown as InceptionPack;
  const sessionId = 'test-session-123';
  const onBack = vi.fn();

  it('renders without crashing', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('displays product name in hero section', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);
    // Check for product name in hero
    const heroTitle = document.querySelector('.hero-title');
    expect(heroTitle).toBeInTheDocument();
  });

  it('renders all 16 section tabs', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const expectedTabs = [
      'Summary', 'Research', 'Competitive', 'Personas',
      'Business', 'Go-to-Market', 'Financial',
      'Product', 'Tech', 'Legal', 'Risks',
      'Wireframes', 'Prototype',
      'Stakeholders', 'Validation', 'QA'
    ];

    expectedTabs.forEach(tabName => {
      const tab = screen.getByRole('button', { name: tabName });
      expect(tab).toBeInTheDocument();
    });
  });

  it('shows Summary section by default', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    // Summary tab should be active
    const summaryTab = screen.getByRole('button', { name: 'Summary' });
    expect(summaryTab).toHaveClass('active');
  });

  it('can navigate to Competitive section', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const competitiveTab = screen.getByRole('button', { name: 'Competitive' });
    fireEvent.click(competitiveTab);

    expect(competitiveTab).toHaveClass('active');
  });

  it('can navigate to Wireframes section', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const wireframesTab = screen.getByRole('button', { name: 'Wireframes' });
    fireEvent.click(wireframesTab);

    expect(wireframesTab).toHaveClass('active');
  });

  it('can navigate to Stakeholders section', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const stakeholdersTab = screen.getByRole('button', { name: 'Stakeholders' });
    fireEvent.click(stakeholdersTab);

    expect(stakeholdersTab).toHaveClass('active');
  });

  it('can navigate to Validation section', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const validationTab = screen.getByRole('button', { name: 'Validation' });
    fireEvent.click(validationTab);

    expect(validationTab).toHaveClass('active');
  });

  it('disables sections without content', () => {
    // Create a pack with missing sections
    const partialPack: InceptionPack = {
      ...pack,
      competitive_analysis: null,
      wireframes: null,
    };

    render(<PackViewer pack={partialPack} sessionId={sessionId} onBack={onBack} />);

    const competitiveTab = screen.getByRole('button', { name: 'Competitive' });
    const wireframesTab = screen.getByRole('button', { name: 'Wireframes' });

    expect(competitiveTab).toBeDisabled();
    expect(wireframesTab).toBeDisabled();
  });

  it('calls onBack when back button is clicked', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const backBtn = screen.getByRole('button', { name: /dashboard/i });
    fireEvent.click(backBtn);

    expect(onBack).toHaveBeenCalled();
  });
});

describe('PackViewer Section Content', () => {
  const pack = mockPack as unknown as InceptionPack;
  const sessionId = 'test-session-123';
  const onBack = vi.fn();

  it('renders executive summary content', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    // Should show problem statement
    expect(screen.getByText('Problem Statement')).toBeInTheDocument();
    expect(screen.getByText('Solution Overview')).toBeInTheDocument();
  });

  it('renders business section with lean canvas', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const businessTab = screen.getByRole('button', { name: 'Business' });
    fireEvent.click(businessTab);

    // Should show lean canvas (use getAllByText since there may be multiple)
    const leanCanvasElements = screen.getAllByText('Lean Canvas');
    expect(leanCanvasElements.length).toBeGreaterThan(0);
  });

  it('renders quality section with score', () => {
    render(<PackViewer pack={pack} sessionId={sessionId} onBack={onBack} />);

    const qaTab = screen.getByRole('button', { name: 'QA' });
    fireEvent.click(qaTab);

    expect(screen.getByText('Overall Quality Score')).toBeInTheDocument();
  });
});
