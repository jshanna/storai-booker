/**
 * Public story card component for displaying a story in browse/saved views.
 */

import { Link } from 'react-router-dom';
import { BookOpen, Bookmark, BookmarkCheck, User, Loader2 } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatRelativeTime, formatPageCount } from '@/lib/utils';
import { useAuthStore } from '@/lib/stores/authStore';
import { useBookmarkStatus, useAddBookmark, useRemoveBookmark } from '@/lib/hooks/useBookmarks';
import type { PublicStoryListItem, BookmarkWithStory } from '@/types/api';

interface PublicStoryCardProps {
  story: PublicStoryListItem | BookmarkWithStory;
  /** If true, shows "Remove" instead of bookmark toggle */
  isSavedView?: boolean;
}

// Type guard to check if it's a BookmarkWithStory
function isBookmarkWithStory(story: PublicStoryListItem | BookmarkWithStory): story is BookmarkWithStory {
  return 'story_title' in story;
}

export function PublicStoryCard({ story, isSavedView = false }: PublicStoryCardProps) {
  const { status } = useAuthStore();
  const isAuthenticated = status === 'authenticated';

  // Normalize story data
  const storyId = isBookmarkWithStory(story) ? story.story_id : story.id;
  const title = isBookmarkWithStory(story) ? story.story_title : story.title;
  const coverUrl = story.cover_image_url;
  const shareToken = story.share_token;
  const ownerName = story.owner_name;
  const format = story.format;
  const pageCount = story.page_count;
  const createdAt = isBookmarkWithStory(story) ? story.story_created_at : story.created_at;

  // Bookmark status (only fetch if authenticated and not in saved view)
  const { data: bookmarkStatus, isLoading: isLoadingStatus } = useBookmarkStatus(
    !isSavedView && isAuthenticated ? storyId : ''
  );
  const addBookmark = useAddBookmark();
  const removeBookmark = useRemoveBookmark();

  const isBookmarked = isSavedView || bookmarkStatus?.is_bookmarked;
  const isBookmarkPending = addBookmark.isPending || removeBookmark.isPending;

  const handleBookmarkToggle = () => {
    if (isBookmarked) {
      removeBookmark.mutate(storyId);
    } else {
      addBookmark.mutate(storyId);
    }
  };

  return (
    <Card className="overflow-hidden transition-all hover:shadow-lg">
      {/* Cover Image or Placeholder */}
      <Link to={`/shared/${shareToken}`}>
        <div className="aspect-[3/4] bg-muted relative overflow-hidden cursor-pointer">
          {coverUrl ? (
            <img
              src={coverUrl}
              alt={`Cover image for "${title}"`}
              className="w-full h-full object-cover transition-transform hover:scale-105"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <BookOpen className="h-16 w-16 text-muted-foreground" aria-hidden="true" />
            </div>
          )}

          {/* Format Badge Overlay */}
          <div className="absolute top-2 right-2">
            <Badge variant="secondary" className="capitalize">
              {format}
            </Badge>
          </div>
        </div>
      </Link>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <Link to={`/shared/${shareToken}`}>
              <h3 className="font-semibold text-lg truncate hover:text-primary transition-colors">
                {title}
              </h3>
            </Link>
            {ownerName && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                <User className="h-3 w-3" />
                <span>{ownerName}</span>
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pb-3">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Pages:</span>
            <span className="font-medium">{formatPageCount(pageCount)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Created:</span>
            <span className="font-medium">{formatRelativeTime(createdAt)}</span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="gap-2">
        <Button asChild className="flex-1" size="sm">
          <Link to={`/shared/${shareToken}`}>
            Read Story
          </Link>
        </Button>

        {/* Bookmark Button - only show if authenticated */}
        {isAuthenticated && (
          <Button
            variant={isBookmarked ? "secondary" : "outline"}
            size="icon"
            onClick={handleBookmarkToggle}
            disabled={isBookmarkPending || isLoadingStatus}
            aria-label={isBookmarked ? "Remove from saved" : "Save story"}
          >
            {isBookmarkPending || isLoadingStatus ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : isBookmarked ? (
              <BookmarkCheck className="h-4 w-4" />
            ) : (
              <Bookmark className="h-4 w-4" />
            )}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
