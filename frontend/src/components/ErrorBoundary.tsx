/**
 * Error Boundary Component for Seedform
 * Catches render errors and displays user-friendly recovery UI
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary - catches JavaScript errors in child component tree
 * and displays a fallback UI instead of crashing the whole app.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('[ErrorBoundary] Caught error:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  handleGoHome = (): void => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div style={styles.container}>
          <div style={styles.card}>
            <AlertTriangle size={48} color="#c2410c" />
            <h1 style={styles.title}>Something went wrong</h1>
            <p style={styles.description}>
              We encountered an unexpected error. You can try again or return to the home page.
            </p>
            <div style={styles.actions}>
              <button onClick={this.handleRetry} style={styles.primaryButton}>
                <RefreshCw size={18} />
                Try Again
              </button>
              <button onClick={this.handleGoHome} style={styles.secondaryButton}>
                <Home size={18} />
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px',
    background: '#FAFAF9',
  },
  card: {
    maxWidth: '400px',
    width: '100%',
    background: '#FFFFFF',
    border: '1px solid rgba(0, 0, 0, 0.08)',
    borderRadius: '8px',
    padding: '40px 32px',
    textAlign: 'center' as const,
  },
  title: {
    fontSize: '20px',
    fontWeight: 600,
    color: '#171717',
    margin: '16px 0 8px 0',
  },
  description: {
    fontSize: '14px',
    color: '#525252',
    margin: '0 0 24px 0',
  },
  actions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
  },
  primaryButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#FFFFFF',
    background: '#c2410c',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  secondaryButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#525252',
    background: 'transparent',
    border: '1px solid rgba(0, 0, 0, 0.1)',
    borderRadius: '6px',
    cursor: 'pointer',
  },
};

export default ErrorBoundary;
