/**
 * Sound effect text overlay for comic panels.
 */

import type { SoundEffectPosition, SoundEffectStyle } from '@/types/api';

interface SoundEffectOverlayProps {
  text: string;
  position: SoundEffectPosition;
  style: SoundEffectStyle;
}

/**
 * Get CSS position classes based on effect position.
 */
function getPositionClasses(position: SoundEffectPosition): string {
  const positionMap: Record<SoundEffectPosition, string> = {
    'top-left': 'top-1 left-1',
    'top-center': 'top-1 left-1/2 -translate-x-1/2',
    'top-right': 'top-1 right-1',
    'middle-left': 'top-1/2 left-1 -translate-y-1/2',
    'middle-center': 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
    'middle-right': 'top-1/2 right-1 -translate-y-1/2',
    'bottom-left': 'bottom-1 left-1',
    'bottom-center': 'bottom-1 left-1/2 -translate-x-1/2',
    'bottom-right': 'bottom-1 right-1',
  };
  return positionMap[position] || 'top-right';
}

/**
 * Get style classes based on sound effect type.
 */
function getStyleClasses(style: SoundEffectStyle): string {
  switch (style) {
    case 'impact':
      // Bold, impactful text with red/orange tones
      return 'text-red-600 font-black text-xl sm:text-2xl drop-shadow-[2px_2px_0px_rgba(0,0,0,0.8)] -rotate-6';
    case 'whoosh':
      // Italicized, flowing text with blue tones
      return 'text-blue-500 font-bold italic text-lg sm:text-xl drop-shadow-[1px_1px_0px_rgba(0,0,0,0.6)] skew-x-[-6deg]';
    case 'ambient':
      // Softer, smaller text with gray tones
      return 'text-gray-600 font-semibold text-sm sm:text-base drop-shadow-[1px_1px_0px_rgba(255,255,255,0.8)]';
    case 'dramatic':
      // Large, dramatic text with purple/dark tones
      return 'text-purple-700 font-black text-2xl sm:text-3xl drop-shadow-[3px_3px_0px_rgba(0,0,0,0.9)] rotate-3';
    default:
      return 'text-orange-500 font-bold text-lg drop-shadow-[1px_1px_0px_rgba(0,0,0,0.7)]';
  }
}

/**
 * Format sound effect text for comic-style display.
 */
function formatText(text: string): string {
  // Ensure text is uppercase for comic effect
  return text.toUpperCase();
}

export function SoundEffectOverlay({ text, position, style }: SoundEffectOverlayProps) {
  const positionClasses = getPositionClasses(position);
  const styleClasses = getStyleClasses(style);

  return (
    <div
      className={`
        absolute ${positionClasses} z-20 pointer-events-none
        select-none comic-sfx
      `}
    >
      <span
        className={`
          ${styleClasses}
          tracking-tight
          leading-none
          whitespace-nowrap
        `}
        style={{
          // Comic-style text stroke effect
          WebkitTextStroke: style === 'impact' || style === 'dramatic' ? '1px black' : undefined,
          paintOrder: 'stroke fill',
        }}
      >
        {formatText(text)}
      </span>
    </div>
  );
}
