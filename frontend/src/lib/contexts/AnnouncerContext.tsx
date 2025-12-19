/**
 * Global announcer context for app-wide screen reader announcements.
 * Provides aria-live regions for polite and assertive announcements.
 */

import { createContext, useContext, useRef, useCallback, ReactNode } from 'react';

type Politeness = 'polite' | 'assertive';

interface AnnouncerContextValue {
  /**
   * Announce a message to screen readers.
   * @param message - The message to announce
   * @param politeness - 'polite' (default) or 'assertive' for urgent messages
   */
  announce: (message: string, politeness?: Politeness) => void;
}

const AnnouncerContext = createContext<AnnouncerContextValue | null>(null);

interface AnnouncerProviderProps {
  children: ReactNode;
}

export function AnnouncerProvider({ children }: AnnouncerProviderProps) {
  const politeRef = useRef<HTMLDivElement>(null);
  const assertiveRef = useRef<HTMLDivElement>(null);

  const announce = useCallback((message: string, politeness: Politeness = 'polite') => {
    const ref = politeness === 'assertive' ? assertiveRef : politeRef;
    if (ref.current) {
      // Clear first to ensure the announcement triggers even if the message is the same
      ref.current.textContent = '';
      // Use setTimeout to ensure the DOM update triggers the announcement
      setTimeout(() => {
        if (ref.current) {
          ref.current.textContent = message;
        }
      }, 100);
    }
  }, []);

  return (
    <AnnouncerContext.Provider value={{ announce }}>
      {children}
      {/* Polite announcements - wait for current speech to finish */}
      <div
        ref={politeRef}
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />
      {/* Assertive announcements - interrupt current speech */}
      <div
        ref={assertiveRef}
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
      />
    </AnnouncerContext.Provider>
  );
}

/**
 * Hook to access the global announcer for screen reader announcements.
 * Must be used within an AnnouncerProvider.
 */
export function useAnnouncer() {
  const context = useContext(AnnouncerContext);
  if (!context) {
    throw new Error('useAnnouncer must be used within an AnnouncerProvider');
  }
  return context;
}
