/**
 * Story grid component with view toggle.
 */

import { Grid3x3, List, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { StoryCard } from './StoryCard';
import { LoadingSpinner, EmptyState } from '@/components/shared';
import type { Story } from '@/types/api';
import { useUIStore } from '@/lib/stores/uiStore';
import { cn } from '@/lib/utils';

interface StoryGridProps {
  stories: Story[];
  isLoading: boolean;
  onDelete: (id: string) => void;
}

export function StoryGrid({ stories, isLoading, onDelete }: StoryGridProps) {
  const { libraryView, setLibraryView } = useUIStore();

  if (isLoading) {
    return <LoadingSpinner size="lg" text="Loading stories..." className="py-12" />;
  }

  if (stories.length === 0) {
    return (
      <EmptyState
        icon={BookOpen}
        title="No stories found"
        description="Start creating your first story to see it here."
        action={{
          label: 'Create Story',
          onClick: () => window.location.href = '/generate',
        }}
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* View Toggle */}
      <div className="flex justify-end">
        <div className="flex gap-1 border rounded-lg p-1">
          <Button
            variant={libraryView === 'grid' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setLibraryView('grid')}
            className="h-8 w-8 p-0"
          >
            <Grid3x3 className="h-4 w-4" />
            <span className="sr-only">Grid view</span>
          </Button>
          <Button
            variant={libraryView === 'list' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setLibraryView('list')}
            className="h-8 w-8 p-0"
          >
            <List className="h-4 w-4" />
            <span className="sr-only">List view</span>
          </Button>
        </div>
      </div>

      {/* Story Grid/List */}
      <div
        className={cn(
          libraryView === 'grid'
            ? 'grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
            : 'grid gap-4 grid-cols-1'
        )}
      >
        {stories.map((story) => (
          <StoryCard key={story.id} story={story} onDelete={onDelete} />
        ))}
      </div>
    </div>
  );
}
