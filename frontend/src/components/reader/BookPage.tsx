/**
 * Single book page component displaying illustration and text.
 */

import * as React from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { ImageOff } from 'lucide-react';
import type { Page } from '@/types/api';

interface BookPageProps {
  page: Page;
  isFlipping?: boolean;
  flipDirection?: 'forward' | 'backward';
}

export function BookPage({ page, isFlipping = false, flipDirection = 'forward' }: BookPageProps) {
  const [imageLoaded, setImageLoaded] = React.useState(false);
  const [imageError, setImageError] = React.useState(false);

  React.useEffect(() => {
    if (page.illustration_url) {
      setImageLoaded(false);
      setImageError(false);
    }
  }, [page.illustration_url]);

  return (
    <div
      className={`
        relative h-full w-full bg-background rounded-lg overflow-hidden shadow-2xl
        ${isFlipping ? (flipDirection === 'forward' ? 'animate-page-flip-forward' : 'animate-page-flip-backward') : ''}
      `}
    >
      <div className="h-full flex flex-col">
        {/* Illustration Area */}
        <div className="relative flex-1 bg-muted flex items-center justify-center overflow-hidden">
          {page.illustration_url ? (
            <>
              {!imageLoaded && !imageError && (
                <Skeleton className="absolute inset-0" />
              )}
              {imageError ? (
                <div className="flex flex-col items-center justify-center gap-2 text-muted-foreground">
                  <ImageOff className="h-16 w-16" />
                  <p className="text-sm">Image failed to load</p>
                </div>
              ) : (
                <img
                  src={page.illustration_url}
                  alt={`Page ${page.page_number}`}
                  className={`h-full w-full object-contain transition-opacity ${
                    imageLoaded ? 'opacity-100' : 'opacity-0'
                  }`}
                  onLoad={() => setImageLoaded(true)}
                  onError={() => setImageError(true)}
                />
              )}
            </>
          ) : (
            <div className="flex items-center justify-center text-muted-foreground">
              <ImageOff className="h-16 w-16" />
            </div>
          )}
        </div>

        {/* Text Area */}
        {page.text && (
          <div className="p-6 bg-background">
            <p className="text-lg leading-relaxed text-center">{page.text}</p>
          </div>
        )}

        {/* Page Number */}
        <div className="absolute bottom-4 right-4 px-3 py-1 bg-background/80 backdrop-blur rounded-full text-sm text-muted-foreground">
          {page.page_number}
        </div>
      </div>
    </div>
  );
}
