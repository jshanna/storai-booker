/**
 * Speech bubble overlay for comic panels.
 */

import type { DialoguePosition, DialogueStyle } from '@/types/api';

interface SpeechBubbleProps {
  character: string;
  text: string;
  position: DialoguePosition;
  style: DialogueStyle;
}

/**
 * Get CSS position classes based on bubble position.
 */
function getPositionClasses(position: DialoguePosition): string {
  const positionMap: Record<DialoguePosition, string> = {
    'top-left': 'top-2 left-2',
    'top-center': 'top-2 left-1/2 -translate-x-1/2',
    'top-right': 'top-2 right-2',
    'middle-left': 'top-1/2 left-2 -translate-y-1/2',
    'middle-right': 'top-1/2 right-2 -translate-y-1/2',
    'bottom-left': 'bottom-8 left-2',
    'bottom-center': 'bottom-8 left-1/2 -translate-x-1/2',
    'bottom-right': 'bottom-8 right-2',
  };
  return positionMap[position] || 'top-2 left-2';
}

/**
 * Get bubble style classes based on style type.
 */
function getBubbleStyles(style: DialogueStyle): {
  container: string;
  tail: string;
} {
  switch (style) {
    case 'thought':
      // Cloud-like thought bubble
      return {
        container: 'bg-white border-2 border-gray-300 rounded-full px-3 py-2',
        tail: 'thought-tail',
      };
    case 'shout':
      // Jagged/spiky bubble for shouting
      return {
        container: 'bg-yellow-100 border-2 border-yellow-500 rounded-lg px-3 py-2 font-bold',
        tail: 'shout-tail',
      };
    case 'whisper':
      // Dashed border for whispers
      return {
        container: 'bg-white/90 border-2 border-dashed border-gray-400 rounded-lg px-3 py-2 italic text-gray-600',
        tail: 'whisper-tail',
      };
    case 'speech':
    default:
      // Standard speech bubble
      return {
        container: 'bg-white border-2 border-gray-800 rounded-2xl px-3 py-2',
        tail: 'speech-tail',
      };
  }
}

/**
 * Get tail direction based on position.
 */
function getTailDirection(position: DialoguePosition): 'down' | 'up' | 'left' | 'right' {
  if (position.startsWith('top')) return 'down';
  if (position.startsWith('bottom')) return 'up';
  if (position.endsWith('left')) return 'right';
  return 'left';
}

export function SpeechBubble({ character, text, position, style }: SpeechBubbleProps) {
  const positionClasses = getPositionClasses(position);
  const { container: bubbleClasses } = getBubbleStyles(style);
  const tailDirection = getTailDirection(position);

  return (
    <div
      className={`absolute ${positionClasses} max-w-[70%] z-10`}
    >
      <div className={`relative ${bubbleClasses} shadow-md`}>
        {/* Character name (optional, small text) */}
        {character && style !== 'thought' && (
          <div className="text-[10px] text-gray-500 font-semibold mb-0.5 uppercase tracking-wide">
            {character}
          </div>
        )}

        {/* Dialogue text */}
        <p className="text-xs sm:text-sm leading-tight text-gray-900">
          {text}
        </p>

        {/* Tail/pointer - using CSS triangles */}
        {style === 'speech' && (
          <div
            className={`absolute ${
              tailDirection === 'down'
                ? '-bottom-2 left-4 w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[8px] border-t-white'
                : tailDirection === 'up'
                ? '-top-2 left-4 w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-b-[8px] border-b-white'
                : tailDirection === 'left'
                ? 'top-4 -left-2 w-0 h-0 border-t-[8px] border-t-transparent border-b-[8px] border-b-transparent border-r-[8px] border-r-white'
                : 'top-4 -right-2 w-0 h-0 border-t-[8px] border-t-transparent border-b-[8px] border-b-transparent border-l-[8px] border-l-white'
            }`}
          />
        )}

        {/* Outer tail border */}
        {style === 'speech' && (
          <div
            className={`absolute ${
              tailDirection === 'down'
                ? '-bottom-3 left-4 w-0 h-0 border-l-[9px] border-l-transparent border-r-[9px] border-r-transparent border-t-[9px] border-t-gray-800'
                : tailDirection === 'up'
                ? '-top-3 left-4 w-0 h-0 border-l-[9px] border-l-transparent border-r-[9px] border-r-transparent border-b-[9px] border-b-gray-800'
                : tailDirection === 'left'
                ? 'top-4 -left-3 w-0 h-0 border-t-[9px] border-t-transparent border-b-[9px] border-b-transparent border-r-[9px] border-r-gray-800'
                : 'top-4 -right-3 w-0 h-0 border-t-[9px] border-t-transparent border-b-[9px] border-b-transparent border-l-[9px] border-l-gray-800'
            } -z-10`}
          />
        )}

        {/* Thought bubble circles */}
        {style === 'thought' && tailDirection === 'down' && (
          <>
            <div className="absolute -bottom-2 left-4 w-2 h-2 bg-white border border-gray-300 rounded-full" />
            <div className="absolute -bottom-4 left-2 w-1.5 h-1.5 bg-white border border-gray-300 rounded-full" />
          </>
        )}
      </div>
    </div>
  );
}
