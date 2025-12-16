/**
 * React Query hooks for settings management.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '@/lib/api';
import { useToast } from './use-toast';
import type { SettingsUpdateRequest } from '@/types/api';

/**
 * Query keys for React Query caching.
 */
export const settingsKeys = {
  all: ['settings'] as const,
  detail: () => [...settingsKeys.all, 'detail'] as const,
};

/**
 * Hook to fetch application settings.
 */
export const useSettings = () => {
  return useQuery({
    queryKey: settingsKeys.detail(),
    queryFn: () => settingsApi.get(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to update settings.
 */
export const useUpdateSettings = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: SettingsUpdateRequest) => settingsApi.update(data),
    onSuccess: (updatedSettings) => {
      // Update cache with server response
      queryClient.setQueryData(settingsKeys.detail(), updatedSettings);

      toast({
        title: 'Settings updated',
        description: 'Your settings have been saved successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to update settings',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};

/**
 * Hook to reset settings to defaults.
 */
export const useResetSettings = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: () => settingsApi.reset(),
    onSuccess: (resetSettings) => {
      // Update cache with reset settings
      queryClient.setQueryData(settingsKeys.detail(), resetSettings);

      toast({
        title: 'Settings reset',
        description: 'Settings have been reset to defaults.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to reset settings',
        description: error.message || 'An unexpected error occurred',
        variant: 'destructive',
      });
    },
  });
};
