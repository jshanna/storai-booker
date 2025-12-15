/**
 * Main layout component wrapping all pages.
 */

import { ReactNode } from 'react';
import { Header } from './Header';
import { Toaster } from '@/components/ui/toaster';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-6">
        {children}
      </main>
      <Toaster />
    </div>
  );
}
