/**
 * Main layout component wrapping all pages.
 */

import { ReactNode } from 'react';
import { Header } from './Header';
import { SkipLink } from '@/components/shared/SkipLink';
import { Toaster } from '@/components/ui/toaster';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <SkipLink targetId="main-content" />
      <Header />
      <main id="main-content" className="container py-6" tabIndex={-1}>
        {children}
      </main>
      <Toaster />
    </div>
  );
}
