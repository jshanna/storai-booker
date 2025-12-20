/**
 * Bookmarks API client functions.
 */

import { apiClient } from './client';
import type {
  Bookmark,
  BookmarkListResponse,
  BookmarkListParams,
  BookmarkStatus,
} from '@/types/api';

/**
 * List current user's bookmarked stories with pagination.
 */
export const listBookmarks = async (
  params?: BookmarkListParams
): Promise<BookmarkListResponse> => {
  const response = await apiClient.get<BookmarkListResponse>('/bookmarks', {
    params,
  });
  return response.data;
};

/**
 * Add a bookmark for a story.
 */
export const addBookmark = async (storyId: string): Promise<Bookmark> => {
  const response = await apiClient.post<Bookmark>(`/bookmarks/${storyId}`);
  return response.data;
};

/**
 * Remove a bookmark for a story.
 */
export const removeBookmark = async (storyId: string): Promise<void> => {
  await apiClient.delete(`/bookmarks/${storyId}`);
};

/**
 * Check if a story is bookmarked by the current user.
 */
export const getBookmarkStatus = async (storyId: string): Promise<BookmarkStatus> => {
  const response = await apiClient.get<BookmarkStatus>(`/bookmarks/${storyId}/status`);
  return response.data;
};

/**
 * Bookmarks API namespace for easier imports.
 */
export const bookmarksApi = {
  list: listBookmarks,
  add: addBookmark,
  remove: removeBookmark,
  getStatus: getBookmarkStatus,
};
