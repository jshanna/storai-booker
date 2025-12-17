/**
 * Authentication API client functions.
 */

import { apiClient } from './client';
import type {
  User,
  RegisterRequest,
  LoginRequest,
  TokenResponse,
  RefreshTokenRequest,
  ChangePasswordRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  UpdateProfileRequest,
  OAuthCallbackRequest,
  MessageResponse,
  OAuthUrlResponse,
  OAuthProvidersResponse,
} from '@/types/auth';

// ============================================================================
// Token Storage
// ============================================================================

const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_EXPIRY_KEY = 'token_expiry';

/**
 * Store tokens in localStorage.
 */
export const storeTokens = (tokens: TokenResponse): void => {
  localStorage.setItem(TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  // Store expiry time (current time + expires_in seconds)
  const expiryTime = Date.now() + tokens.expires_in * 1000;
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
};

/**
 * Clear tokens from localStorage.
 */
export const clearTokens = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
};

/**
 * Get stored access token.
 */
export const getStoredAccessToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Get stored refresh token.
 */
export const getStoredRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Check if access token is expired or about to expire (within 5 minutes).
 */
export const isTokenExpired = (): boolean => {
  const expiryStr = localStorage.getItem(TOKEN_EXPIRY_KEY);
  if (!expiryStr) return true;

  const expiry = parseInt(expiryStr, 10);
  // Consider expired if within 5 minutes of expiry
  return Date.now() > expiry - 5 * 60 * 1000;
};

/**
 * Check if we have valid stored tokens.
 */
export const hasValidTokens = (): boolean => {
  const token = getStoredAccessToken();
  const refreshToken = getStoredRefreshToken();
  return !!token && !!refreshToken;
};

// ============================================================================
// Auth API Functions
// ============================================================================

/**
 * Register a new user.
 */
export const register = async (data: RegisterRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/register', data);
  storeTokens(response.data);
  return response.data;
};

/**
 * Login with email and password.
 */
export const login = async (data: LoginRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/login', data);
  storeTokens(response.data);
  return response.data;
};

/**
 * Refresh access token using refresh token.
 */
export const refreshToken = async (): Promise<TokenResponse> => {
  const refresh = getStoredRefreshToken();
  if (!refresh) {
    throw new Error('No refresh token available');
  }

  const response = await apiClient.post<TokenResponse>('/auth/refresh', {
    refresh_token: refresh,
  } as RefreshTokenRequest);

  storeTokens(response.data);
  return response.data;
};

/**
 * Logout and clear tokens.
 */
export const logout = async (): Promise<void> => {
  try {
    const refresh = getStoredRefreshToken();
    if (refresh) {
      await apiClient.post('/auth/logout', { refresh_token: refresh });
    }
  } catch (error) {
    // Ignore errors during logout
    console.error('Logout error:', error);
  } finally {
    clearTokens();
  }
};

/**
 * Get current user profile.
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>('/auth/me');
  return response.data;
};

/**
 * Update user profile.
 */
export const updateProfile = async (data: UpdateProfileRequest): Promise<User> => {
  const response = await apiClient.put<User>('/auth/me', data);
  return response.data;
};

/**
 * Change password.
 */
export const changePassword = async (data: ChangePasswordRequest): Promise<MessageResponse> => {
  const response = await apiClient.post<MessageResponse>('/auth/change-password', data);
  return response.data;
};

/**
 * Request password reset.
 */
export const forgotPassword = async (data: ForgotPasswordRequest): Promise<MessageResponse> => {
  const response = await apiClient.post<MessageResponse>('/auth/forgot-password', data);
  return response.data;
};

/**
 * Reset password with token.
 */
export const resetPassword = async (data: ResetPasswordRequest): Promise<MessageResponse> => {
  const response = await apiClient.post<MessageResponse>('/auth/reset-password', data);
  return response.data;
};

// ============================================================================
// OAuth API Functions
// ============================================================================

/**
 * Get available OAuth providers.
 */
export const getOAuthProviders = async (): Promise<OAuthProvidersResponse> => {
  const response = await apiClient.get<OAuthProvidersResponse>('/auth/oauth/providers');
  return response.data;
};

/**
 * Get Google OAuth authorization URL.
 */
export const getGoogleAuthUrl = async (): Promise<OAuthUrlResponse> => {
  const response = await apiClient.get<OAuthUrlResponse>('/auth/oauth/google');
  return response.data;
};

/**
 * Handle Google OAuth callback.
 */
export const googleCallback = async (data: OAuthCallbackRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/oauth/google/callback', data);
  storeTokens(response.data);
  return response.data;
};

/**
 * Get GitHub OAuth authorization URL.
 */
export const getGitHubAuthUrl = async (): Promise<OAuthUrlResponse> => {
  const response = await apiClient.get<OAuthUrlResponse>('/auth/oauth/github');
  return response.data;
};

/**
 * Handle GitHub OAuth callback.
 */
export const githubCallback = async (data: OAuthCallbackRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/oauth/github/callback', data);
  storeTokens(response.data);
  return response.data;
};

/**
 * Link Google account to existing user.
 */
export const linkGoogleAccount = async (data: OAuthCallbackRequest): Promise<User> => {
  const response = await apiClient.post<User>('/auth/oauth/google/link', data);
  return response.data;
};

/**
 * Link GitHub account to existing user.
 */
export const linkGitHubAccount = async (data: OAuthCallbackRequest): Promise<User> => {
  const response = await apiClient.post<User>('/auth/oauth/github/link', data);
  return response.data;
};

/**
 * Unlink Google account from user.
 */
export const unlinkGoogleAccount = async (): Promise<User> => {
  const response = await apiClient.delete<User>('/auth/oauth/google/unlink');
  return response.data;
};

/**
 * Unlink GitHub account from user.
 */
export const unlinkGitHubAccount = async (): Promise<User> => {
  const response = await apiClient.delete<User>('/auth/oauth/github/unlink');
  return response.data;
};

// ============================================================================
// Auth API Namespace
// ============================================================================

export const authApi = {
  // Token management
  storeTokens,
  clearTokens,
  getStoredAccessToken,
  getStoredRefreshToken,
  isTokenExpired,
  hasValidTokens,

  // Auth
  register,
  login,
  logout,
  refreshToken,

  // User
  getCurrentUser,
  updateProfile,
  changePassword,
  forgotPassword,
  resetPassword,

  // OAuth
  getOAuthProviders,
  getGoogleAuthUrl,
  googleCallback,
  getGitHubAuthUrl,
  githubCallback,
  linkGoogleAccount,
  linkGitHubAccount,
  unlinkGoogleAccount,
  unlinkGitHubAccount,
};
