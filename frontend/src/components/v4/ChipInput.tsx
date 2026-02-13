/**
 * V4 Chip Input Component
 * Tag/chip input for form fields
 */

import { useState, type KeyboardEvent, type ChangeEvent } from 'react';
import '../../styles/theme-v4.css';

interface ChipInputProps {
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  suggestions?: string[];
}

export function ChipInput({
  value,
  onChange,
  placeholder = 'Add...',
  suggestions = [],
}: ChipInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      if (!value.includes(inputValue.trim())) {
        onChange([...value, inputValue.trim()]);
      }
      setInputValue('');
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      onChange(value.slice(0, -1));
    }
  };

  const handleRemove = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (!value.includes(suggestion)) {
      onChange([...value, suggestion]);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  return (
    <div>
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          padding: '10px 12px',
          background: 'var(--v4-surface)',
          border: '1px solid var(--v4-border)',
          borderRadius: 'var(--v4-radius)',
          minHeight: '46px',
        }}
      >
        {value.map((tag) => (
          <span
            key={tag}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 10px',
              fontSize: '13px',
              background: 'var(--v4-bg)',
              borderRadius: '4px',
            }}
          >
            {tag}
            <span
              onClick={() => handleRemove(tag)}
              style={{
                cursor: 'pointer',
                opacity: 0.5,
                fontSize: '14px',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '1';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '0.5';
              }}
            >
              ×
            </span>
          </span>
        ))}
        <input
          type="text"
          value={inputValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={value.length === 0 ? placeholder : ''}
          style={{
            flex: 1,
            minWidth: '100px',
            border: 'none',
            outline: 'none',
            fontFamily: 'inherit',
            fontSize: '14px',
            background: 'transparent',
          }}
        />
      </div>
      {suggestions.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
          {suggestions.map((suggestion) => (
            <span
              key={suggestion}
              onClick={() => handleSuggestionClick(suggestion)}
              style={{
                padding: '8px 14px',
                fontSize: '13px',
                color: value.includes(suggestion) ? 'white' : 'var(--v4-text-secondary)',
                background: value.includes(suggestion) ? 'var(--v4-text)' : 'var(--v4-bg)',
                border: `1px solid ${value.includes(suggestion) ? 'var(--v4-text)' : 'var(--v4-border)'}`,
                borderRadius: '100px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!value.includes(suggestion)) {
                  e.currentTarget.style.borderColor = 'var(--v4-text)';
                  e.currentTarget.style.color = 'var(--v4-text)';
                }
              }}
              onMouseLeave={(e) => {
                if (!value.includes(suggestion)) {
                  e.currentTarget.style.borderColor = 'var(--v4-border)';
                  e.currentTarget.style.color = 'var(--v4-text-secondary)';
                }
              }}
            >
              {suggestion}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

interface ChipSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  multiSelect?: boolean;
}

export function ChipSelect({ options, selected, onChange, multiSelect = true }: ChipSelectProps) {
  const handleClick = (option: string) => {
    if (multiSelect) {
      if (selected.includes(option)) {
        onChange(selected.filter((s) => s !== option));
      } else {
        onChange([...selected, option]);
      }
    } else {
      onChange([option]);
    }
  };

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
      {options.map((option) => {
        const isSelected = selected.includes(option);
        return (
          <span
            key={option}
            onClick={() => handleClick(option)}
            style={{
              padding: '8px 14px',
              fontSize: '13px',
              color: isSelected ? 'white' : 'var(--v4-text-secondary)',
              background: isSelected ? 'var(--v4-text)' : 'var(--v4-bg)',
              border: `1px solid ${isSelected ? 'var(--v4-text)' : 'var(--v4-border)'}`,
              borderRadius: '100px',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'var(--v4-text)';
                e.currentTarget.style.color = 'var(--v4-text)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'var(--v4-border)';
                e.currentTarget.style.color = 'var(--v4-text-secondary)';
              }
            }}
          >
            {option}
          </span>
        );
      })}
    </div>
  );
}

export default ChipInput;
