/**
 * Skip link component for keyboard navigation.
 * Allows users to skip directly to main content, bypassing navigation.
 * Visible only when focused (for keyboard users).
 */

import { cn } from '@/lib/utils';

interface SkipLinkProps {
  /** The ID of the target element to skip to */
  targetId: string;
  /** Custom link text (defaults to "Skip to main content") */
  children?: React.ReactNode;
}

export function SkipLink({ targetId, children = 'Skip to main content' }: SkipLinkProps) {
  return (
    <a
      href={`#${targetId}`}
      className={cn(
        // Hidden by default, visible on focus
        'sr-only focus:not-sr-only',
        // Position at top-left when visible
        'focus:absolute focus:top-4 focus:left-4 focus:z-[100]',
        // Styled button appearance
        'focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground',
        'focus:rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        // Smooth transition
        'focus:shadow-lg'
      )}
    >
      {children}
    </a>
  );
}
