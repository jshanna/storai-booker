/**
 * Header component with navigation and dark mode toggle.
 */

import { Link, useLocation } from 'react-router-dom';
import { BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DarkModeToggle } from './DarkModeToggle';

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'Generate', href: '/generate' },
  { name: 'Library', href: '/library' },
  { name: 'Settings', href: '/settings' },
];

export function Header() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        {/* Logo */}
        <Link to="/" className="flex items-center space-x-2 mr-4 sm:mr-8">
          <BookOpen className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
          <span className="font-bold text-lg sm:text-xl">StorAI Booker</span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center space-x-3 sm:space-x-6 flex-1">
          {navigation.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                'text-xs sm:text-sm font-medium transition-colors hover:text-primary whitespace-nowrap',
                location.pathname === item.href
                  ? 'text-foreground'
                  : 'text-foreground/60'
              )}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Dark mode toggle */}
        <DarkModeToggle />
      </div>
    </header>
  );
}
