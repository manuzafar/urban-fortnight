import React from 'react';
import { Zap, Compass, Microscope, Clock, Shield, Check } from 'lucide-react';

interface ModeSelectorProps {
  selected: 'quick' | 'guided' | 'deep';
  onSelect: (mode: 'quick' | 'guided' | 'deep') => void;
  disabled?: boolean;
}

const MODES = [
  {
    id: 'quick' as const,
    icon: Zap,
    title: 'Quick Mode',
    subtitle: 'AI generates everything',
    duration: '3-5 min',
    evidence: 'E3-E4',
    description: 'Best for: Early exploration, quick validation, time-constrained projects',
    features: ['Full AI generation', 'No checkpoints', 'Instant results'],
    color: '#22c55e', // green
  },
  {
    id: 'guided' as const,
    icon: Compass,
    title: 'Guided Mode',
    subtitle: 'AI generates + you review',
    duration: '5-8 min',
    evidence: 'E2-E4',
    description: 'Best for: Balanced approach, some customization, learning the frameworks',
    features: ['AI with checkpoints', 'Optional interviews', 'Edit any section'],
    recommended: true,
    color: '#3b82f6', // blue
  },
  {
    id: 'deep' as const,
    icon: Microscope,
    title: 'Deep Mode',
    subtitle: 'You provide interviews, AI synthesizes',
    duration: 'Days-weeks',
    evidence: 'E1-E2',
    description: 'Best for: Serious validation, investor-ready research, real customer data',
    features: ['Real interview input', 'Teresa Torres methodology', 'Highest evidence quality'],
    color: '#8b5cf6', // purple
  },
];

export function ModeSelector({ selected, onSelect, disabled }: ModeSelectorProps) {
  return (
    <div className="mode-selector-container">
      <div className="mode-selector-header">
        <h2>Choose Your Discovery Mode</h2>
        <p>Select how deeply you want to validate your product idea</p>
      </div>

      <div className="mode-selector-grid">
        {MODES.map((mode) => {
          const Icon = mode.icon;
          const isSelected = selected === mode.id;

          return (
            <button
              key={mode.id}
              className={`mode-card ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
              onClick={() => !disabled && onSelect(mode.id)}
              style={{
                '--mode-color': mode.color,
                borderColor: isSelected ? mode.color : undefined,
              } as React.CSSProperties}
              disabled={disabled}
            >
              {mode.recommended && (
                <span className="recommended-badge">Recommended</span>
              )}

              <div className="mode-header">
                <div className="mode-icon" style={{ backgroundColor: `${mode.color}20` }}>
                  <Icon size={24} color={mode.color} />
                </div>
                <div className="mode-titles">
                  <h3>{mode.title}</h3>
                  <p className="mode-subtitle">{mode.subtitle}</p>
                </div>
              </div>

              <p className="mode-description">{mode.description}</p>

              <div className="mode-meta">
                <span className="mode-meta-item">
                  <Clock size={14} />
                  {mode.duration}
                </span>
                <span className="mode-meta-item">
                  <Shield size={14} />
                  Evidence: {mode.evidence}
                </span>
              </div>

              <ul className="mode-features">
                {mode.features.map((feature) => (
                  <li key={feature}>
                    <Check size={12} color={mode.color} />
                    {feature}
                  </li>
                ))}
              </ul>

              {isSelected && (
                <div className="selected-indicator">
                  <Check size={16} />
                  Selected
                </div>
              )}
            </button>
          );
        })}
      </div>

      <style>{`
        .mode-selector-container {
          padding: 24px 0;
        }

        .mode-selector-header {
          text-align: center;
          margin-bottom: 32px;
        }

        .mode-selector-header h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        .mode-selector-header p {
          margin: 0;
          color: var(--text-secondary, #6b7280);
        }

        .mode-selector-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;
          max-width: 960px;
          margin: 0 auto;
        }

        .mode-card {
          position: relative;
          display: flex;
          flex-direction: column;
          padding: 24px;
          background: white;
          border: 2px solid var(--border-color, #e5e7eb);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
        }

        .mode-card:hover:not(.disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .mode-card.selected {
          border-width: 2px;
          background: linear-gradient(
            to bottom,
            color-mix(in srgb, var(--mode-color) 5%, white),
            white
          );
        }

        .mode-card.disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .recommended-badge {
          position: absolute;
          top: -10px;
          right: 16px;
          padding: 4px 12px;
          background: var(--mode-color);
          color: white;
          font-size: 11px;
          font-weight: 600;
          border-radius: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .mode-header {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 16px;
        }

        .mode-icon {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 12px;
          flex-shrink: 0;
        }

        .mode-titles h3 {
          margin: 0 0 4px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary, #1a1a2e);
        }

        .mode-subtitle {
          margin: 0;
          font-size: 14px;
          color: var(--text-secondary, #6b7280);
        }

        .mode-description {
          margin: 0 0 16px 0;
          font-size: 13px;
          color: var(--text-secondary, #6b7280);
          line-height: 1.5;
        }

        .mode-meta {
          display: flex;
          gap: 16px;
          margin-bottom: 16px;
        }

        .mode-meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: var(--text-secondary, #6b7280);
        }

        .mode-features {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .mode-features li {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: var(--text-primary, #1a1a2e);
        }

        .selected-indicator {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          margin-top: 16px;
          padding: 8px 0;
          border-top: 1px solid var(--border-color, #e5e7eb);
          color: var(--mode-color);
          font-size: 13px;
          font-weight: 500;
        }

        @media (max-width: 768px) {
          .mode-selector-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default ModeSelector;
