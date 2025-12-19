/**
 * React Query hooks for story sharing and comments.
 */

import { useMutation, useQuery, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { sharingApi } from '@/lib/api';
import { useToast } from './use-toast';
import { storyKeys } from './useStories';

/**
 * Query keys for sharing-related queries.
 */
export const sharingKeys = {
  all: ['sharing'] as const,
  shared: () => [...sharingKeys.all, 'shared'] as const,
  sharedStory: (token: string) => [...sharingKeys.shared(), token] as const,
  comments: () => [...sharingKeys.all, 'comments'] as const,
  commentList: (token: string, page?: number) => [...sharingKeys.comments(), token, page] as const,
};

/**
 * Hook to fetch a shared story by its share token.
 */
export const useSharedStory = (token: string) => {
  return useQuery({
    queryKey: sharingKeys.sharedStory(token),
    queryFn: () => sharingApi.getSharedStory(token),
    enabled: !!token,
    staleTime: 60000, // 1 minute
  });
};

/**
 * Hook to fetch comments on a shared story with pagination.
 */
export const useComments = (token: string, page: number = 1, pageSize: number = 20) => {
  return useQuery({
    queryKey: sharingKeys.commentList(token, page),
    queryFn: () => sharingApi.listComments(token, page, pageSize),
    enabled: !!token,
    staleTime: 30000, // 30 seconds
  });
};

/**
 * Hook to fetch comments with infinite scrolling / load more.
 */
export const useInfiniteComments = (token: string, pageSize: number = 20) => {
  return useInfiniteQuery({
    queryKey: [...sharingKeys.comments(), token, 'infinite'],
    queryFn: ({ pageParam = 1 }) => sharingApi.listComments(token, pageParam, pageSize),
    getNextPageParam: (lastPage, allPages) => {
      const totalFetched = allPages.reduce((sum, page) => sum + page.comments.length, 0);
      if (totalFetched < lastPage.total) {
        return allPages.length + 1;
      }
      return undefined;
    },
    initialPageParam: 1,
    enabled: !!token,
    staleTime: 30000,
  });
};

/**
 * Hook to enable sharing for a story.
 */
export const useEnableSharing = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (storyId: string) => sharingApi.enableSharing(storyId),
    onSuccess: (_, storyId) => {
      // Invalidate the story detail to get updated sharing info
      queryClient.invalidateQueries({ queryKey: storyKeys.detail(storyId) });
      queryClient.invalidateQueries({ queryKey: storyKeys.lists() });

      toast({
        title: 'Sharing enabled',
        description: 'Your story can now be shared with others.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to enable sharing',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};

/**
 * Hook to disable sharing for a story.
 */
export const useDisableSharing = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (storyId: string) => sharingApi.disableSharing(storyId),
    onSuccess: (_, storyId) => {
      // Invalidate the story detail to get updated sharing info
      queryClient.invalidateQueries({ queryKey: storyKeys.detail(storyId) });
      queryClient.invalidateQueries({ queryKey: storyKeys.lists() });

      toast({
        title: 'Sharing disabled',
        description: 'Your story is no longer publicly accessible.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to disable sharing',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};

/**
 * Hook to create a comment on a shared story.
 */
export const useCreateComment = (token: string) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (text: string) => sharingApi.createComment(token, text),
    onSuccess: () => {
      // Invalidate comments to refetch
      queryClient.invalidateQueries({ queryKey: sharingKeys.comments() });

      toast({
        title: 'Comment added',
        description: 'Your comment has been posted.',
      });
    },
    onError: (error: any) => {
      if (error.response?.status === 429) {
        toast({
          title: 'Rate limit reached',
          description: 'Please wait before posting more comments.',
          variant: 'destructive',
        });
      } else {
        toast({
          title: 'Failed to post comment',
          description: error.message || 'An unexpected error occurred',
          variant: 'destructive',
        });
      }
    },
  });
};

/**
 * Hook to delete a comment.
 */
export const useDeleteComment = (_shareToken: string) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (commentId: string) => sharingApi.deleteComment(commentId),
    onSuccess: () => {
      // Invalidate comments to refetch
      queryClient.invalidateQueries({ queryKey: sharingKeys.comments() });

      toast({
        title: 'Comment deleted',
        description: 'The comment has been removed.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to delete comment',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};
