/**
 * Sharing and comments API client functions.
 */

import { apiClient } from './client';
import type {
  ShareResponse,
  SharedStory,
  Comment,
  CommentListResponse,
  PublicStoriesListResponse,
  PublicStoriesListParams,
} from '@/types/api';

/**
 * Enable sharing for a story.
 */
export const enableSharing = async (storyId: string): Promise<ShareResponse> => {
  const response = await apiClient.post<ShareResponse>(`/stories/${storyId}/share`);
  return response.data;
};

/**
 * Disable sharing for a story.
 */
export const disableSharing = async (storyId: string): Promise<ShareResponse> => {
  const response = await apiClient.delete<ShareResponse>(`/stories/${storyId}/share`);
  return response.data;
};

/**
 * Get a shared story by its share token.
 * This is a public endpoint - no authentication required.
 */
export const getSharedStory = async (token: string): Promise<SharedStory> => {
  const response = await apiClient.get<SharedStory>(`/shared/${token}`);
  return response.data;
};

/**
 * List comments on a shared story.
 */
export const listComments = async (
  token: string,
  page: number = 1,
  pageSize: number = 20
): Promise<CommentListResponse> => {
  const response = await apiClient.get<CommentListResponse>(`/shared/${token}/comments`, {
    params: { page, page_size: pageSize },
  });
  return response.data;
};

/**
 * Create a comment on a shared story.
 * Requires authentication.
 */
export const createComment = async (token: string, text: string): Promise<Comment> => {
  const response = await apiClient.post<Comment>(`/shared/${token}/comments`, { text });
  return response.data;
};

/**
 * Delete a comment.
 * Requires authentication - only comment author or story owner can delete.
 */
export const deleteComment = async (commentId: string): Promise<void> => {
  await apiClient.delete(`/comments/${commentId}`);
};

/**
 * List all publicly shared stories with pagination.
 */
export const listPublicStories = async (
  params?: PublicStoriesListParams
): Promise<PublicStoriesListResponse> => {
  const response = await apiClient.get<PublicStoriesListResponse>('/shared', {
    params,
  });
  return response.data;
};

/**
 * Sharing API namespace for easier imports.
 */
export const sharingApi = {
  enableSharing,
  disableSharing,
  getSharedStory,
  listComments,
  createComment,
  deleteComment,
  listPublicStories,
};
