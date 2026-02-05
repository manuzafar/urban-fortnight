import { useState, useEffect, useCallback } from 'react';
import { AlertCircle, LogOut } from 'lucide-react';
import { useAuth } from './hooks/useAuth';
import { LandingPage } from './components/LandingPage';
import { DiscoveryForm } from './components/DiscoveryForm';
import { ProgressTracker } from './components/ProgressTracker';
import { InceptionPackViewer } from './components/InceptionPackViewer';
import {
  startDiscovery,
  getSessionStatus,
  pollSessionStatus,
  checkHealth,
  setAuthToken,
  ApiError,
} from './api/client';
import type { DiscoveryRequest, SessionStatusResponse, InceptionPack } from './types/api';
import './App.css';

type AppState = 'landing' | 'form' | 'progress' | 'result';

function App() {
  const { user, session, isLoading: authLoading, signInWithGoogle, signOut } = useAuth();
  const [appState, setAppState] = useState<AppState>('landing');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionData, setSessionData] = useState<SessionStatusResponse | null>(null);
  const [inceptionPack, setInceptionPack] = useState<InceptionPack | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  // Sync auth token to API client whenever session changes
  useEffect(() => {
    setAuthToken(session?.access_token ?? null);
  }, [session]);

  // Handle OAuth redirect: check if user was trying to go to form before login
  useEffect(() => {
    if (authLoading) return;
    if (!user) return;

    const pending = sessionStorage.getItem('seedcraft_pending_action');
    if (pending === 'form') {
      sessionStorage.removeItem('seedcraft_pending_action');
      setAppState('form');
    }
  }, [user, authLoading]);

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
      setSessionData(status);
      setAppState('progress');

      // Start polling
      const stopPolling = pollSessionStatus(response.session_id, (updatedStatus) => {
        setSessionData(updatedStatus);

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
        if (err.status === 401) {
          // Token expired or invalid — re-trigger login
          sessionStorage.setItem('seedcraft_pending_action', 'form');
          await signInWithGoogle();
          return;
        }
        setError(err.message);
      } else {
        setError('Failed to start discovery. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [signInWithGoogle]);

  const handleNewDiscovery = useCallback(() => {
    setAppState('landing');
    setSessionData(null);
    setInceptionPack(null);
    setError(null);
  }, []);

  const handleGoToForm = useCallback(() => {
    if (!user) {
      // Not logged in — store intent and trigger Google SSO
      sessionStorage.setItem('seedcraft_pending_action', 'form');
      signInWithGoogle();
      return;
    }
    setAppState('form');
  }, [user, signInWithGoogle]);

  const handleSignOut = useCallback(async () => {
    await signOut();
    handleNewDiscovery();
  }, [signOut, handleNewDiscovery]);

  return (
    <div className="app">
      {/* Header - only show on landing and form pages */}
      {(appState === 'landing' || appState === 'form') && (
        <header className="app-header">
          <div className="header-inner">
            <div className="brand" onClick={handleNewDiscovery} style={{ cursor: 'pointer' }}>
              <div className="logo"></div>
              <span>Seedcraft</span>
            </div>
            <nav className="nav">
              {isHealthy !== null && (
                <a href="#" className="nav-pill">
                  <span className={`status-dot ${isHealthy ? '' : 'unhealthy'}`}></span>
                  <span>{isHealthy ? 'System healthy' : 'System offline'}</span>
                </a>
              )}
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="nav-pill">
                Docs
              </a>
              <a href="https://github.com/manuzafar/urban-fortnight" target="_blank" rel="noopener noreferrer" className="nav-pill">
                GitHub
              </a>
              {user ? (
                <div className="user-menu">
                  {user.user_metadata?.avatar_url && (
                    <img
                      src={user.user_metadata.avatar_url}
                      alt=""
                      className="user-avatar"
                    />
                  )}
                  <span className="user-name">{user.user_metadata?.full_name || user.email}</span>
                  <button className="nav-pill sign-out-btn" onClick={handleSignOut} title="Sign out">
                    <LogOut size={14} />
                  </button>
                </div>
              ) : null}
              {appState === 'landing' && (
                <button className="btn-start" onClick={handleGoToForm}>
                  Start Discovery
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M6 12l4-4-4-4"/>
                  </svg>
                </button>
              )}
            </nav>
          </div>
        </header>
      )}

      {/* Main content area */}
      <main className="app-main">
        {error && (
          <div className="error-toast">
            <AlertCircle size={18} />
            <p>{error}</p>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {appState === 'landing' && (
          <LandingPage onStartDiscovery={handleGoToForm} />
        )}

        {appState === 'form' && (
          <DiscoveryForm onSubmit={handleStartDiscovery} isLoading={isLoading} onBack={handleNewDiscovery} />
        )}

        {appState === 'progress' && sessionData && (
          <ProgressTracker session={sessionData} onCancel={handleNewDiscovery} />
        )}

        {appState === 'result' && inceptionPack && (
          <InceptionPackViewer pack={inceptionPack} onNewDiscovery={handleNewDiscovery} />
        )}
      </main>

      {/* Footer - only show on landing page */}
      {appState === 'landing' && (
        <footer className="app-footer">
          <div className="footer-links">
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="footer-link">Documentation</a>
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="footer-link">API Reference</a>
            <a href="https://github.com/manuzafar/urban-fortnight" target="_blank" rel="noopener noreferrer" className="footer-link">GitHub</a>
            <a href="https://github.com/manuzafar/urban-fortnight/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener noreferrer" className="footer-link">Contributing</a>
          </div>
          <p className="footer-text">Made with ❤️ using Multi-Agent AI</p>
        </footer>
      )}
    </div>
  );
}

export default App;
