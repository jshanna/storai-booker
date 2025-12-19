/**
 * Hook to announce route changes to screen readers.
 * Announces the new page title when navigation occurs.
 */

import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAnnouncer } from '@/lib/contexts/AnnouncerContext';

/** Map of route paths to human-readable page titles */
const routeTitles: Record<string, string> = {
  '/': 'Home',
  '/generate': 'Create New Story',
  '/library': 'Story Library',
  '/settings': 'Settings',
  '/login': 'Sign In',
  '/register': 'Sign Up',
  '/profile': 'Profile',
  '/auth/callback': 'Signing in',
};

/**
 * Get the page title for a given path.
 * Handles dynamic routes like /reader/:id
 */
function getPageTitle(pathname: string): string {
  // Check for exact match
  if (routeTitles[pathname]) {
    return routeTitles[pathname];
  }

  // Check for dynamic routes
  if (pathname.startsWith('/reader/')) {
    return 'Story Reader';
  }

  return 'Page';
}

/**
 * Hook that announces route changes to screen readers.
 * Should be used once in the app, typically in the main App component.
 */
export function useRouteAnnouncer() {
  const location = useLocation();
  const { announce } = useAnnouncer();

  useEffect(() => {
    const title = getPageTitle(location.pathname);
    announce(`Navigated to ${title}`);
  }, [location.pathname, announce]);
}
