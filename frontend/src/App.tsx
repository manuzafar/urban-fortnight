import { useState, useEffect, useCallback } from 'react';
import { Github, AlertCircle } from 'lucide-react';
import { DiscoveryForm } from './components/DiscoveryForm';
import { ProgressTracker } from './components/ProgressTracker';
import { InceptionPackViewer } from './components/InceptionPackViewer';
import {
  startDiscovery,
  getSessionStatus,
  pollSessionStatus,
  checkHealth,
  ApiError,
} from './api/client';
import type { DiscoveryRequest, SessionStatusResponse, InceptionPack } from './types/api';
import './App.css';

type AppState = 'form' | 'progress' | 'result';

// Custom Logo Component - Unique Product Discovery Icon
function ProductDiscoveryLogo({ size = 32 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="product-logo"
    >
      {/* Outer ring - represents discovery/exploration */}
      <circle cx="24" cy="24" r="22" stroke="url(#logoGradient)" strokeWidth="2.5" strokeDasharray="4 2" />

      {/* Inner hexagon - represents product structure */}
      <path
        d="M24 6L38.5 15V33L24 42L9.5 33V15L24 6Z"
        fill="url(#hexGradient)"
        stroke="url(#logoGradient)"
        strokeWidth="1.5"
      />

      {/* Lightbulb/idea element in center */}
      <path
        d="M24 14C20 14 17 17 17 21C17 24 19 26 20 27.5V30C20 31 21 32 22 32H26C27 32 28 31 28 30V27.5C29 26 31 24 31 21C31 17 28 14 24 14Z"
        fill="white"
        fillOpacity="0.9"
      />
      <rect x="21" y="33" width="6" height="2" rx="1" fill="white" fillOpacity="0.7" />

      {/* Spark elements */}
      <circle cx="24" cy="20" r="2" fill="url(#sparkGradient)" />
      <path d="M36 10L38 8M10 38L12 36M38 38L36 36M10 10L12 12" stroke="url(#logoGradient)" strokeWidth="1.5" strokeLinecap="round" />

      <defs>
        <linearGradient id="logoGradient" x1="0" y1="0" x2="48" y2="48">
          <stop offset="0%" stopColor="#818cf8" />
          <stop offset="100%" stopColor="#6366f1" />
        </linearGradient>
        <linearGradient id="hexGradient" x1="9.5" y1="6" x2="38.5" y2="42">
          <stop offset="0%" stopColor="#6366f1" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#4f46e5" stopOpacity="0.5" />
        </linearGradient>
        <radialGradient id="sparkGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#fbbf24" />
          <stop offset="100%" stopColor="#f59e0b" />
        </radialGradient>
      </defs>
    </svg>
  );
}

function App() {
  const [appState, setAppState] = useState<AppState>('form');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [session, setSession] = useState<SessionStatusResponse | null>(null);
  const [inceptionPack, setInceptionPack] = useState<InceptionPack | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  const handleStartDiscovery = useCallback(async (request: DiscoveryRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await startDiscovery(request);

      // Get initial status
      const status = await getSessionStatus(response.session_id);
      setSession(status);
      setAppState('progress');

      // Start polling
      const stopPolling = pollSessionStatus(response.session_id, (updatedStatus) => {
        setSession(updatedStatus);

        if (updatedStatus.status === 'completed' && updatedStatus.inception_pack) {
          setInceptionPack(updatedStatus.inception_pack as InceptionPack);
          setAppState('result');
        } else if (updatedStatus.status === 'failed') {
          setError(updatedStatus.error_message || 'Discovery failed');
        }
      });

      // Cleanup polling on unmount
      return () => stopPolling();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to start discovery. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleNewDiscovery = useCallback(() => {
    setAppState('form');
    setSession(null);
    setInceptionPack(null);
    setError(null);
  }, []);

  return (
    <div className="app">
      {/* Minimal top bar */}
      <header className="app-topbar">
        <div className="topbar-left">
          <ProductDiscoveryLogo size={28} />
          <span className="app-name">Inception</span>
        </div>
        <div className="topbar-right">
          {isHealthy !== null && (
            <span className={`health-dot ${isHealthy ? 'healthy' : 'unhealthy'}`} title={isHealthy ? 'API Connected' : 'API Offline'} />
          )}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="topbar-link"
          >
            API
          </a>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="topbar-link"
          >
            <Github size={18} />
          </a>
        </div>
      </header>

      {/* Main centered content area */}
      <main className="app-centered-main">
        {error && (
          <div className="error-toast">
            <AlertCircle size={18} />
            <p>{error}</p>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {appState === 'form' && (
          <div className="centered-form-container">
            <div className="welcome-section">
              <ProductDiscoveryLogo size={64} />
              <h1>What would you like to build?</h1>
              <p>Describe your product idea and I'll generate a complete inception pack with customer research, business strategy, PRD, and technical architecture.</p>
            </div>
            <DiscoveryForm onSubmit={handleStartDiscovery} isLoading={isLoading} />
          </div>
        )}

        {appState === 'progress' && session && (
          <div className="centered-progress-container">
            <ProgressTracker session={session} onCancel={handleNewDiscovery} />
          </div>
        )}

        {appState === 'result' && inceptionPack && (
          <div className="result-container">
            <InceptionPackViewer pack={inceptionPack} onNewDiscovery={handleNewDiscovery} />
          </div>
        )}
      </main>

      {/* Minimal footer */}
      <footer className="app-minimal-footer">
        <span>Powered by Multi-Agent AI</span>
      </footer>
    </div>
  );
}

export default App;
