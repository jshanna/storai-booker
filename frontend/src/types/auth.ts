/**
 * TypeScript type definitions for authentication.
 */

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  email_verified: boolean;
  full_name?: string | null;
  avatar_url?: string | null;
  is_active: boolean;
  created_at: string;
  last_login_at?: string | null;
  google_connected: boolean;
  github_connected: boolean;
}

// ============================================================================
// Auth Request Types
// ============================================================================

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface UpdateProfileRequest {
  full_name?: string | null;
  avatar_url?: string | null;
}

export interface OAuthCallbackRequest {
  code: string;
  state: string;
}

// ============================================================================
// Auth Response Types
// ============================================================================

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MessageResponse {
  message: string;
}

export interface OAuthUrlResponse {
  authorization_url: string;
  state: string;
}

export interface OAuthProvidersResponse {
  google: boolean;
  github: boolean;
}

// ============================================================================
// Auth State Types
// ============================================================================

export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'unauthenticated';

export interface AuthState {
  user: User | null;
  status: AuthStatus;
  accessToken: string | null;
  refreshToken: string | null;
  error: string | null;
}

// ============================================================================
// Token Storage Types
// ============================================================================

export interface StoredTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number; // Unix timestamp
}
