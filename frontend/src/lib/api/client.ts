/**
 * Axios HTTP client with interceptors for API communication.
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

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

      // Add auth token if available (for future authentication)
      const token = localStorage.getItem('auth_token');
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

  // Response interceptor - handle errors, log responses, etc.
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Log response in development
      if (import.meta.env.DEV) {
        console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
      }

      return response;
    },
    (error: AxiosError) => {
      // Log error
      console.error('[API Response Error]', error.response?.data || error.message);

      // Handle specific error cases
      if (error.response) {
        const { status, data } = error.response;

        switch (status) {
          case 401:
            // Unauthorized - clear auth and redirect to login (for future)
            localStorage.removeItem('auth_token');
            // window.location.href = '/login';
            break;
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
