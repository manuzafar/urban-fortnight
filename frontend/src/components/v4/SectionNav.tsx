/**
 * V4 Section Navigation Component
 * Sidebar navigation with status dots for results viewer
 */

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

const phases = ['Overview', 'Discovery', 'Strategy', 'Delivery', 'Design', 'Synthesis', 'Quality'];

export function SectionNav({ sections, activeSection, onSectionChange }: SectionNavProps) {
  const sectionsByPhase = phases.reduce((acc, phase) => {
    acc[phase] = sections.filter((s) => s.phase === phase);
    return acc;
  }, {} as Record<string, NavSection[]>);

  return (
    <nav>
      {phases.map((phase) => {
        const phaseSections = sectionsByPhase[phase];
        if (!phaseSections || phaseSections.length === 0) return null;

        return (
          <div key={phase} style={{ padding: '16px 0 8px' }}>
            <div
              style={{
                padding: '0 16px 8px',
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                color: 'var(--v4-text-muted)',
              }}
            >
              {phase}
            </div>
            {phaseSections.map((section) => {
              const isActive = section.id === activeSection;
              return (
                <div
                  key={section.id}
                  onClick={() => onSectionChange(section.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 16px',
                    fontSize: '13px',
                    color: isActive ? 'var(--v4-text)' : 'var(--v4-text-secondary)',
                    cursor: 'pointer',
                    borderLeft: `2px solid ${isActive ? 'var(--v4-accent)' : 'transparent'}`,
                    background: isActive ? 'var(--v4-bg)' : 'transparent',
                    fontWeight: isActive ? 500 : 400,
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'var(--v4-bg)';
                      e.currentTarget.style.color = 'var(--v4-text)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = 'var(--v4-text-secondary)';
                    }
                  }}
                >
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: isActive ? 'var(--v4-accent)' : 'var(--v4-text-muted)',
                      width: '20px',
                    }}
                  >
                    {section.number}
                  </span>
                  <span style={{ flex: 1 }}>{section.title}</span>
                  <span
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      background:
                        section.status === 'done'
                          ? 'var(--v4-success)'
                          : section.status === 'warn'
                          ? 'var(--v4-warning)'
                          : 'var(--v4-text-muted)',
                    }}
                  />
                </div>
              );
            })}
          </div>
        );
      })}
    </nav>
  );
}

export default SectionNav;
