import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePagination } from './usePagination';

describe('usePagination', () => {
  it('initializes with default values', () => {
    const { result } = renderHook(() => usePagination());

    expect(result.current.page).toBe(1);
    expect(result.current.limit).toBe(12);
    expect(result.current.skip).toBe(0);
  });

  it('initializes with custom values', () => {
    const { result } = renderHook(() =>
      usePagination({ initialPage: 3, initialLimit: 20 })
    );

    expect(result.current.page).toBe(3);
    expect(result.current.limit).toBe(20);
    expect(result.current.skip).toBe(40); // (3-1) * 20
  });

  it('calculates skip correctly', () => {
    const { result } = renderHook(() =>
      usePagination({ initialPage: 1, initialLimit: 10 })
    );

    expect(result.current.skip).toBe(0);

    act(() => {
      result.current.setPage(2);
    });
    expect(result.current.skip).toBe(10);

    act(() => {
      result.current.setPage(5);
    });
    expect(result.current.skip).toBe(40);
  });

  it('navigates to next page', () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.nextPage();
    });
    expect(result.current.page).toBe(2);

    act(() => {
      result.current.nextPage();
    });
    expect(result.current.page).toBe(3);
  });

  it('navigates to previous page', () => {
    const { result } = renderHook(() => usePagination({ initialPage: 3 }));

    act(() => {
      result.current.prevPage();
    });
    expect(result.current.page).toBe(2);

    act(() => {
      result.current.prevPage();
    });
    expect(result.current.page).toBe(1);
  });

  it('does not go below page 1', () => {
    const { result } = renderHook(() => usePagination({ initialPage: 1 }));

    act(() => {
      result.current.prevPage();
    });
    expect(result.current.page).toBe(1);

    act(() => {
      result.current.prevPage();
    });
    expect(result.current.page).toBe(1);
  });

  it('resets to initial page', () => {
    const { result } = renderHook(() => usePagination({ initialPage: 1 }));

    act(() => {
      result.current.setPage(5);
    });
    expect(result.current.page).toBe(5);

    act(() => {
      result.current.reset();
    });
    expect(result.current.page).toBe(1);
  });

  it('calculates total pages correctly', () => {
    const { result } = renderHook(() => usePagination({ initialLimit: 10 }));

    expect(result.current.getTotalPages(100)).toBe(10);
    expect(result.current.getTotalPages(95)).toBe(10);
    expect(result.current.getTotalPages(101)).toBe(11);
    expect(result.current.getTotalPages(0)).toBe(0);
    expect(result.current.getTotalPages(5)).toBe(1);
  });

  it('determines if can go to next page', () => {
    const { result } = renderHook(() => usePagination({ initialLimit: 10 }));

    // Page 1 of 5 total pages
    expect(result.current.canGoNext(50)).toBe(true);

    // Go to last page
    act(() => {
      result.current.setPage(5);
    });
    expect(result.current.canGoNext(50)).toBe(false);
  });

  it('determines if can go to previous page', () => {
    const { result } = renderHook(() => usePagination());

    // On page 1
    expect(result.current.canGoPrev()).toBe(false);

    // Go to page 2
    act(() => {
      result.current.nextPage();
    });
    expect(result.current.canGoPrev()).toBe(true);
  });

  it('allows setting limit', () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.setLimit(25);
    });
    expect(result.current.limit).toBe(25);
  });

  it('updates skip when limit changes', () => {
    const { result } = renderHook(() =>
      usePagination({ initialPage: 3, initialLimit: 10 })
    );

    expect(result.current.skip).toBe(20); // (3-1) * 10

    act(() => {
      result.current.setLimit(20);
    });
    expect(result.current.skip).toBe(40); // (3-1) * 20
  });
});
