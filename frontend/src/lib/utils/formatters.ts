/**
 * Utility functions for formatting data.
 */

import { format, formatDistanceToNow, parseISO } from 'date-fns';

/**
 * Format ISO date string to human-readable format.
 */
export const formatDate = (dateString: string, formatStr: string = 'MMM d, yyyy'): string => {
  try {
    return format(parseISO(dateString), formatStr);
  } catch {
    return dateString;
  }
};

/**
 * Format ISO date string to relative time (e.g., "2 hours ago").
 */
export const formatRelativeTime = (dateString: string): string => {
  try {
    return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
  } catch {
    return dateString;
  }
};

/**
 * Format story status to display text.
 */
export const formatStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'Pending',
    generating: 'Generating',
    complete: 'Complete',
    error: 'Error',
  };

  return statusMap[status] || status;
};

/**
 * Get status color for badges.
 */
export const getStatusColor = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  const colorMap: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    pending: 'secondary',
    generating: 'default',
    complete: 'outline',
    error: 'destructive',
  };

  return colorMap[status] || 'default';
};

/**
 * Truncate text to specified length with ellipsis.
 */
export const truncate = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
};

/**
 * Capitalize first letter of string.
 */
export const capitalize = (str: string): string => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Format page count (e.g., "10 pages").
 */
export const formatPageCount = (count: number): string => {
  return `${count} ${count === 1 ? 'page' : 'pages'}`;
};

/**
 * Format illustration style for display.
 */
export const formatIllustrationStyle = (style: string): string => {
  return style
    .split('-')
    .map(word => capitalize(word))
    .join(' ');
};
