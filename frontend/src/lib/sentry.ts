/**
 * Sentry error tracking configuration.
 */

import * as Sentry from '@sentry/react';

// Get Sentry DSN from environment variables
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
const SENTRY_ENVIRONMENT = import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development';
const APP_VERSION = import.meta.env.VITE_APP_VERSION || '0.1.0';

/**
 * Initialize Sentry error tracking.
 * Only initializes if VITE_SENTRY_DSN is set.
 */
export function initSentry() {
  if (!SENTRY_DSN) {
    console.log('Sentry DSN not configured, skipping initialization');
    return;
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: SENTRY_ENVIRONMENT,
    release: `storai-booker-frontend@${APP_VERSION}`,

    // Performance monitoring
    tracesSampleRate: SENTRY_ENVIRONMENT === 'production' ? 0.1 : 1.0,

    // Session replay for debugging (only in production, low sample rate)
    replaysSessionSampleRate: SENTRY_ENVIRONMENT === 'production' ? 0.1 : 0,
    replaysOnErrorSampleRate: SENTRY_ENVIRONMENT === 'production' ? 1.0 : 0,

    // Don't send PII
    sendDefaultPii: false,

    // Filter out known non-actionable errors
    beforeSend(event, hint) {
      const error = hint.originalException;

      // Filter out network errors that are expected
      if (error instanceof Error) {
        // Ignore canceled requests
        if (error.message.includes('canceled') || error.message.includes('aborted')) {
          return null;
        }
        // Ignore network errors (user offline, etc.)
        if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
          return null;
        }
      }

      return event;
    },

    // Integrations
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        // Mask all text and block all media for privacy
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
  });

  console.log(`Sentry initialized for environment: ${SENTRY_ENVIRONMENT}`);
}

/**
 * Capture an exception to Sentry with optional context.
 */
export function captureException(error: Error, context?: Record<string, unknown>) {
  if (!SENTRY_DSN) {
    console.error('Error (Sentry not configured):', error, context);
    return;
  }

  Sentry.withScope((scope) => {
    if (context) {
      scope.setExtras(context);
    }
    Sentry.captureException(error);
  });
}

/**
 * Capture a message to Sentry.
 */
export function captureMessage(message: string, level: Sentry.SeverityLevel = 'info') {
  if (!SENTRY_DSN) {
    console.log(`Message (Sentry not configured): ${message}`);
    return;
  }

  Sentry.captureMessage(message, level);
}

/**
 * Set user context for Sentry events.
 */
export function setUser(user: { id: string; email?: string; username?: string } | null) {
  Sentry.setUser(user);
}

/**
 * Add breadcrumb for debugging.
 */
export function addBreadcrumb(breadcrumb: Sentry.Breadcrumb) {
  Sentry.addBreadcrumb(breadcrumb);
}

// Export Sentry for direct access if needed
export { Sentry };
