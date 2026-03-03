/**
 * Error Handling Utilities for Seedcraft
 * Provides error classification, formatting, and retry logic
 */

import { ApiError } from '../api/client';

// ============================================================================
// Error Types & Classification
// ============================================================================

export type ErrorCategory =
  | 'network'
  | 'authentication'
  | 'authorization'
  | 'validation'
  | 'server'
  | 'timeout'
  | 'unknown';

export interface ClassifiedError {
  category: ErrorCategory;
  message: string;
  userMessage: string;
  isRetryable: boolean;
  originalError: Error;
}

/**
 * Classifies an error into a category for appropriate handling
 */
export function classifyError(error: unknown): ClassifiedError {
  const errorObj = error instanceof Error ? error : new Error(String(error));

  // Network errors
  if (isNetworkError(error)) {
    return {
      category: 'network',
      message: errorObj.message,
      userMessage: isOffline()
        ? 'You appear to be offline. Please check your internet connection.'
        : 'Unable to connect to the server. Please try again.',
      isRetryable: true,
      originalError: errorObj,
    };
  }

  // API errors
  if (error instanceof ApiError) {
    return classifyApiError(error);
  }

  // Timeout errors
  if (isTimeoutError(error)) {
    return {
      category: 'timeout',
      message: errorObj.message,
      userMessage: 'The request took too long. Please try again.',
      isRetryable: true,
      originalError: errorObj,
    };
  }

  // Unknown errors
  return {
    category: 'unknown',
    message: errorObj.message,
    userMessage: 'An unexpected error occurred. Please try again.',
    isRetryable: true,
    originalError: errorObj,
  };
}

/**
 * Classifies API errors based on status code
 */
function classifyApiError(error: ApiError): ClassifiedError {
  const { status, message } = error;

  switch (status) {
    case 401:
      return {
        category: 'authentication',
        message,
        userMessage: 'Your session has expired. Please sign in again.',
        isRetryable: false,
        originalError: error,
      };

    case 403:
      return {
        category: 'authorization',
        message,
        userMessage: 'You do not have permission to perform this action.',
        isRetryable: false,
        originalError: error,
      };

    case 400:
    case 422:
      return {
        category: 'validation',
        message,
        userMessage: formatValidationMessage(message),
        isRetryable: false,
        originalError: error,
      };

    case 404:
      return {
        category: 'unknown',
        message,
        userMessage: 'The requested resource was not found.',
        isRetryable: false,
        originalError: error,
      };

    case 408:
    case 504:
      return {
        category: 'timeout',
        message,
        userMessage: 'The request timed out. Please try again.',
        isRetryable: true,
        originalError: error,
      };

    case 429:
      return {
        category: 'server',
        message,
        userMessage: 'Too many requests. Please wait a moment and try again.',
        isRetryable: true,
        originalError: error,
      };

    case 500:
    case 502:
    case 503:
      return {
        category: 'server',
        message,
        userMessage: 'The server encountered an error. Please try again later.',
        isRetryable: true,
        originalError: error,
      };

    default:
      return {
        category: 'unknown',
        message,
        userMessage: message || 'An error occurred. Please try again.',
        isRetryable: status >= 500,
        originalError: error,
      };
  }
}

/**
 * Format validation error messages for user display
 */
function formatValidationMessage(message: string): string {
  // Try to extract meaningful validation info
  if (message.toLowerCase().includes('required')) {
    return 'Please fill in all required fields.';
  }
  if (message.toLowerCase().includes('invalid')) {
    return 'Please check your input and try again.';
  }
  return message || 'Please check your input and try again.';
}

// ============================================================================
// Network Status Detection
// ============================================================================

/**
 * Check if the browser is offline
 */
export function isOffline(): boolean {
  return typeof navigator !== 'undefined' && !navigator.onLine;
}

/**
 * Check if an error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError) {
    const message = error.message.toLowerCase();
    return (
      message.includes('failed to fetch') ||
      message.includes('network request failed') ||
      message.includes('networkerror') ||
      message.includes('load failed')
    );
  }

  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    const name = error.name.toLowerCase();
    return (
      name === 'networkerror' ||
      message.includes('network') ||
      message.includes('connection')
    );
  }

  return false;
}

/**
 * Check if an error is a timeout error
 */
export function isTimeoutError(error: unknown): boolean {
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    const name = error.name.toLowerCase();
    return (
      name === 'timeouterror' ||
      name === 'aborterror' ||
      message.includes('timeout') ||
      message.includes('timed out') ||
      message.includes('aborted')
    );
  }
  return false;
}

/**
 * Listen for online/offline status changes
 */
export function onNetworkStatusChange(
  callback: (isOnline: boolean) => void
): () => void {
  const handleOnline = () => callback(true);
  const handleOffline = () => callback(false);

  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);

  // Return cleanup function
  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
}

// ============================================================================
// Retry Logic with Exponential Backoff
// ============================================================================

export interface RetryOptions {
  /** Maximum number of retry attempts (default: 3) */
  maxRetries?: number;
  /** Initial delay in ms before first retry (default: 1000) */
  initialDelay?: number;
  /** Maximum delay in ms between retries (default: 10000) */
  maxDelay?: number;
  /** Multiplier for exponential backoff (default: 2) */
  backoffMultiplier?: number;
  /** Add random jitter to delays (default: true) */
  jitter?: boolean;
  /** Function to determine if error is retryable (default: uses classifyError) */
  shouldRetry?: (error: unknown, attempt: number) => boolean;
  /** Callback called before each retry attempt */
  onRetry?: (error: unknown, attempt: number, delay: number) => void;
}

const DEFAULT_RETRY_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffMultiplier: 2,
  jitter: true,
  shouldRetry: (error) => classifyError(error).isRetryable,
  onRetry: () => {},
};

/**
 * Calculates delay for exponential backoff with optional jitter
 */
export function calculateBackoffDelay(
  attempt: number,
  options: Required<RetryOptions>
): number {
  const { initialDelay, maxDelay, backoffMultiplier, jitter } = options;

  // Calculate exponential delay
  let delay = initialDelay * Math.pow(backoffMultiplier, attempt - 1);

  // Apply jitter (random variance of +/- 25%)
  if (jitter) {
    const jitterFactor = 0.75 + Math.random() * 0.5;
    delay = delay * jitterFactor;
  }

  // Cap at max delay
  return Math.min(delay, maxDelay);
}

/**
 * Sleep for a specified duration
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Execute a function with retry logic and exponential backoff
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const opts = { ...DEFAULT_RETRY_OPTIONS, ...options };
  let lastError: unknown;

  for (let attempt = 1; attempt <= opts.maxRetries + 1; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if we should retry
      const isLastAttempt = attempt > opts.maxRetries;
      const shouldRetry = !isLastAttempt && opts.shouldRetry(error, attempt);

      if (!shouldRetry) {
        throw error;
      }

      // Calculate delay and wait
      const delay = calculateBackoffDelay(attempt, opts);
      opts.onRetry(error, attempt, delay);
      await sleep(delay);
    }
  }

  throw lastError;
}

// ============================================================================
// Error Message Formatting
// ============================================================================

/**
 * Format an error for user display
 */
export function formatErrorMessage(error: unknown): string {
  const classified = classifyError(error);
  return classified.userMessage;
}

/**
 * Format an error for logging (includes technical details)
 */
export function formatErrorForLogging(error: unknown): string {
  if (error instanceof ApiError) {
    return `ApiError [${error.status}] ${error.statusText}: ${error.message}`;
  }

  if (error instanceof Error) {
    return `${error.name}: ${error.message}${error.stack ? '\n' + error.stack : ''}`;
  }

  return String(error);
}

// ============================================================================
// SSE-Specific Error Handling
// ============================================================================

export interface SSERetryConfig {
  /** Maximum number of reconnection attempts (default: 5) */
  maxReconnects?: number;
  /** Initial delay before first reconnect in ms (default: 1000) */
  initialReconnectDelay?: number;
  /** Maximum delay between reconnects in ms (default: 30000) */
  maxReconnectDelay?: number;
  /** Callback when reconnection starts */
  onReconnecting?: (attempt: number, delay: number) => void;
  /** Callback when reconnection succeeds */
  onReconnected?: () => void;
  /** Callback when all reconnection attempts fail */
  onReconnectFailed?: (error: unknown) => void;
}

export const DEFAULT_SSE_RETRY_CONFIG: Required<SSERetryConfig> = {
  maxReconnects: 5,
  initialReconnectDelay: 1000,
  maxReconnectDelay: 30000,
  onReconnecting: () => {},
  onReconnected: () => {},
  onReconnectFailed: () => {},
};

/**
 * Calculate SSE reconnection delay with exponential backoff
 */
export function calculateSSEReconnectDelay(
  attempt: number,
  config: Required<SSERetryConfig>
): number {
  const { initialReconnectDelay, maxReconnectDelay } = config;
  const delay = initialReconnectDelay * Math.pow(2, attempt - 1);
  // Add some jitter
  const jitter = delay * (0.5 + Math.random());
  return Math.min(jitter, maxReconnectDelay);
}

/**
 * Get user-friendly SSE error message
 */
export function getSSEErrorMessage(
  error: unknown,
  reconnectAttempt?: number,
  maxReconnects?: number
): string {
  if (isOffline()) {
    return 'You are offline. Waiting for connection...';
  }

  if (isNetworkError(error)) {
    if (reconnectAttempt !== undefined && maxReconnects !== undefined) {
      return `Connection lost. Reconnecting (${reconnectAttempt}/${maxReconnects})...`;
    }
    return 'Connection lost. Attempting to reconnect...';
  }

  if (error instanceof Error) {
    if (error.message.includes('401') || error.message.includes('unauthorized')) {
      return 'Session expired. Please sign in again.';
    }
  }

  return 'Connection error. Attempting to reconnect...';
}
