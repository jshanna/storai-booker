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
  isCover?: boolean;
}

export function BookPage({ page, isFlipping = false, flipDirection = 'forward', isCover = false }: BookPageProps) {
  const [imageLoaded, setImageLoaded] = React.useState(false);
  const [imageError, setImageError] = React.useState(false);

  React.useEffect(() => {
    if (page.illustration_url) {
      setImageLoaded(false);
      setImageError(false);
    }
  }, [page.illustration_url]);

  // Determine aspect ratio class based on page type
  const aspectRatioClass = isCover ? 'aspect-[3/4]' : 'aspect-[16/9]';

  return (
    <div
      className={`
        relative w-full h-full bg-background rounded-lg overflow-hidden shadow-2xl flex items-center justify-center
        ${isFlipping ? (flipDirection === 'forward' ? 'animate-page-flip-forward' : 'animate-page-flip-backward') : ''}
      `}
    >
      <div className="w-full h-full flex flex-col max-h-full">
        {/* Illustration Area */}
        <div className="relative flex-shrink-0 bg-muted flex items-center justify-center">
          <div className={`w-full ${aspectRatioClass} max-h-[70vh] sm:max-h-[75vh] md:max-h-[80vh]`}>
            {page.illustration_url ? (
              <>
                {!imageLoaded && !imageError && (
                  <Skeleton className="absolute inset-0" />
                )}
                {imageError ? (
                  <div className="flex flex-col items-center justify-center gap-2 text-muted-foreground h-full">
                    <ImageOff className="h-12 w-12 sm:h-16 sm:w-16" />
                    <p className="text-xs sm:text-sm">Image failed to load</p>
                  </div>
                ) : (
                  <img
                    src={page.illustration_url}
                    alt={`Page ${page.page_number}`}
                    className={`w-full h-full object-contain transition-opacity ${
                      imageLoaded ? 'opacity-100' : 'opacity-0'
                    }`}
                    onLoad={() => setImageLoaded(true)}
                    onError={() => setImageError(true)}
                  />
                )}
              </>
            ) : (
              <div className="flex items-center justify-center text-muted-foreground h-full">
                <ImageOff className="h-12 w-12 sm:h-16 sm:w-16" />
              </div>
            )}
          </div>
        </div>

        {/* Text Area */}
        {page.text && (
          <div className="p-3 sm:p-4 md:p-6 bg-background overflow-y-auto">
            <p className="text-sm sm:text-base md:text-lg leading-relaxed text-center">
              {page.text}
            </p>
          </div>
        )}

        {/* Page Number */}
        {page.page_number > 0 && (
          <div className="absolute bottom-2 right-2 sm:bottom-4 sm:right-4 px-2 py-1 sm:px-3 bg-background/80 backdrop-blur rounded-full text-xs sm:text-sm text-muted-foreground">
            {page.page_number}
          </div>
        )}
      </div>
    </div>
  );
}
