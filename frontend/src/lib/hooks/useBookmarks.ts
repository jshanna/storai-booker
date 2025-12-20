/**
 * React Query hooks for bookmarks.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { bookmarksApi } from '@/lib/api';
import { useToast } from './use-toast';
import type { BookmarkListParams } from '@/types/api';

/**
 * Query keys for bookmark-related queries.
 */
export const bookmarkKeys = {
  all: ['bookmarks'] as const,
  lists: () => [...bookmarkKeys.all, 'list'] as const,
  list: (params?: BookmarkListParams) => [...bookmarkKeys.lists(), params] as const,
  status: (storyId: string) => [...bookmarkKeys.all, 'status', storyId] as const,
};

/**
 * Hook to fetch user's bookmarked stories with pagination.
 */
export const useBookmarks = (params?: BookmarkListParams) => {
  return useQuery({
    queryKey: bookmarkKeys.list(params),
    queryFn: () => bookmarksApi.list(params),
    staleTime: 30000, // 30 seconds
  });
};

/**
 * Hook to check if a story is bookmarked.
 */
export const useBookmarkStatus = (storyId: string) => {
  return useQuery({
    queryKey: bookmarkKeys.status(storyId),
    queryFn: () => bookmarksApi.getStatus(storyId),
    enabled: !!storyId,
    staleTime: 60000, // 1 minute
  });
};

/**
 * Hook to add a bookmark.
 */
export const useAddBookmark = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (storyId: string) => bookmarksApi.add(storyId),
    onSuccess: (_, storyId) => {
      // Invalidate bookmark list and status
      queryClient.invalidateQueries({ queryKey: bookmarkKeys.lists() });
      queryClient.invalidateQueries({ queryKey: bookmarkKeys.status(storyId) });

      toast({
        title: 'Story saved',
        description: 'Added to your saved stories.',
      });
    },
    onError: (error: any) => {
      if (error.response?.status === 409) {
        toast({
          title: 'Already saved',
          description: 'This story is already in your saved stories.',
        });
      } else {
        toast({
          title: 'Failed to save story',
          description: error.message || 'An unexpected error occurred',
          variant: 'destructive',
        });
      }
    },
  });
};

/**
 * Hook to remove a bookmark.
 */
export const useRemoveBookmark = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (storyId: string) => bookmarksApi.remove(storyId),
    onSuccess: (_, storyId) => {
      // Invalidate bookmark list and status
      queryClient.invalidateQueries({ queryKey: bookmarkKeys.lists() });
      queryClient.invalidateQueries({ queryKey: bookmarkKeys.status(storyId) });

      toast({
        title: 'Story removed',
        description: 'Removed from your saved stories.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to remove story',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};
