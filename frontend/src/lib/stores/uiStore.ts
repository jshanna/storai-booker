/**
 * Zustand store for UI state management.
 * Persisted to localStorage for user preferences.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import i18n from '@/lib/i18n';
import type { SupportedLanguage } from '@/lib/i18n';

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

  // Language/locale preference
  locale: SupportedLanguage;
  setLocale: (locale: SupportedLanguage) => void;
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

      // Language/locale state and actions
      locale: (i18n.language?.substring(0, 2) as SupportedLanguage) || 'en',
      setLocale: (locale) => {
        i18n.changeLanguage(locale);
        set({ locale });
      },
    }),
    {
      name: 'storai-ui-storage',
      // Only persist specific fields
      partialize: (state) => ({
        darkMode: state.darkMode,
        libraryView: state.libraryView,
        sidebarOpen: state.sidebarOpen,
        locale: state.locale,
      }),
      // Initialize dark mode and locale on load
      onRehydrateStorage: () => (state) => {
        if (state?.darkMode) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        // Sync i18n with persisted locale
        if (state?.locale) {
          i18n.changeLanguage(state.locale);
        }
      },
    }
  )
);
