/**
 * Zod validation schemas for authentication forms.
 */

import { z } from 'zod';

/**
 * Email validation schema.
 */
const emailSchema = z
  .string({
    required_error: 'Email is required',
  })
  .min(1, 'Email is required')
  .email('Please enter a valid email address');

/**
 * Password validation schema with strength requirements.
 */
const passwordSchema = z
  .string({
    required_error: 'Password is required',
  })
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password must be at most 128 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number');

/**
 * Login form schema.
 */
export const loginSchema = z.object({
  email: emailSchema,
  password: z
    .string({
      required_error: 'Password is required',
    })
    .min(1, 'Password is required'),
});

/**
 * Registration form schema.
 */
export const registerSchema = z
  .object({
    email: emailSchema,
    password: passwordSchema,
    confirmPassword: z
      .string({
        required_error: 'Please confirm your password',
      })
      .min(1, 'Please confirm your password'),
    full_name: z
      .string()
      .max(100, 'Name must be at most 100 characters')
      .optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

/**
 * Profile update schema.
 */
export const profileSchema = z.object({
  full_name: z
    .string()
    .max(100, 'Name must be at most 100 characters')
    .optional()
    .nullable(),
  avatar_url: z
    .string()
    .url('Please enter a valid URL')
    .optional()
    .nullable()
    .or(z.literal('')),
});

/**
 * Change password schema.
 */
export const changePasswordSchema = z
  .object({
    current_password: z
      .string({
        required_error: 'Current password is required',
      })
      .min(1, 'Current password is required'),
    new_password: passwordSchema,
    confirm_password: z
      .string({
        required_error: 'Please confirm your new password',
      })
      .min(1, 'Please confirm your new password'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  });

/**
 * Forgot password schema.
 */
export const forgotPasswordSchema = z.object({
  email: emailSchema,
});

/**
 * Reset password schema.
 */
export const resetPasswordSchema = z
  .object({
    new_password: passwordSchema,
    confirm_password: z
      .string({
        required_error: 'Please confirm your new password',
      })
      .min(1, 'Please confirm your new password'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  });

/**
 * Inferred TypeScript types from schemas.
 */
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ProfileFormData = z.infer<typeof profileSchema>;
export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
