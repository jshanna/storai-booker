/**
 * Hook for managing pagination state.
 */

import { useState } from 'react';

interface UsePaginationOptions {
  initialPage?: number;
  initialLimit?: number;
}

interface UsePaginationReturn {
  page: number;
  limit: number;
  skip: number;
  setPage: (page: number) => void;
  setLimit: (limit: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  reset: () => void;
  getTotalPages: (total: number) => number;
  canGoNext: (total: number) => boolean;
  canGoPrev: () => boolean;
}

export function usePagination(options: UsePaginationOptions = {}): UsePaginationReturn {
  const { initialPage = 1, initialLimit = 12 } = options;

  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);

  const skip = (page - 1) * limit;

  const nextPage = () => setPage((prev) => prev + 1);
  const prevPage = () => setPage((prev) => Math.max(1, prev - 1));
  const reset = () => setPage(initialPage);

  const getTotalPages = (total: number) => Math.ceil(total / limit);
  const canGoNext = (total: number) => page < getTotalPages(total);
  const canGoPrev = () => page > 1;

  return {
    page,
    limit,
    skip,
    setPage,
    setLimit,
    nextPage,
    prevPage,
    reset,
    getTotalPages,
    canGoNext,
    canGoPrev,
  };
}
