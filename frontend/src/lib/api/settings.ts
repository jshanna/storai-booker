/**
 * Settings API client functions.
 */

import { apiClient } from './client';
import type { AppSettings, SettingsUpdateRequest } from '@/types/api';

/**
 * Get application settings.
 */
export const getSettings = async (): Promise<AppSettings> => {
  const response = await apiClient.get<AppSettings>('/settings');
  return response.data;
};

/**
 * Update application settings (partial update).
 */
export const updateSettings = async (data: SettingsUpdateRequest): Promise<AppSettings> => {
  const response = await apiClient.put<AppSettings>('/settings', data);
  return response.data;
};

/**
 * Reset settings to defaults.
 */
export const resetSettings = async (): Promise<AppSettings> => {
  const response = await apiClient.post<AppSettings>('/settings/reset');
  return response.data;
};

/**
 * Settings API namespace for easier imports.
 */
export const settingsApi = {
  get: getSettings,
  update: updateSettings,
  reset: resetSettings,
};
