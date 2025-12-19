/**
 * Main book reader component with page flipping and navigation.
 * Supports both storybook and comic formats.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { BookPage } from './BookPage';
import { ComicPageRenderer } from './ComicPageRenderer';
import { PageNavigation } from './PageNavigation';
import type { Story, Page } from '@/types/api';
import { cn } from '@/lib/utils';
import { useAnnouncer } from '@/lib/contexts/AnnouncerContext';

interface BookReaderProps {
  story: Story;
}

export function BookReader({ story }: BookReaderProps) {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [isFlipping, setIsFlipping] = useState(false);
  const [flipDirection, setFlipDirection] = useState<'forward' | 'backward'>('forward');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { announce } = useAnnouncer();

  // Get current page (cover or regular page)
  const pages = story.cover_image_url
    ? [
        {
          page_number: 0,
          text: null,
          illustration_url: story.cover_image_url,
          illustration_prompt: null,
          generation_attempts: 0,
          validated: true,
        },
        ...story.pages,
      ]
    : story.pages;

  const currentPage = pages[currentPageIndex];
  const totalPages = pages.length;

  // Page navigation functions
  const goToPage = useCallback(
    (pageIndex: number) => {
      if (pageIndex < 0 || pageIndex >= totalPages || pageIndex === currentPageIndex) {
        return;
      }

      setFlipDirection(pageIndex > currentPageIndex ? 'forward' : 'backward');
      setIsFlipping(true);

      // Delay page change for animation
      setTimeout(() => {
        setCurrentPageIndex(pageIndex);
        setIsFlipping(false);
        // Announce page change to screen readers
        const pageLabel = pageIndex === 0 && story.cover_image_url ? 'Cover' : `Page ${pageIndex + 1}`;
        announce(`${pageLabel} of ${totalPages}`);
      }, 300);
    },
    [currentPageIndex, totalPages, announce, story.cover_image_url]
  );

  const nextPage = useCallback(() => {
    if (currentPageIndex < totalPages - 1) {
      goToPage(currentPageIndex + 1);
    }
  }, [currentPageIndex, totalPages, goToPage]);

  const previousPage = useCallback(() => {
    if (currentPageIndex > 0) {
      goToPage(currentPageIndex - 1);
    }
  }, [currentPageIndex, goToPage]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        nextPage();
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        previousPage();
      } else if (e.key === 'Escape' && isFullscreen) {
        e.preventDefault();
        exitFullscreen();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [nextPage, previousPage, isFullscreen]);

  // Fullscreen functions
  const enterFullscreen = useCallback(() => {
    if (containerRef.current) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    }
  }, []);

  const exitFullscreen = useCallback(() => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (isFullscreen) {
      exitFullscreen();
    } else {
      enterFullscreen();
    }
  }, [isFullscreen, enterFullscreen, exitFullscreen]);

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Determine if this is a comic format
  const isComic = story.generation_inputs.format === 'comic';

  // Render the appropriate page component based on format
  const renderPage = (
    page: Page,
    story: Story,
    pageIndex: number,
    isFlipping: boolean,
    flipDirection: 'forward' | 'backward'
  ) => {
    const isCover = pageIndex === 0 && !!story.cover_image_url;

    // Cover page always uses BookPage (single image)
    if (isCover) {
      return (
        <BookPage
          page={page}
          isFlipping={isFlipping}
          flipDirection={flipDirection}
          isCover={true}
        />
      );
    }

    // Comic format with panels uses ComicPageRenderer
    if (isComic && page.panels && page.panels.length > 0) {
      return (
        <ComicPageRenderer
          page={page}
          isFlipping={isFlipping}
          flipDirection={flipDirection}
        />
      );
    }

    // Default to BookPage for storybook format or comics without panels
    return (
      <BookPage
        page={page}
        isFlipping={isFlipping}
        flipDirection={flipDirection}
        isCover={false}
      />
    );
  };

  return (
    <div
      ref={containerRef}
      role="region"
      aria-label={`Book reader: ${story.title}`}
      aria-keyshortcuts="ArrowLeft ArrowRight Escape"
      className={cn(
        'flex flex-col bg-muted/30',
        isFullscreen ? 'h-screen' : 'min-h-[600px] rounded-lg border'
      )}
    >
      {/* Story Header */}
      {!isFullscreen && (
        <div className="p-4 border-b bg-background">
          <h1 className="text-2xl font-bold">{story.title}</h1>
          <p className="text-sm text-muted-foreground">
            {story.generation_inputs.format === 'comic' ? 'Comic Book' : 'Storybook'}
            {' • '}
            Age {story.generation_inputs.audience_age}+
          </p>
        </div>
      )}

      {/* Page Display Area */}
      <div className="flex-1 flex items-center justify-center p-2 sm:p-4 md:p-8">
        <div className="w-full h-full max-w-6xl">
          {currentPage && (
            renderPage(currentPage, story, currentPageIndex, isFlipping, flipDirection)
          )}
        </div>
      </div>

      {/* Navigation Controls */}
      <PageNavigation
        currentPage={currentPageIndex + 1}
        totalPages={totalPages}
        onPrevious={previousPage}
        onNext={nextPage}
        onPageSelect={(pageNum) => goToPage(pageNum - 1)}
        isFullscreen={isFullscreen}
        onToggleFullscreen={toggleFullscreen}
      />
    </div>
  );
}
