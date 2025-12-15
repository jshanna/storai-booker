/**
 * Story API client functions.
 */

import { apiClient } from './client';
import type {
  Story,
  StoryCreateRequest,
  StoryCreateResponse,
  StoryListParams,
  StoryListResponse,
  StoryStatusResponse,
} from '@/types/api';

/**
 * Create a new story and start generation.
 */
export const createStory = async (data: StoryCreateRequest): Promise<StoryCreateResponse> => {
  const response = await apiClient.post<StoryCreateResponse>('/stories/generate', data);
  return response.data;
};

/**
 * Get list of stories with optional filters and pagination.
 */
export const listStories = async (params?: StoryListParams): Promise<StoryListResponse> => {
  const response = await apiClient.get<StoryListResponse>('/stories', { params });
  return response.data;
};

/**
 * Get a single story by ID.
 */
export const getStory = async (id: string): Promise<Story> => {
  const response = await apiClient.get<Story>(`/stories/${id}`);
  return response.data;
};

/**
 * Get story generation status.
 */
export const getStoryStatus = async (id: string): Promise<StoryStatusResponse> => {
  const response = await apiClient.get<StoryStatusResponse>(`/stories/${id}/status`);
  return response.data;
};

/**
 * Delete a story.
 */
export const deleteStory = async (id: string): Promise<void> => {
  await apiClient.delete(`/stories/${id}`);
};

/**
 * Stories API namespace for easier imports.
 */
export const storiesApi = {
  create: createStory,
  list: listStories,
  get: getStory,
  getStatus: getStoryStatus,
  delete: deleteStory,
};
