/**
 * Axios HTTP client with interceptors for API communication.
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// Token storage keys
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: any) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * Create and configure Axios client instance.
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: '/api',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds default timeout
  });

  // Request interceptor - add auth headers, log requests, etc.
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Log request in development
      if (import.meta.env.DEV) {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
      }

      // Add auth token if available
      const token = localStorage.getItem(TOKEN_KEY);
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      return config;
    },
    (error: AxiosError) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor - handle errors, token refresh, etc.
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Log response in development
      if (import.meta.env.DEV) {
        console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
      }

      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

      // Log error
      console.error('[API Response Error]', error.response?.data || error.message);

      // Handle 401 Unauthorized with token refresh
      if (error.response?.status === 401 && !originalRequest._retry) {
        // Don't try to refresh for auth endpoints (login, register, refresh itself)
        const isAuthEndpoint = originalRequest.url?.includes('/auth/login') ||
                               originalRequest.url?.includes('/auth/register') ||
                               originalRequest.url?.includes('/auth/refresh');

        if (!isAuthEndpoint) {
          if (isRefreshing) {
            // Queue this request while refresh is in progress
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            }).then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return client(originalRequest);
            }).catch((err) => {
              return Promise.reject(err);
            });
          }

          originalRequest._retry = true;
          isRefreshing = true;

          const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
          if (refreshToken) {
            try {
              const response = await axios.post('/api/auth/refresh', {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token: newRefreshToken, expires_in } = response.data;

              // Store new tokens
              localStorage.setItem(TOKEN_KEY, access_token);
              localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
              localStorage.setItem('token_expiry', (Date.now() + expires_in * 1000).toString());

              // Update header for original request
              originalRequest.headers.Authorization = `Bearer ${access_token}`;

              // Process queued requests
              processQueue(null, access_token);

              return client(originalRequest);
            } catch (refreshError) {
              // Refresh failed, clear tokens and redirect to login
              processQueue(refreshError, null);
              localStorage.removeItem(TOKEN_KEY);
              localStorage.removeItem(REFRESH_TOKEN_KEY);
              localStorage.removeItem('token_expiry');

              // Redirect to login
              window.location.href = '/login';
              return Promise.reject(refreshError);
            } finally {
              isRefreshing = false;
            }
          } else {
            // No refresh token, redirect to login
            localStorage.removeItem(TOKEN_KEY);
            window.location.href = '/login';
          }
        }
      }

      // Handle other error cases
      if (error.response) {
        const { status, data } = error.response;

        switch (status) {
          case 403:
            // Forbidden
            console.error('Access forbidden:', data);
            break;
          case 404:
            // Not found
            console.error('Resource not found:', data);
            break;
          case 422:
            // Validation error
            console.error('Validation error:', data);
            break;
          case 500:
            // Server error
            console.error('Server error:', data);
            break;
          default:
            console.error('Unexpected error:', data);
        }
      } else if (error.request) {
        // Request made but no response received
        console.error('No response received from server');
      } else {
        // Error setting up the request
        console.error('Error setting up request:', error.message);
      }

      return Promise.reject(error);
    }
  );

  return client;
};

/**
 * Shared Axios client instance.
 */
export const apiClient = createApiClient();

/**
 * Helper to extract error message from API error.
 */
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;

    // Handle FastAPI validation errors
    if (data?.detail) {
      if (Array.isArray(data.detail)) {
        // Validation error array
        return data.detail.map((e: any) => e.msg).join(', ');
      }
      // String error message
      return data.detail;
    }

    // Fallback to status text
    return error.response?.statusText || error.message;
  }

  // Handle non-Axios errors
  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
};
