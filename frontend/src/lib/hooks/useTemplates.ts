/**
 * React Query hooks for story templates.
 */

import { useQuery } from '@tanstack/react-query';
import { templatesApi } from '@/lib/api';
import type { TemplateListParams } from '@/types/api';

/**
 * Query keys for React Query caching.
 */
export const templateKeys = {
  all: ['templates'] as const,
  lists: () => [...templateKeys.all, 'list'] as const,
  list: (params?: TemplateListParams) => [...templateKeys.lists(), params] as const,
  details: () => [...templateKeys.all, 'detail'] as const,
  detail: (id: string) => [...templateKeys.details(), id] as const,
  categories: () => [...templateKeys.all, 'categories'] as const,
};

/**
 * Hook to fetch list of templates with optional filters.
 */
export const useTemplates = (params?: TemplateListParams) => {
  return useQuery({
    queryKey: templateKeys.list(params),
    queryFn: () => templatesApi.list(params),
    staleTime: 5 * 60 * 1000, // 5 minutes - templates rarely change
  });
};

/**
 * Hook to fetch a single template by ID.
 */
export const useTemplate = (id: string) => {
  return useQuery({
    queryKey: templateKeys.detail(id),
    queryFn: () => templatesApi.get(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to fetch available template categories.
 */
export const useTemplateCategories = () => {
  return useQuery({
    queryKey: templateKeys.categories(),
    queryFn: () => templatesApi.listCategories(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
