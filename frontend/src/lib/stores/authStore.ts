/**
 * Zustand store for authentication state management.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  User,
  AuthStatus,
  RegisterRequest,
  LoginRequest,
  UpdateProfileRequest,
  ChangePasswordRequest,
  OAuthCallbackRequest,
} from '@/types/auth';
import { authApi } from '@/lib/api/auth';

interface AuthState {
  // State
  user: User | null;
  status: AuthStatus;
  error: string | null;
  oauthProviders: { google: boolean; github: boolean } | null;

  // Actions
  initialize: () => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<boolean>;
  updateProfile: (data: UpdateProfileRequest) => Promise<void>;
  changePassword: (data: ChangePasswordRequest) => Promise<void>;
  clearError: () => void;

  // OAuth Actions
  loadOAuthProviders: () => Promise<void>;
  initiateGoogleAuth: () => Promise<string>;
  initiateGitHubAuth: () => Promise<string>;
  handleOAuthCallback: (provider: 'google' | 'github', code: string, state: string) => Promise<void>;
  linkOAuthAccount: (provider: 'google' | 'github', code: string, state: string) => Promise<void>;
  unlinkOAuthAccount: (provider: 'google' | 'github') => Promise<void>;
}

/**
 * Auth store with persistence for essential state.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      status: 'idle',
      error: null,
      oauthProviders: null,

      /**
       * Initialize auth state on app load.
       * Checks for existing tokens and fetches user if valid.
       */
      initialize: async () => {
        // Don't re-initialize if already authenticated
        if (get().status === 'authenticated') return;

        set({ status: 'loading', error: null });

        try {
          // Check if we have valid tokens
          if (!authApi.hasValidTokens()) {
            set({ status: 'unauthenticated', user: null });
            return;
          }

          // Try to refresh if token is expired
          if (authApi.isTokenExpired()) {
            try {
              await authApi.refreshToken();
            } catch {
              // Refresh failed, clear tokens
              authApi.clearTokens();
              set({ status: 'unauthenticated', user: null });
              return;
            }
          }

          // Fetch current user
          const user = await authApi.getCurrentUser();
          set({ status: 'authenticated', user });
        } catch (error) {
          // Auth check failed
          authApi.clearTokens();
          set({ status: 'unauthenticated', user: null });
        }
      },

      /**
       * Register a new user.
       */
      register: async (data: RegisterRequest) => {
        set({ status: 'loading', error: null });

        try {
          await authApi.register(data);
          const user = await authApi.getCurrentUser();
          set({ status: 'authenticated', user });
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || 'Registration failed';
          set({ status: 'unauthenticated', error: message });
          throw new Error(message);
        }
      },

      /**
       * Login with email and password.
       */
      login: async (data: LoginRequest) => {
        set({ status: 'loading', error: null });

        try {
          await authApi.login(data);
          const user = await authApi.getCurrentUser();
          set({ status: 'authenticated', user });
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || 'Login failed';
          set({ status: 'unauthenticated', error: message });
          throw new Error(message);
        }
      },

      /**
       * Logout and clear session.
       */
      logout: async () => {
        try {
          await authApi.logout();
        } finally {
          set({ status: 'unauthenticated', user: null, error: null });
        }
      },

      /**
       * Refresh the current session.
       * Returns true if refresh was successful.
       */
      refreshSession: async (): Promise<boolean> => {
        try {
          if (!authApi.hasValidTokens()) {
            return false;
          }

          await authApi.refreshToken();
          const user = await authApi.getCurrentUser();
          set({ status: 'authenticated', user });
          return true;
        } catch {
          set({ status: 'unauthenticated', user: null });
          return false;
        }
      },

      /**
       * Update user profile.
       */
      updateProfile: async (data: UpdateProfileRequest) => {
        try {
          const user = await authApi.updateProfile(data);
          set({ user });
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || 'Profile update failed';
          set({ error: message });
          throw new Error(message);
        }
      },

      /**
       * Change password.
       */
      changePassword: async (data: ChangePasswordRequest) => {
        try {
          await authApi.changePassword(data);
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || 'Password change failed';
          set({ error: message });
          throw new Error(message);
        }
      },

      /**
       * Clear error state.
       */
      clearError: () => {
        set({ error: null });
      },

      // OAuth Actions

      /**
       * Load available OAuth providers.
       */
      loadOAuthProviders: async () => {
        try {
          const providers = await authApi.getOAuthProviders();
          set({ oauthProviders: providers });
        } catch (error) {
          console.error('Failed to load OAuth providers:', error);
          set({ oauthProviders: { google: false, github: false } });
        }
      },

      /**
       * Initiate Google OAuth flow.
       * Returns the authorization URL to redirect to.
       */
      initiateGoogleAuth: async (): Promise<string> => {
        try {
          const { authorization_url, state } = await authApi.getGoogleAuthUrl();
          // Store state for validation (prevents CSRF)
          sessionStorage.setItem('oauth_state', state);
          sessionStorage.setItem('oauth_provider', 'google');
          return authorization_url;
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Failed to initiate Google auth';
          throw new Error(message);
        }
      },

      /**
       * Initiate GitHub OAuth flow.
       * Returns the authorization URL to redirect to.
       */
      initiateGitHubAuth: async (): Promise<string> => {
        try {
          const { authorization_url, state } = await authApi.getGitHubAuthUrl();
          // Store state for validation (prevents CSRF)
          sessionStorage.setItem('oauth_state', state);
          sessionStorage.setItem('oauth_provider', 'github');
          return authorization_url;
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Failed to initiate GitHub auth';
          throw new Error(message);
        }
      },

      /**
       * Handle OAuth callback after redirect.
       */
      handleOAuthCallback: async (provider: 'google' | 'github', code: string, state: string) => {
        set({ status: 'loading', error: null });

        try {
          // Validate state parameter
          const storedState = sessionStorage.getItem('oauth_state');
          if (state !== storedState) {
            throw new Error('Invalid OAuth state');
          }

          // Clear stored OAuth data
          sessionStorage.removeItem('oauth_state');
          sessionStorage.removeItem('oauth_provider');

          const callbackData: OAuthCallbackRequest = { code, state };

          if (provider === 'google') {
            await authApi.googleCallback(callbackData);
          } else {
            await authApi.githubCallback(callbackData);
          }

          // Fetch user after OAuth login
          const user = await authApi.getCurrentUser();
          set({ status: 'authenticated', user });
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || 'OAuth login failed';
          set({ status: 'unauthenticated', error: message });
          throw new Error(message);
        }
      },

      /**
       * Link OAuth account to existing user.
       */
      linkOAuthAccount: async (provider: 'google' | 'github', code: string, state: string) => {
        try {
          const callbackData: OAuthCallbackRequest = { code, state };
          let user: User;

          if (provider === 'google') {
            user = await authApi.linkGoogleAccount(callbackData);
          } else {
            user = await authApi.linkGitHubAccount(callbackData);
          }

          set({ user });
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || `Failed to link ${provider} account`;
          set({ error: message });
          throw new Error(message);
        }
      },

      /**
       * Unlink OAuth account from user.
       */
      unlinkOAuthAccount: async (provider: 'google' | 'github') => {
        try {
          let user: User;

          if (provider === 'google') {
            user = await authApi.unlinkGoogleAccount();
          } else {
            user = await authApi.unlinkGitHubAccount();
          }

          set({ user });
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || `Failed to unlink ${provider} account`;
          set({ error: message });
          throw new Error(message);
        }
      },
    }),
    {
      name: 'storai-auth-storage',
      // Only persist minimal auth state (not the full user object)
      partialize: (state) => ({
        // We don't persist user data - it's fetched fresh on init
        // Only persist that we might be authenticated
        status: state.status === 'authenticated' ? 'idle' : 'unauthenticated',
      }),
    }
  )
);

/**
 * Selector for checking if user is authenticated.
 */
export const selectIsAuthenticated = (state: AuthState): boolean =>
  state.status === 'authenticated' && state.user !== null;

/**
 * Selector for checking if auth is loading.
 */
export const selectIsAuthLoading = (state: AuthState): boolean =>
  state.status === 'loading' || state.status === 'idle';
