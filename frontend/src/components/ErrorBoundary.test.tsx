import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ErrorBoundary } from './ErrorBoundary';

// Component that throws an error for testing
function ThrowError({ error }: { error: Error }) {
  throw error;
}

// Component that renders normally
function NormalComponent() {
  return <div>Normal content</div>;
}

describe('ErrorBoundary', () => {
  // Suppress console.error during tests since we expect errors
  const originalError = console.error;

  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalError;
  });

  // ─── Basic Rendering ──────────────────────────────────────────────
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <NormalComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Normal content')).toBeInTheDocument();
  });

  it('renders error UI when child component throws', () => {
    const testError = new Error('Test error message');

    render(
      <ErrorBoundary>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText(/We encountered an unexpected error/)).toBeInTheDocument();
  });

  // ─── Error Details ─────────────────────────────────────────────────
  it('shows component name in error display when provided', () => {
    const testError = new Error('Test error');

    render(
      <ErrorBoundary componentName="TestComponent">
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Error occurred in:/)).toBeInTheDocument();
    expect(screen.getByText('TestComponent')).toBeInTheDocument();
  });

  it('shows technical details when toggle is clicked', () => {
    const testError = new Error('Detailed error message');

    render(
      <ErrorBoundary>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    // Details should be hidden initially - check for "Error:" label which is in details
    expect(screen.queryByText('Error:')).not.toBeInTheDocument();

    // Click to show details
    fireEvent.click(screen.getByText('Show technical details'));

    // Details should now be visible - check for the label
    expect(screen.getByText('Error:')).toBeInTheDocument();
    expect(screen.getByText('Hide technical details')).toBeInTheDocument();
  });

  it('hides technical details when toggle is clicked again', () => {
    const testError = new Error('Detailed error message');

    render(
      <ErrorBoundary>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    // Show details
    fireEvent.click(screen.getByText('Show technical details'));
    expect(screen.getByText('Error:')).toBeInTheDocument();

    // Hide details
    fireEvent.click(screen.getByText('Hide technical details'));
    expect(screen.queryByText('Error:')).not.toBeInTheDocument();
  });

  // ─── Recovery Actions ──────────────────────────────────────────────
  it('calls onRetry when Try Again button is clicked', () => {
    const onRetry = vi.fn();
    const testError = new Error('Test error');

    render(
      <ErrorBoundary onRetry={onRetry}>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    fireEvent.click(screen.getByText('Try Again'));

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('calls onGoHome when Go Home button is clicked', () => {
    const onGoHome = vi.fn();
    const testError = new Error('Test error');

    render(
      <ErrorBoundary onGoHome={onGoHome}>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    fireEvent.click(screen.getByText('Go Home'));

    expect(onGoHome).toHaveBeenCalledTimes(1);
  });

  it('resets error state when Try Again is clicked', () => {
    const onRetry = vi.fn();
    let shouldThrow = true;

    function ConditionalThrow() {
      if (shouldThrow) {
        throw new Error('Conditional error');
      }
      return <div>Recovered content</div>;
    }

    const { rerender } = render(
      <ErrorBoundary onRetry={onRetry}>
        <ConditionalThrow />
      </ErrorBoundary>
    );

    // Error UI should be shown
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    // Stop throwing errors
    shouldThrow = false;

    // Click Try Again
    fireEvent.click(screen.getByText('Try Again'));

    // Re-render with the updated state
    rerender(
      <ErrorBoundary onRetry={onRetry}>
        <ConditionalThrow />
      </ErrorBoundary>
    );

    // Should show recovered content
    expect(screen.getByText('Recovered content')).toBeInTheDocument();
  });

  // ─── Error Callbacks ───────────────────────────────────────────────
  it('calls onError with error and errorInfo when error is caught', () => {
    const onError = vi.fn();
    const testError = new Error('Test error');

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError).toHaveBeenCalledWith(
      testError,
      expect.objectContaining({
        componentStack: expect.any(String),
      })
    );
  });

  it('logs error to console when caught', () => {
    const testError = new Error('Console test error');

    render(
      <ErrorBoundary>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    expect(console.error).toHaveBeenCalledWith(
      '[ErrorBoundary] Caught error:',
      testError
    );
  });

  // ─── Custom Fallback ───────────────────────────────────────────────
  it('renders custom fallback when provided', () => {
    const testError = new Error('Test error');
    const customFallback = <div>Custom error fallback</div>;

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom error fallback')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });

  // ─── Error Display ─────────────────────────────────────────────────
  it('displays error name and message in details', () => {
    const testError = new Error('Specific error message');
    testError.name = 'CustomError';

    render(
      <ErrorBoundary>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    // Show details
    fireEvent.click(screen.getByText('Show technical details'));

    // Check that the error code element contains both name and message
    const codeElement = screen.getByText((content, element) => {
      return element?.tagName === 'CODE' && content.includes('CustomError') && content.includes('Specific error message');
    });
    expect(codeElement).toBeInTheDocument();
  });

  // ─── Action Buttons ────────────────────────────────────────────────
  it('renders Try Again and Go Home buttons', () => {
    const testError = new Error('Test error');

    render(
      <ErrorBoundary>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Go Home/i })).toBeInTheDocument();
  });

  // ─── Navigation Fallback ───────────────────────────────────────────
  it('navigates to root when Go Home clicked without onGoHome handler', () => {
    const testError = new Error('Test error');
    const originalLocation = window.location;

    // Mock window.location.href setter
    delete (window as { location?: Location }).location;
    window.location = { ...originalLocation, href: '' };
    Object.defineProperty(window.location, 'href', {
      set: vi.fn(),
      get: () => '',
    });

    render(
      <ErrorBoundary>
        <ThrowError error={testError} />
      </ErrorBoundary>
    );

    fireEvent.click(screen.getByText('Go Home'));

    // Restore original location
    window.location = originalLocation;
  });

  // ─── Multiple Errors ───────────────────────────────────────────────
  it('handles sequential error and recovery', () => {
    const onError = vi.fn();
    const onRetry = vi.fn();
    const error1 = new Error('First error');

    render(
      <ErrorBoundary onError={onError} onRetry={onRetry}>
        <ThrowError error={error1} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError).toHaveBeenCalledWith(error1, expect.any(Object));

    // Click Try Again - this triggers the retry callback
    fireEvent.click(screen.getByText('Try Again'));

    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
