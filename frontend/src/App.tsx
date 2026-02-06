import { useState, useEffect, useCallback } from 'react';
import { AlertCircle, LogOut, History } from 'lucide-react';
import { useAuth } from './hooks/useAuth';
import { LandingPage } from './components/LandingPage';
import { DiscoveryForm } from './components/DiscoveryForm';
import { ProgressTracker } from './components/ProgressTracker';
import { SlideViewer } from './components/SlideViewer';
import { SessionHistory } from './components/SessionHistory';
import { Dashboard } from './components/Dashboard';
import { ExecutionView } from './components/ExecutionView';
import { PackViewer } from './components/PackViewer';
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

// Extended app state with new views
type AppState = 'landing' | 'form' | 'progress' | 'result' | 'sessions' | 'dashboard' | 'execution' | 'pack';

function App() {
  const { user, session, isLoading: authLoading, signInWithGoogle, signOut } = useAuth();
  const [appState, setAppState] = useState<AppState>('landing');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionData, setSessionData] = useState<SessionStatusResponse | null>(null);
  const [inceptionPack, setInceptionPack] = useState<InceptionPack | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  // Sync auth token to API client whenever session changes
  useEffect(() => {
    setAuthToken(session?.access_token ?? null);
  }, [session]);

  // Handle OAuth redirect: check if user was trying to go to form/dashboard before login
  useEffect(() => {
    if (authLoading) return;
    if (!user) return;

    const pending = sessionStorage.getItem('seedcraft_pending_action');
    if (pending === 'form') {
      sessionStorage.removeItem('seedcraft_pending_action');
      setAppState('form');
    } else if (pending === 'dashboard') {
      sessionStorage.removeItem('seedcraft_pending_action');
      setAppState('dashboard');
    }
  }, [user, authLoading]);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  // Handle starting discovery (used by both DiscoveryForm and Dashboard)
  const handleStartDiscovery = useCallback(async (request: DiscoveryRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await startDiscovery(request);
      setCurrentSessionId(response.session_id);

      // Get initial status
      const status = await getSessionStatus(response.session_id);
      setSessionData(status);

      // Switch to execution view for SSE streaming
      setAppState('execution');

    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          // Token expired or invalid — re-trigger login
          sessionStorage.setItem('seedcraft_pending_action', 'dashboard');
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

  // Legacy start discovery with polling (for old DiscoveryForm)
  const handleStartDiscoveryLegacy = useCallback(async (request: DiscoveryRequest) => {
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
          setCurrentSessionId(response.session_id);
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
    setCurrentSessionId(null);
    setError(null);
  }, []);

  const handleGoToDashboard = useCallback(() => {
    if (!user) {
      // Not logged in — store intent and trigger Google SSO
      sessionStorage.setItem('seedcraft_pending_action', 'dashboard');
      signInWithGoogle();
      return;
    }
    setAppState('dashboard');
  }, [user, signInWithGoogle]);

  const handleViewSessionPack = useCallback((pack: InceptionPack, sessionId?: string) => {
    setInceptionPack(pack);
    setCurrentSessionId(sessionId || pack.metadata?.session_id || null);
    setAppState('pack');
  }, []);

  // Legacy pack viewer
  const handleViewSessionPackLegacy = useCallback((pack: InceptionPack) => {
    setInceptionPack(pack);
    setCurrentSessionId(pack.metadata?.session_id || null);
    setAppState('result');
  }, []);

  const handleExecutionComplete = useCallback((pack: InceptionPack) => {
    setInceptionPack(pack);
    setAppState('pack');
  }, []);

  const handleBackToDashboard = useCallback(() => {
    setAppState('dashboard');
  }, []);

  const handleSignOut = useCallback(async () => {
    await signOut();
    handleNewDiscovery();
  }, [signOut, handleNewDiscovery]);

  // Determine if we should show header
  const showHeader = ['landing', 'form', 'sessions', 'dashboard'].includes(appState);

  // Determine if we should show footer
  const showFooter = appState === 'landing';

  return (
    <div className="app">
      {/* Header - show on landing, form, sessions, and dashboard pages */}
      {showHeader && (
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
                <>
                  <button className="nav-pill" onClick={handleGoToDashboard}>
                    <History size={14} />
                    <span>Dashboard</span>
                  </button>
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
                </>
              ) : null}
              {appState === 'landing' && (
                <button className="btn-start" onClick={handleGoToDashboard}>
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
          <LandingPage onStartDiscovery={handleGoToDashboard} />
        )}

        {appState === 'dashboard' && (
          <Dashboard
            onStartDiscovery={handleStartDiscovery}
            onViewPack={handleViewSessionPack}
            isLoading={isLoading}
          />
        )}

        {appState === 'form' && (
          <DiscoveryForm onSubmit={handleStartDiscoveryLegacy} isLoading={isLoading} onBack={handleNewDiscovery} />
        )}

        {appState === 'progress' && sessionData && (
          <ProgressTracker session={sessionData} onCancel={handleNewDiscovery} />
        )}

        {appState === 'execution' && currentSessionId && session?.access_token && (
          <ExecutionView
            sessionId={currentSessionId}
            authToken={session.access_token}
            onComplete={handleExecutionComplete}
            onBack={handleBackToDashboard}
          />
        )}

        {appState === 'sessions' && (
          <SessionHistory onBack={handleNewDiscovery} onViewPack={handleViewSessionPackLegacy} />
        )}

        {appState === 'result' && inceptionPack && (
          <SlideViewer pack={inceptionPack} onNewDiscovery={handleNewDiscovery} />
        )}

        {appState === 'pack' && inceptionPack && currentSessionId && (
          <PackViewer
            pack={inceptionPack}
            sessionId={currentSessionId}
            onBack={handleBackToDashboard}
          />
        )}
      </main>

      {/* Footer - only show on landing page */}
      {showFooter && (
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
