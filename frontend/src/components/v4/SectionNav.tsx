/**
 * V4 Section Navigation Component
 * Sidebar navigation with collapsible phase groups and status dots
 */

import { useState, useMemo } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import '../../styles/theme-v4.css';

export interface NavSection {
  id: string;
  number: string;
  title: string;
  phase: string;
  status: 'done' | 'warn' | 'pending';
}

interface SectionNavProps {
  sections: NavSection[];
  activeSection: string;
  onSectionChange: (sectionId: string) => void;
}

const phases = ['V4 Discovery', 'Overview', 'Discovery', 'Strategy', 'Delivery', 'Design', 'Synthesis', 'Quality'];

export function SectionNav({ sections, activeSection, onSectionChange }: SectionNavProps) {
  const [collapsedPhases, setCollapsedPhases] = useState<Set<string>>(new Set());

  const sectionsByPhase = useMemo(() => {
    return phases.reduce((acc, phase) => {
      acc[phase] = sections.filter((s) => s.phase === phase);
      return acc;
    }, {} as Record<string, NavSection[]>);
  }, [sections]);

  // Calculate completion stats
  const completionStats = useMemo(() => {
    const total = sections.length;
    const done = sections.filter(s => s.status === 'done').length;
    return { total, done, percentage: Math.round((done / total) * 100) };
  }, [sections]);

  const togglePhase = (phase: string) => {
    setCollapsedPhases(prev => {
      const next = new Set(prev);
      if (next.has(phase)) {
        next.delete(phase);
      } else {
        next.add(phase);
      }
      return next;
    });
  };

  // Find which phase the active section is in
  const activePhase = sections.find(s => s.id === activeSection)?.phase;

  return (
    <nav className="section-nav">
      {/* Progress Summary */}
      <div className="sn-progress">
        <div className="sn-progress-header">
          <span className="sn-progress-label">Completion</span>
          <span className="sn-progress-value">{completionStats.percentage}%</span>
        </div>
        <div className="sn-progress-bar">
          <div
            className="sn-progress-fill"
            style={{ width: `${completionStats.percentage}%` }}
          />
        </div>
        <div className="sn-progress-count">
          {completionStats.done} of {completionStats.total} sections
        </div>
      </div>

      {/* Phase Groups */}
      {phases.map((phase) => {
        const phaseSections = sectionsByPhase[phase];
        if (!phaseSections || phaseSections.length === 0) return null;

        const isCollapsed = collapsedPhases.has(phase);
        const isActivePhase = phase === activePhase;
        const phaseComplete = phaseSections.every(s => s.status === 'done');
        const phaseHasWarnings = phaseSections.some(s => s.status === 'warn');

        return (
          <div key={phase} className={`sn-phase ${isActivePhase ? 'active' : ''}`}>
            <button
              className="sn-phase-header"
              onClick={() => togglePhase(phase)}
            >
              <span className="sn-phase-chevron">
                {isCollapsed ? <ChevronRight size={14} /> : <ChevronDown size={14} />}
              </span>
              <span className="sn-phase-name">{phase}</span>
              <span className={`sn-phase-dot ${phaseComplete ? 'done' : phaseHasWarnings ? 'warn' : ''}`} />
            </button>

            {!isCollapsed && (
              <div className="sn-sections">
                {phaseSections.map((section) => {
                  const isActive = section.id === activeSection;
                  return (
                    <button
                      key={section.id}
                      className={`sn-section ${isActive ? 'active' : ''}`}
                      onClick={() => onSectionChange(section.id)}
                    >
                      <span className="sn-section-number">{section.number}</span>
                      <span className="sn-section-title">{section.title}</span>
                      <span className={`sn-section-dot ${section.status}`} />
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}

      <style>{`
        .section-nav {
          padding: 0;
        }

        .sn-progress {
          padding: 16px;
          border-bottom: 1px solid var(--v4-border-subtle);
        }

        .sn-progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .sn-progress-label {
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--v4-text-muted);
        }

        .sn-progress-value {
          font-size: 13px;
          font-weight: 600;
          color: var(--v4-text);
          font-family: var(--v4-font-display);
        }

        .sn-progress-bar {
          height: 4px;
          background: var(--v4-bg-subtle);
          border-radius: 2px;
          overflow: hidden;
        }

        .sn-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--v4-success), var(--v4-success));
          border-radius: 2px;
          transition: width 0.5s ease;
        }

        .sn-progress-count {
          font-size: 11px;
          color: var(--v4-text-muted);
          margin-top: 6px;
        }

        .sn-phase {
          border-bottom: 1px solid var(--v4-border-subtle);
        }

        .sn-phase:last-child {
          border-bottom: none;
        }

        .sn-phase.active {
          background: var(--v4-accent-lighter);
        }

        .sn-phase-header {
          display: flex;
          align-items: center;
          gap: 8px;
          width: 100%;
          padding: 12px 16px;
          background: none;
          border: none;
          cursor: pointer;
          text-align: left;
          transition: background 0.15s ease;
        }

        .sn-phase-header:hover {
          background: var(--v4-bg-subtle);
        }

        .sn-phase.active .sn-phase-header:hover {
          background: var(--v4-accent-light);
        }

        .sn-phase-chevron {
          color: var(--v4-text-muted);
          display: flex;
          align-items: center;
        }

        .sn-phase-name {
          flex: 1;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--v4-text-muted);
        }

        .sn-phase.active .sn-phase-name {
          color: var(--v4-accent);
        }

        .sn-phase-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--v4-text-muted);
          opacity: 0.5;
        }

        .sn-phase-dot.done {
          background: var(--v4-success);
          opacity: 1;
        }

        .sn-phase-dot.warn {
          background: var(--v4-warning);
          opacity: 1;
        }

        .sn-sections {
          padding: 0 8px 8px 8px;
          animation: sn-expand 0.2s ease;
        }

        @keyframes sn-expand {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .sn-section {
          display: flex;
          align-items: center;
          gap: 10px;
          width: 100%;
          padding: 11px 12px;
          margin-left: 8px;
          background: none;
          border: none;
          border-left: 2px solid transparent;
          border-radius: 0 var(--v4-radius-sm) var(--v4-radius-sm) 0;
          cursor: pointer;
          text-align: left;
          transition: all 0.15s ease;
        }

        .sn-section:hover {
          background: var(--v4-bg-subtle);
        }

        .sn-section.active {
          background: var(--v4-accent-light);
          border-left-color: var(--v4-accent);
        }

        .sn-section-number {
          font-size: 11px;
          font-weight: 600;
          color: var(--v4-text-muted);
          width: 20px;
          font-family: var(--v4-font-body);
        }

        .sn-section.active .sn-section-number {
          color: var(--v4-accent);
        }

        .sn-section-title {
          flex: 1;
          font-size: 13px;
          color: var(--v4-text-secondary);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .sn-section.active .sn-section-title {
          color: var(--v4-text);
          font-weight: 500;
        }

        .sn-section-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .sn-section-dot.done {
          background: var(--v4-success);
        }

        .sn-section-dot.warn {
          background: var(--v4-warning);
        }

        .sn-section-dot.pending {
          background: var(--v4-text-muted);
          opacity: 0.5;
        }
      `}</style>
    </nav>
  );
}

export default SectionNav;
