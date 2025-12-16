/**
 * Zustand store for UI state management.
 * Persisted to localStorage for user preferences.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  // Dark mode
  darkMode: boolean;
  toggleDarkMode: () => void;
  setDarkMode: (value: boolean) => void;

  // Library view preference
  libraryView: 'grid' | 'list';
  setLibraryView: (view: 'grid' | 'list') => void;

  // Sidebar state (for future use)
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (value: boolean) => void;
}

/**
 * UI store with localStorage persistence.
 */
export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Dark mode state and actions
      darkMode: false,
      toggleDarkMode: () =>
        set((state) => {
          const newDarkMode = !state.darkMode;
          // Update document class for Tailwind dark mode
          if (newDarkMode) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { darkMode: newDarkMode };
        }),
      setDarkMode: (value) =>
        set(() => {
          // Update document class for Tailwind dark mode
          if (value) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { darkMode: value };
        }),

      // Library view state and actions
      libraryView: 'grid',
      setLibraryView: (view) => set({ libraryView: view }),

      // Sidebar state and actions
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (value) => set({ sidebarOpen: value }),
    }),
    {
      name: 'storai-ui-storage',
      // Only persist specific fields
      partialize: (state) => ({
        darkMode: state.darkMode,
        libraryView: state.libraryView,
        sidebarOpen: state.sidebarOpen,
      }),
      // Initialize dark mode on load
      onRehydrateStorage: () => (state) => {
        if (state?.darkMode) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },
    }
  )
);
