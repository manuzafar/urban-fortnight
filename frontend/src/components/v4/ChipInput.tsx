/**
 * V4 Chip Input Component
 * Tag/chip input for form fields
 * Accessible implementation with ARIA attributes and keyboard navigation
 */

import { useState, useRef, useId, type KeyboardEvent, type ChangeEvent } from 'react';
import '../../styles/theme-v4.css';

interface ChipInputProps {
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  suggestions?: string[];
  label?: string;
  'aria-label'?: string;
}

export function ChipInput({
  value,
  onChange,
  placeholder = 'Add...',
  suggestions = [],
  label,
  'aria-label': ariaLabel,
}: ChipInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [announcement, setAnnouncement] = useState('');
  const [focusedChipIndex, setFocusedChipIndex] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const chipRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const inputId = useId();

  const announceChange = (message: string) => {
    setAnnouncement(message);
    // Clear after a short delay to allow for new announcements
    setTimeout(() => setAnnouncement(''), 1000);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      if (!value.includes(inputValue.trim())) {
        onChange([...value, inputValue.trim()]);
        announceChange(`Added ${inputValue.trim()}`);
      }
      setInputValue('');
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      // Focus the last chip instead of removing it directly
      setFocusedChipIndex(value.length - 1);
      chipRefs.current[value.length - 1]?.focus();
    } else if (e.key === 'ArrowLeft' && !inputValue && value.length > 0) {
      // Navigate to chips
      setFocusedChipIndex(value.length - 1);
      chipRefs.current[value.length - 1]?.focus();
    }
  };

  const handleChipKeyDown = (e: KeyboardEvent<HTMLButtonElement>, index: number, tag: string) => {
    if (e.key === 'Delete' || e.key === 'Backspace') {
      e.preventDefault();
      handleRemove(tag);
      // Focus next chip or input
      if (value.length > 1) {
        const nextIndex = index >= value.length - 1 ? index - 1 : index;
        setFocusedChipIndex(nextIndex);
        setTimeout(() => chipRefs.current[nextIndex]?.focus(), 0);
      } else {
        setFocusedChipIndex(null);
        inputRef.current?.focus();
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      setFocusedChipIndex(index - 1);
      chipRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight') {
      if (index < value.length - 1) {
        setFocusedChipIndex(index + 1);
        chipRefs.current[index + 1]?.focus();
      } else {
        setFocusedChipIndex(null);
        inputRef.current?.focus();
      }
    } else if (e.key === 'Escape') {
      setFocusedChipIndex(null);
      inputRef.current?.focus();
    }
  };

  const handleRemove = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
    announceChange(`Removed ${tagToRemove}`);
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (!value.includes(suggestion)) {
      onChange([...value, suggestion]);
      announceChange(`Added ${suggestion}`);
    } else {
      onChange(value.filter((v) => v !== suggestion));
      announceChange(`Removed ${suggestion}`);
    }
  };

  const handleSuggestionKeyDown = (e: KeyboardEvent<HTMLButtonElement>, suggestion: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleSuggestionClick(suggestion);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  return (
    <div>
      {/* Screen reader live region for announcements */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        style={{
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: 0,
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          border: 0,
        }}
      >
        {announcement}
      </div>

      <div
        role="group"
        aria-labelledby={label ? `${inputId}-label` : undefined}
        aria-label={ariaLabel || (label ? undefined : 'Tag input')}
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
        onClick={() => inputRef.current?.focus()}
      >
        {value.map((tag, index) => (
          <span
            key={tag}
            role="listitem"
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
            <button
              ref={(el) => { chipRefs.current[index] = el; }}
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleRemove(tag);
              }}
              onKeyDown={(e) => handleChipKeyDown(e, index, tag)}
              aria-label={`Remove ${tag}`}
              style={{
                cursor: 'pointer',
                opacity: focusedChipIndex === index ? 1 : 0.5,
                fontSize: '14px',
                background: 'none',
                border: 'none',
                padding: '0 2px',
                lineHeight: 1,
                color: 'inherit',
                borderRadius: '2px',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '1';
              }}
              onMouseLeave={(e) => {
                if (focusedChipIndex !== index) {
                  e.currentTarget.style.opacity = '0.5';
                }
              }}
              onFocus={() => setFocusedChipIndex(index)}
              onBlur={() => setFocusedChipIndex(null)}
            >
              <span aria-hidden="true">×</span>
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          id={inputId}
          type="text"
          value={inputValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={value.length === 0 ? placeholder : ''}
          aria-label={ariaLabel || label || 'Add new tag'}
          aria-describedby={value.length > 0 ? `${inputId}-count` : undefined}
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
      {value.length > 0 && (
        <span id={`${inputId}-count`} className="sr-only" style={{ position: 'absolute', width: '1px', height: '1px', padding: 0, margin: '-1px', overflow: 'hidden', clip: 'rect(0, 0, 0, 0)', whiteSpace: 'nowrap', border: 0 }}>
          {value.length} {value.length === 1 ? 'tag' : 'tags'} added
        </span>
      )}
      {suggestions.length > 0 && (
        <div
          role="group"
          aria-label="Suggested tags"
          style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}
        >
          {suggestions.map((suggestion) => {
            const isSelected = value.includes(suggestion);
            return (
              <button
                key={suggestion}
                type="button"
                onClick={() => handleSuggestionClick(suggestion)}
                onKeyDown={(e) => handleSuggestionKeyDown(e, suggestion)}
                aria-pressed={isSelected}
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
                {suggestion}
              </button>
            );
          })}
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
  label?: string;
  'aria-label'?: string;
}

export function ChipSelect({
  options,
  selected,
  onChange,
  multiSelect = true,
  label,
  'aria-label': ariaLabel,
}: ChipSelectProps) {
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const groupId = useId();

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

  const handleKeyDown = (e: KeyboardEvent<HTMLButtonElement>, index: number, option: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick(option);
    } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      const nextIndex = (index + 1) % options.length;
      setFocusedIndex(nextIndex);
      (e.currentTarget.parentElement?.children[nextIndex] as HTMLButtonElement)?.focus();
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      const prevIndex = (index - 1 + options.length) % options.length;
      setFocusedIndex(prevIndex);
      (e.currentTarget.parentElement?.children[prevIndex] as HTMLButtonElement)?.focus();
    }
  };

  return (
    <div
      role={multiSelect ? 'group' : 'radiogroup'}
      aria-labelledby={label ? `${groupId}-label` : undefined}
      aria-label={ariaLabel || (label ? undefined : multiSelect ? 'Select options' : 'Select one option')}
      style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}
    >
      {label && (
        <span id={`${groupId}-label`} className="sr-only">
          {label}
        </span>
      )}
      {options.map((option, index) => {
        const isSelected = selected.includes(option);
        return (
          <button
            key={option}
            type="button"
            role={multiSelect ? undefined : 'radio'}
            aria-pressed={multiSelect ? isSelected : undefined}
            aria-checked={multiSelect ? undefined : isSelected}
            tabIndex={!multiSelect && focusedIndex !== -1 && focusedIndex !== index && !isSelected ? -1 : 0}
            onClick={() => handleClick(option)}
            onKeyDown={(e) => handleKeyDown(e, index, option)}
            onFocus={() => setFocusedIndex(index)}
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
          </button>
        );
      })}
    </div>
  );
}

export default ChipInput;
