/**
 * Export API client functions.
 */

import { apiClient } from './client';

export type ExportFormat = 'pdf' | 'images' | 'cbz' | 'epub';

export interface ExportInfo {
  story_id: string;
  format: string;
  filename: string;
  size: number;
  content_type: string;
}

/**
 * Get export info (filename, size) without downloading.
 */
export const getExportInfo = async (
  storyId: string,
  format: ExportFormat
): Promise<ExportInfo> => {
  const response = await apiClient.get<ExportInfo>(
    `/exports/${storyId}/${format}/info`
  );
  return response.data;
};

/**
 * Download story in the specified format.
 * Opens download in browser.
 */
export const downloadExport = async (
  storyId: string,
  format: ExportFormat
): Promise<void> => {
  const response = await apiClient.get(`/exports/${storyId}/${format}`, {
    responseType: 'blob',
  });

  // Get filename from Content-Disposition header
  const contentDisposition = response.headers['content-disposition'];
  let filename = `story.${format}`;
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?(.+)"?/);
    if (match) {
      filename = match[1];
    }
  }

  // Create download link and trigger download
  const blob = new Blob([response.data], {
    type: response.headers['content-type'],
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Format file size for display.
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const exportsApi = {
  getExportInfo,
  downloadExport,
  formatFileSize,
};
