/**
 * Custom hooks for authentication.
 */

import { useCallback, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore, selectIsAuthenticated, selectIsAuthLoading } from '@/lib/stores/authStore';
import type { RegisterRequest, LoginRequest, UpdateProfileRequest, ChangePasswordRequest } from '@/types/auth';

/**
 * Main authentication hook.
 * Provides access to auth state and actions.
 */
export const useAuth = () => {
  const store = useAuthStore();

  const isAuthenticated = useAuthStore(selectIsAuthenticated);
  const isLoading = useAuthStore(selectIsAuthLoading);

  return {
    // State
    user: store.user,
    isAuthenticated,
    isLoading,
    error: store.error,
    status: store.status,
    oauthProviders: store.oauthProviders,

    // Actions
    initialize: store.initialize,
    register: store.register,
    login: store.login,
    logout: store.logout,
    updateProfile: store.updateProfile,
    changePassword: store.changePassword,
    clearError: store.clearError,

    // OAuth
    loadOAuthProviders: store.loadOAuthProviders,
    initiateGoogleAuth: store.initiateGoogleAuth,
    initiateGitHubAuth: store.initiateGitHubAuth,
    handleOAuthCallback: store.handleOAuthCallback,
    linkOAuthAccount: store.linkOAuthAccount,
    unlinkOAuthAccount: store.unlinkOAuthAccount,
  };
};

/**
 * Hook to initialize auth on app mount.
 * Should be called once at the app root level.
 */
export const useAuthInit = () => {
  const initialize = useAuthStore((state) => state.initialize);
  const loadOAuthProviders = useAuthStore((state) => state.loadOAuthProviders);

  useEffect(() => {
    initialize();
    loadOAuthProviders();
  }, [initialize, loadOAuthProviders]);
};

/**
 * Hook for protected routes.
 * Redirects to login if not authenticated.
 */
export const useRequireAuth = (redirectTo: string = '/login') => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading, status } = useAuth();

  useEffect(() => {
    // Wait for auth initialization
    if (status === 'idle') return;

    // Redirect if not authenticated and not loading
    if (!isAuthenticated && !isLoading) {
      // Store intended destination
      const returnTo = encodeURIComponent(location.pathname + location.search);
      navigate(`${redirectTo}?returnTo=${returnTo}`, { replace: true });
    }
  }, [isAuthenticated, isLoading, status, navigate, location, redirectTo]);

  return { isAuthenticated, isLoading };
};

/**
 * Hook to redirect away from auth pages if already authenticated.
 */
export const useRedirectIfAuthenticated = (redirectTo: string = '/') => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading, status } = useAuth();

  useEffect(() => {
    // Wait for auth initialization
    if (status === 'idle') return;

    // Redirect if authenticated
    if (isAuthenticated && !isLoading) {
      // Check for returnTo parameter
      const params = new URLSearchParams(location.search);
      const returnTo = params.get('returnTo');
      navigate(returnTo ? decodeURIComponent(returnTo) : redirectTo, { replace: true });
    }
  }, [isAuthenticated, isLoading, status, navigate, location, redirectTo]);

  return { isAuthenticated, isLoading };
};

/**
 * Hook for login functionality.
 */
export const useLogin = () => {
  const login = useAuthStore((state) => state.login);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);
  const status = useAuthStore((state) => state.status);

  const handleLogin = useCallback(
    async (data: LoginRequest) => {
      await login(data);
    },
    [login]
  );

  return {
    login: handleLogin,
    error,
    clearError,
    isLoading: status === 'loading',
  };
};

/**
 * Hook for registration functionality.
 */
export const useRegister = () => {
  const register = useAuthStore((state) => state.register);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);
  const status = useAuthStore((state) => state.status);

  const handleRegister = useCallback(
    async (data: RegisterRequest) => {
      await register(data);
    },
    [register]
  );

  return {
    register: handleRegister,
    error,
    clearError,
    isLoading: status === 'loading',
  };
};

/**
 * Hook for OAuth authentication.
 */
export const useOAuth = () => {
  const {
    oauthProviders,
    loadOAuthProviders,
    initiateGoogleAuth,
    initiateGitHubAuth,
    handleOAuthCallback,
    linkOAuthAccount,
    unlinkOAuthAccount,
    error,
    clearError,
  } = useAuth();

  const startGoogleAuth = useCallback(async () => {
    const url = await initiateGoogleAuth();
    window.location.href = url;
  }, [initiateGoogleAuth]);

  const startGitHubAuth = useCallback(async () => {
    const url = await initiateGitHubAuth();
    window.location.href = url;
  }, [initiateGitHubAuth]);

  return {
    providers: oauthProviders,
    loadProviders: loadOAuthProviders,
    startGoogleAuth,
    startGitHubAuth,
    handleCallback: handleOAuthCallback,
    linkAccount: linkOAuthAccount,
    unlinkAccount: unlinkOAuthAccount,
    error,
    clearError,
  };
};

/**
 * Hook for profile management.
 */
export const useProfile = () => {
  const user = useAuthStore((state) => state.user);
  const updateProfile = useAuthStore((state) => state.updateProfile);
  const changePassword = useAuthStore((state) => state.changePassword);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);

  const handleUpdateProfile = useCallback(
    async (data: UpdateProfileRequest) => {
      await updateProfile(data);
    },
    [updateProfile]
  );

  const handleChangePassword = useCallback(
    async (data: ChangePasswordRequest) => {
      await changePassword(data);
    },
    [changePassword]
  );

  return {
    user,
    updateProfile: handleUpdateProfile,
    changePassword: handleChangePassword,
    error,
    clearError,
  };
};
