/**
 * React Query hooks for story management.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { storiesApi } from '@/lib/api';
import { useToast } from './use-toast';
import type {
  StoryCreateRequest,
  StoryListParams,
} from '@/types/api';

/**
 * Query keys for React Query caching.
 */
export const storyKeys = {
  all: ['stories'] as const,
  lists: () => [...storyKeys.all, 'list'] as const,
  list: (params: StoryListParams) => [...storyKeys.lists(), params] as const,
  details: () => [...storyKeys.all, 'detail'] as const,
  detail: (id: string) => [...storyKeys.details(), id] as const,
  status: (id: string) => [...storyKeys.all, 'status', id] as const,
};

/**
 * Hook to fetch list of stories with filters and pagination.
 */
export const useStories = (params: StoryListParams = {}) => {
  return useQuery({
    queryKey: storyKeys.list(params),
    queryFn: () => storiesApi.list(params),
    staleTime: 30000, // 30 seconds
  });
};

/**
 * Hook to fetch a single story by ID.
 */
export const useStory = (id: string) => {
  return useQuery({
    queryKey: storyKeys.detail(id),
    queryFn: () => storiesApi.get(id),
    enabled: !!id,
    staleTime: 60000, // 1 minute
  });
};

/**
 * Hook to fetch story generation status.
 */
export const useStoryStatus = (id: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: storyKeys.status(id),
    queryFn: () => storiesApi.getStatus(id),
    enabled: options?.enabled ?? !!id,
    refetchInterval: (query) => {
      // Poll every 2 seconds if generating, otherwise stop
      return query.state.data?.status === 'generating' ? 2000 : false;
    },
    staleTime: 0, // Always fetch fresh status
  });
};

/**
 * Hook to create a new story.
 */
export const useCreateStory = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: StoryCreateRequest) => storiesApi.create(data),
    onSuccess: (response) => {
      // Invalidate story lists to refetch
      queryClient.invalidateQueries({ queryKey: storyKeys.lists() });

      toast({
        title: 'Story created!',
        description: `Your story "${response.story_id}" is being generated.`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to create story',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};

/**
 * Hook to delete a story.
 */
export const useDeleteStory = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => storiesApi.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: storyKeys.detail(deletedId) });
      // Invalidate list queries
      queryClient.invalidateQueries({ queryKey: storyKeys.lists() });

      toast({
        title: 'Story deleted',
        description: 'The story has been successfully deleted.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to delete story',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};

/**
 * Helper hook to track generating stories and poll their status.
 */
export const useGeneratingStories = () => {
  const { data, isLoading } = useStories({ status: 'generating' });

  return {
    generatingStories: data?.stories || [],
    isLoading,
  };
};
