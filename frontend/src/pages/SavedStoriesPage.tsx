/**
 * Saved Stories page - user's bookmarked stories.
 */

import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Bookmark } from 'lucide-react';
import { PublicStoryCard } from '@/components/story';
import { Pagination, FullPageSpinner } from '@/components/shared';
import { useBookmarks, usePagination } from '@/lib/hooks';

export function SavedStoriesPage() {
  const { t } = useTranslation();
  // Pagination
  const { page, setPage, getTotalPages } = usePagination({
    initialLimit: 12,
  });

  // Fetch bookmarks
  const { data, isLoading } = useBookmarks({
    page,
    page_size: 12,
  });

  // Reset page when data changes (e.g., after removing a bookmark)
  useEffect(() => {
    if (data && data.bookmarks.length === 0 && page > 1) {
      setPage(page - 1);
    }
  }, [data, page, setPage]);

  const totalPages = data ? getTotalPages(data.total) : 0;

  if (isLoading && !data) {
    return <FullPageSpinner text={t('common.loading')} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Bookmark className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">{t('saved.title')}</h1>
        </div>
        <p className="text-muted-foreground mt-1">
          {t('saved.subtitle')}
        </p>
      </div>

      {/* Info */}
      {data && data.total > 0 && (
        <p className="text-sm text-muted-foreground">
          {t('library.pagination.showing', { start: 1, end: data.bookmarks.length, total: data.total })}
        </p>
      )}

      {/* Stories Grid */}
      {data && data.bookmarks.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data.bookmarks.map((bookmark) => (
            <PublicStoryCard
              key={bookmark.id}
              story={bookmark}
              isSavedView
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Bookmark className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium">{t('saved.empty.title')}</h3>
          <p className="text-muted-foreground">
            {t('saved.empty.description')}
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
