/**
 * Comic page renderer with support for both whole-page and per-panel images.
 * Note: Speech bubbles and sound effects are rendered directly in the generated images.
 */

import * as React from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { ImageOff } from 'lucide-react';
import type { Page, Panel } from '@/types/api';

interface ComicPageRendererProps {
  page: Page;
  isFlipping?: boolean;
  flipDirection?: 'forward' | 'backward';
}

/**
 * Renders a whole-page comic image (all panels in one image).
 * Used when page.illustration_url is set.
 */
function WholePageRenderer({
  page,
  isFlipping,
  flipDirection,
}: ComicPageRendererProps) {
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
        relative w-full h-full bg-background rounded-lg overflow-hidden shadow-2xl
        ${isFlipping ? (flipDirection === 'forward' ? 'animate-page-flip-forward' : 'animate-page-flip-backward') : ''}
      `}
    >
      {/* Whole Page Image */}
      <div className="w-full h-full">
        {!imageLoaded && !imageError && (
          <Skeleton className="absolute inset-0" />
        )}
        {imageError ? (
          <div className="flex flex-col items-center justify-center gap-2 text-muted-foreground h-full">
            <ImageOff className="h-8 w-8" />
            <p className="text-sm">Image failed to load</p>
          </div>
        ) : (
          <img
            src={page.illustration_url || undefined}
            alt={`Comic page ${page.page_number}`}
            className={`w-full h-full object-contain transition-opacity ${
              imageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
        )}
      </div>

      {/* Page Number */}
      <div className="absolute bottom-2 right-2 px-2 py-1 bg-background/80 backdrop-blur rounded-full text-xs text-muted-foreground">
        {page.page_number}
      </div>
    </div>
  );
}

/**
 * Get CSS grid template based on panel count.
 */
function getGridTemplate(panelCount: number): { columns: string; rows: string } {
  switch (panelCount) {
    case 1:
      return { columns: '1fr', rows: '1fr' };
    case 2:
      // Stacked vertically for better readability
      return { columns: '1fr', rows: '1fr 1fr' };
    case 3:
      // 1 on top, 2 on bottom (handled with grid areas)
      return { columns: '1fr 1fr', rows: '1fr 1fr' };
    case 4:
      return { columns: '1fr 1fr', rows: '1fr 1fr' };
    case 5:
      // 2 on top, 3 on bottom
      return { columns: '1fr 1fr 1fr', rows: '1fr 1fr' };
    case 6:
      return { columns: '1fr 1fr 1fr', rows: '1fr 1fr' };
    case 7:
      // 2-3-2 pattern
      return { columns: '1fr 1fr 1fr', rows: '1fr 1fr 1fr' };
    case 8:
      // 2-4-2 pattern
      return { columns: '1fr 1fr 1fr 1fr', rows: '1fr 1fr 1fr' };
    case 9:
      return { columns: '1fr 1fr 1fr', rows: '1fr 1fr 1fr' };
    default:
      return { columns: '1fr 1fr', rows: '1fr 1fr' };
  }
}

/**
 * Get grid area for special layouts (3 panels, 5 panels, etc.)
 */
function getGridArea(panelIndex: number, panelCount: number): string | undefined {
  if (panelCount === 3) {
    // First panel spans full width
    if (panelIndex === 0) return '1 / 1 / 2 / 3';
    // Second and third panels in bottom row
    if (panelIndex === 1) return '2 / 1 / 3 / 2';
    if (panelIndex === 2) return '2 / 2 / 3 / 3';
  }
  if (panelCount === 5) {
    // First two panels in top row (each takes 1.5 columns via span)
    if (panelIndex === 0) return '1 / 1 / 2 / 2';
    if (panelIndex === 1) return '1 / 2 / 2 / 4';
    // Bottom three panels
    if (panelIndex === 2) return '2 / 1 / 3 / 2';
    if (panelIndex === 3) return '2 / 2 / 3 / 3';
    if (panelIndex === 4) return '2 / 3 / 3 / 4';
  }
  return undefined;
}

interface PanelRendererProps {
  panel: Panel;
  pageNumber: number;
  gridArea?: string;
}

function PanelRenderer({ panel, pageNumber, gridArea }: PanelRendererProps) {
  const [imageLoaded, setImageLoaded] = React.useState(false);
  const [imageError, setImageError] = React.useState(false);

  React.useEffect(() => {
    if (panel.illustration_url) {
      setImageLoaded(false);
      setImageError(false);
    }
  }, [panel.illustration_url]);

  return (
    <div
      className="relative bg-muted border-2 border-foreground/20 overflow-hidden"
      style={gridArea ? { gridArea } : undefined}
    >
      {/* Panel Image - text elements are rendered in the image */}
      <div className="w-full h-full">
        {panel.illustration_url ? (
          <>
            {!imageLoaded && !imageError && (
              <Skeleton className="absolute inset-0" />
            )}
            {imageError ? (
              <div className="flex flex-col items-center justify-center gap-1 text-muted-foreground h-full">
                <ImageOff className="h-6 w-6" />
                <p className="text-xs">Image failed</p>
              </div>
            ) : (
              <img
                src={panel.illustration_url}
                alt={`Page ${pageNumber}, Panel ${panel.panel_number}`}
                className={`w-full h-full object-cover transition-opacity ${
                  imageLoaded ? 'opacity-100' : 'opacity-0'
                }`}
                onLoad={() => setImageLoaded(true)}
                onError={() => setImageError(true)}
              />
            )}
          </>
        ) : (
          <div className="flex items-center justify-center text-muted-foreground h-full bg-muted/50">
            <ImageOff className="h-6 w-6" />
          </div>
        )}
      </div>

      {/* Panel number (small indicator) */}
      <div className="absolute bottom-0.5 right-0.5 text-[10px] text-muted-foreground/50">
        {panel.panel_number}
      </div>
    </div>
  );
}

export function ComicPageRenderer({
  page,
  isFlipping = false,
  flipDirection = 'forward',
}: ComicPageRendererProps) {
  // Check if this is a whole-page image (new generation mode)
  // If page.illustration_url is set, render the whole page as a single image
  if (page.illustration_url) {
    return (
      <WholePageRenderer
        page={page}
        isFlipping={isFlipping}
        flipDirection={flipDirection}
      />
    );
  }

  // Fall back to per-panel grid rendering (legacy mode)
  const panels = page.panels || [];
  const panelCount = panels.length;

  if (panelCount === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center text-muted-foreground">
        <p>No panels available</p>
      </div>
    );
  }

  const { columns, rows } = getGridTemplate(panelCount);

  return (
    <div
      className={`
        relative w-full h-full bg-background rounded-lg overflow-hidden shadow-2xl
        ${isFlipping ? (flipDirection === 'forward' ? 'animate-page-flip-forward' : 'animate-page-flip-backward') : ''}
      `}
    >
      {/* Panel Grid */}
      <div
        className="w-full h-full p-2 gap-2"
        style={{
          display: 'grid',
          gridTemplateColumns: columns,
          gridTemplateRows: rows,
        }}
      >
        {panels.map((panel, idx) => (
          <PanelRenderer
            key={panel.panel_number}
            panel={panel}
            pageNumber={page.page_number}
            gridArea={getGridArea(idx, panelCount)}
          />
        ))}
      </div>

      {/* Page Number */}
      <div className="absolute bottom-2 right-2 px-2 py-1 bg-background/80 backdrop-blur rounded-full text-xs text-muted-foreground">
        {page.page_number}
      </div>
    </div>
  );
}
