/**
 * Library page - story list with filters and pagination.
 */

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { StoryFilters, StoryGrid, DeleteStoryDialog } from '@/components/story';
import { Pagination } from '@/components/shared';
import { useStories, useDeleteStory, usePagination, useDebounce } from '@/lib/hooks';
import type { StoryFormat, StoryStatus } from '@/types/api';

type SharedFilter = 'all' | 'shared' | 'not_shared';

export function LibraryPage() {
  const { t } = useTranslation();

  // Filters state
  const [search, setSearch] = useState('');
  const [format, setFormat] = useState<StoryFormat | 'all'>('all');
  const [status, setStatus] = useState<StoryStatus | 'all'>('all');
  const [shared, setShared] = useState<SharedFilter>('all');

  // Pagination
  const { page, limit, skip, setPage, getTotalPages } = usePagination({
    initialLimit: 12,
  });

  // Debounce search input
  const debouncedSearch = useDebounce(search, 500);

  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [storyToDelete, setStoryToDelete] = useState<{ id: string; title: string } | null>(null);

  // Convert shared filter to boolean for API
  const sharedParam = shared === 'all' ? undefined : shared === 'shared';

  // Fetch stories
  const { data, isLoading, refetch } = useStories({
    skip,
    limit,
    search: debouncedSearch || undefined,
    format: format !== 'all' ? format : undefined,
    status: status !== 'all' ? status : undefined,
    shared: sharedParam,
  });

  // Delete mutation
  const { mutate: deleteStory } = useDeleteStory();

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, format, status, shared, setPage]);

  // Poll for generating stories every 5 seconds
  useEffect(() => {
    if (data?.stories.some(s => s.status === 'generating')) {
      const interval = setInterval(() => {
        refetch();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [data?.stories, refetch]);

  const handleDelete = (id: string) => {
    const story = data?.stories.find(s => s.id === id);
    if (story) {
      setStoryToDelete({ id, title: story.title });
      setDeleteDialogOpen(true);
    }
  };

  const confirmDelete = () => {
    if (storyToDelete) {
      deleteStory(storyToDelete.id, {
        onSuccess: () => {
          setDeleteDialogOpen(false);
          setStoryToDelete(null);
          refetch();
        },
      });
    }
  };

  const totalPages = data ? getTotalPages(data.total) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">{t('library.title')}</h1>
        <p className="text-muted-foreground">
          {t('library.subtitle')}
        </p>
      </div>

      {/* Filters */}
      <StoryFilters
        search={search}
        onSearchChange={setSearch}
        format={format}
        onFormatChange={setFormat}
        status={status}
        onStatusChange={setStatus}
        shared={shared}
        onSharedChange={setShared}
      />

      {/* Story Grid */}
      <StoryGrid
        stories={data?.stories || []}
        isLoading={isLoading}
        onDelete={handleDelete}
      />

      {/* Pagination */}
      {data && data.total > limit && (
        <Pagination
          currentPage={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}

      {/* Delete Confirmation Dialog */}
      {storyToDelete && (
        <DeleteStoryDialog
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          onConfirm={confirmDelete}
          storyTitle={storyToDelete.title}
        />
      )}
    </div>
  );
}
