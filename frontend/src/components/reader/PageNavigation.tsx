/**
 * Page navigation controls for the book reader.
 */

import { ChevronLeft, ChevronRight, Maximize, Minimize } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface PageNavigationProps {
  currentPage: number;
  totalPages: number;
  onPrevious: () => void;
  onNext: () => void;
  onPageSelect: (page: number) => void;
  isFullscreen: boolean;
  onToggleFullscreen: () => void;
}

export function PageNavigation({
  currentPage,
  totalPages,
  onPrevious,
  onNext,
  onPageSelect,
  isFullscreen,
  onToggleFullscreen,
}: PageNavigationProps) {
  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  return (
    <div className="flex items-center justify-between gap-4 p-4 bg-background border-t">
      {/* Previous Button */}
      <Button
        variant="outline"
        size="lg"
        onClick={onPrevious}
        disabled={!canGoPrevious}
        className="gap-2"
        aria-label="Previous page"
      >
        <ChevronLeft className="h-5 w-5" aria-hidden="true" />
        <span className="hidden sm:inline">Previous</span>
      </Button>

      {/* Page Indicators */}
      <div className="flex items-center gap-2">
        {/* Page Dots */}
        <div className="hidden md:flex items-center gap-1">
          {Array.from({ length: Math.min(totalPages, 10) }, (_, i) => {
            const pageNum = i + 1;
            const isCurrent = pageNum === currentPage;

            // Show first 5, last 5, or current +/- 2
            const shouldShow =
              pageNum <= 5 ||
              pageNum > totalPages - 5 ||
              Math.abs(pageNum - currentPage) <= 2;

            if (!shouldShow && totalPages > 10) {
              // Show ellipsis
              if (pageNum === 6 && currentPage > 8) {
                return <span key={`ellipsis-${i}`} className="px-1">...</span>;
              }
              if (pageNum === totalPages - 5 && currentPage < totalPages - 7) {
                return <span key={`ellipsis-${i}`} className="px-1">...</span>;
              }
              return null;
            }

            return (
              <button
                key={pageNum}
                onClick={() => onPageSelect(pageNum)}
                className={cn(
                  'h-2 w-2 rounded-full transition-all',
                  isCurrent
                    ? 'bg-primary w-6'
                    : 'bg-muted-foreground/30 hover:bg-muted-foreground/50'
                )}
                aria-label={`Go to page ${pageNum}`}
                aria-current={isCurrent ? 'page' : undefined}
              />
            );
          })}
        </div>

        {/* Page Counter */}
        <div className="text-sm text-muted-foreground whitespace-nowrap">
          Page {currentPage} of {totalPages}
        </div>

        {/* Fullscreen Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleFullscreen}
          aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
        >
          {isFullscreen ? (
            <Minimize className="h-4 w-4" aria-hidden="true" />
          ) : (
            <Maximize className="h-4 w-4" aria-hidden="true" />
          )}
        </Button>

        {/* Keyboard shortcut hint - hidden on mobile */}
        <span className="hidden lg:inline text-xs text-muted-foreground">
          Use arrow keys
        </span>
      </div>

      {/* Next Button */}
      <Button
        variant="outline"
        size="lg"
        onClick={onNext}
        disabled={!canGoNext}
        className="gap-2"
        aria-label="Next page"
      >
        <span className="hidden sm:inline">Next</span>
        <ChevronRight className="h-5 w-5" aria-hidden="true" />
      </Button>
    </div>
  );
}
