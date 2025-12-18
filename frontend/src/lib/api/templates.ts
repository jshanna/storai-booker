/**
 * Template API client functions.
 */

import { apiClient } from './client';
import type {
  Template,
  TemplateListParams,
  TemplateListResponse,
  TemplateCategoriesResponse,
} from '@/types/api';

/**
 * Get list of templates with optional filters.
 */
export const listTemplates = async (params?: TemplateListParams): Promise<TemplateListResponse> => {
  const response = await apiClient.get<TemplateListResponse>('/templates', { params });
  return response.data;
};

/**
 * Get a single template by ID.
 */
export const getTemplate = async (id: string): Promise<Template> => {
  const response = await apiClient.get<Template>(`/templates/${id}`);
  return response.data;
};

/**
 * Get list of available template categories.
 */
export const listCategories = async (): Promise<TemplateCategoriesResponse> => {
  const response = await apiClient.get<TemplateCategoriesResponse>('/templates/categories');
  return response.data;
};

/**
 * Templates API namespace for easier imports.
 */
export const templatesApi = {
  list: listTemplates,
  get: getTemplate,
  listCategories,
};
