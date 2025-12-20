/**
 * Browse page - discover public stories from all users.
 */

import { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';
import { PublicStoryCard } from '@/components/story';
import { Pagination, FullPageSpinner } from '@/components/shared';
import { usePublicStories, usePagination } from '@/lib/hooks';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import type { StoryFormat } from '@/types/api';

export function BrowsePage() {
  // Filters state
  const [format, setFormat] = useState<StoryFormat | 'all'>('all');

  // Pagination
  const { page, setPage, getTotalPages } = usePagination({
    initialLimit: 12,
  });

  // Fetch public stories
  const { data, isLoading } = usePublicStories({
    page,
    page_size: 12,
    format: format !== 'all' ? format : undefined,
  });

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [format, setPage]);

  const totalPages = data ? getTotalPages(data.total) : 0;

  if (isLoading && !data) {
    return <FullPageSpinner text="Loading stories..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Globe className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Browse Stories</h1>
        </div>
        <p className="text-muted-foreground mt-1">
          Discover stories shared by the community
        </p>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-4">
        <div className="w-48">
          <Label htmlFor="format-filter">Format</Label>
          <Select
            value={format}
            onValueChange={(value) => setFormat(value as StoryFormat | 'all')}
          >
            <SelectTrigger id="format-filter">
              <SelectValue placeholder="All formats" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Formats</SelectItem>
              <SelectItem value="storybook">Storybook</SelectItem>
              <SelectItem value="comic">Comic</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {data && (
          <p className="text-sm text-muted-foreground self-end pb-2">
            {data.total} {data.total === 1 ? 'story' : 'stories'} found
          </p>
        )}
      </div>

      {/* Stories Grid */}
      {data && data.stories.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data.stories.map((story) => (
            <PublicStoryCard key={story.id} story={story} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Globe className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium">No stories yet</h3>
          <p className="text-muted-foreground">
            Be the first to share a story with the community!
          </p>
        </div>
      )}

      {/* Pagination */}
      {data && data.total > 12 && (
        <Pagination
          currentPage={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
