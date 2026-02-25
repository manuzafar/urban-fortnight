/**
 * Error Boundary Component for Seedform
 * Catches render errors and displays user-friendly recovery UI
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw, Home, ChevronDown, ChevronUp } from 'lucide-react';

export interface ErrorBoundaryProps {
  children: ReactNode;
  /** Optional fallback component to render when error occurs */
  fallback?: ReactNode;
  /** Called when an error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Called when user clicks "Try Again" */
  onRetry?: () => void;
  /** Called when user clicks "Go Home" */
  onGoHome?: () => void;
  /** Component name for error logging context */
  componentName?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
}

/**
 * Error Boundary - catches JavaScript errors anywhere in child component tree
 * and displays a fallback UI instead of crashing the whole app.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console
    console.error('[ErrorBoundary] Caught error:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);

    // Update state with error info
    this.setState({ errorInfo });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log additional context if componentName is provided
    if (this.props.componentName) {
      console.error(`[ErrorBoundary] Error occurred in: ${this.props.componentName}`);
    }
  }

  handleRetry = (): void => {
    // Reset error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    });

    // Call optional retry handler
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  handleGoHome = (): void => {
    // Reset error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    });

    // Call optional go home handler or navigate to root
    if (this.props.onGoHome) {
      this.props.onGoHome();
    } else {
      // Fallback: reload the page at root
      window.location.href = '/';
    }
  };

  toggleDetails = (): void => {
    this.setState((prev) => ({ showDetails: !prev.showDetails }));
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // If custom fallback is provided, render it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      const { error, errorInfo, showDetails } = this.state;

      return (
        <div className="v4-root" style={styles.container}>
          <div style={styles.card}>
            {/* Error Icon */}
            <div style={styles.iconContainer}>
              <AlertTriangle size={48} style={styles.icon} />
            </div>

            {/* Error Title */}
            <h1 style={styles.title}>Something went wrong</h1>

            {/* Error Description */}
            <p style={styles.description}>
              We encountered an unexpected error. This has been logged and we're
              working to fix it. You can try again or return to the home page.
            </p>

            {/* Component Context */}
            {this.props.componentName && (
              <p style={styles.context}>
                Error occurred in: <strong>{this.props.componentName}</strong>
              </p>
            )}

            {/* Action Buttons */}
            <div style={styles.actions}>
              <button
                onClick={this.handleRetry}
                style={styles.primaryButton}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#9a3412';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = '#c2410c';
                }}
              >
                <RefreshCw size={18} />
                Try Again
              </button>
              <button
                onClick={this.handleGoHome}
                style={styles.secondaryButton}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#f5f5f4';
                  e.currentTarget.style.borderColor = '#171717';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'rgba(0, 0, 0, 0.08)';
                }}
              >
                <Home size={18} />
                Go Home
              </button>
            </div>

            {/* Error Details Toggle */}
            <button
              onClick={this.toggleDetails}
              style={styles.detailsToggle}
            >
              {showDetails ? (
                <>
                  <ChevronUp size={16} />
                  Hide technical details
                </>
              ) : (
                <>
                  <ChevronDown size={16} />
                  Show technical details
                </>
              )}
            </button>

            {/* Technical Details */}
            {showDetails && (
              <div style={styles.detailsContainer}>
                <div style={styles.detailsSection}>
                  <strong style={styles.detailsLabel}>Error:</strong>
                  <code style={styles.errorCode}>
                    {error?.name}: {error?.message}
                  </code>
                </div>
                {error?.stack && (
                  <div style={styles.detailsSection}>
                    <strong style={styles.detailsLabel}>Stack trace:</strong>
                    <pre style={styles.stackTrace}>{error.stack}</pre>
                  </div>
                )}
                {errorInfo?.componentStack && (
                  <div style={styles.detailsSection}>
                    <strong style={styles.detailsLabel}>Component stack:</strong>
                    <pre style={styles.stackTrace}>{errorInfo.componentStack}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Styles using V4 theme variables
const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px',
    background: 'var(--v4-bg, #FAFAF9)',
  },
  card: {
    maxWidth: '500px',
    width: '100%',
    background: 'var(--v4-surface, #FFFFFF)',
    border: '1px solid var(--v4-border, rgba(0, 0, 0, 0.08))',
    borderRadius: 'var(--v4-radius-lg, 8px)',
    padding: '40px 32px',
    textAlign: 'center' as const,
    boxShadow: 'var(--v4-shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1))',
  },
  iconContainer: {
    marginBottom: '24px',
  },
  icon: {
    color: '#c2410c', // v4-accent (terracotta)
  },
  title: {
    fontSize: '24px',
    fontWeight: 600,
    color: 'var(--v4-text, #171717)',
    margin: '0 0 12px 0',
    letterSpacing: '-0.02em',
  },
  description: {
    fontSize: '15px',
    lineHeight: 1.6,
    color: 'var(--v4-text-secondary, #525252)',
    margin: '0 0 8px 0',
  },
  context: {
    fontSize: '13px',
    color: 'var(--v4-text-muted, #a3a3a3)',
    margin: '0 0 24px 0',
  },
  actions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    marginBottom: '24px',
  },
  primaryButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 24px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#FFFFFF',
    background: '#c2410c', // v4-accent
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background 0.15s ease',
  },
  secondaryButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 24px',
    fontSize: '14px',
    fontWeight: 500,
    color: 'var(--v4-text-secondary, #525252)',
    background: 'transparent',
    border: '1px solid rgba(0, 0, 0, 0.08)',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.15s ease',
  },
  detailsToggle: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '8px 16px',
    fontSize: '13px',
    color: 'var(--v4-text-muted, #a3a3a3)',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    marginBottom: '16px',
  },
  detailsContainer: {
    textAlign: 'left' as const,
    padding: '16px',
    background: 'var(--v4-bg, #FAFAF9)',
    borderRadius: '6px',
    maxHeight: '300px',
    overflow: 'auto',
  },
  detailsSection: {
    marginBottom: '12px',
  },
  detailsLabel: {
    display: 'block',
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--v4-text-secondary, #525252)',
    marginBottom: '4px',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
  },
  errorCode: {
    display: 'block',
    fontSize: '13px',
    color: '#dc2626', // v4-error
    fontFamily: 'Monaco, Menlo, monospace',
    wordBreak: 'break-all' as const,
  },
  stackTrace: {
    fontSize: '11px',
    lineHeight: 1.4,
    color: 'var(--v4-text-muted, #a3a3a3)',
    fontFamily: 'Monaco, Menlo, monospace',
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-all' as const,
    margin: 0,
    maxHeight: '150px',
    overflow: 'auto',
  },
};

export default ErrorBoundary;
