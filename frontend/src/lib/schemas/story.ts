/**
 * Zod validation schemas for story forms.
 */

import { z } from 'zod';

/**
 * Story generation form schema matching backend validation.
 */
export const storyGenerationSchema = z.object({
  audience_age: z
    .number({
      required_error: 'Age is required',
      invalid_type_error: 'Age must be a number',
    })
    .int('Age must be a whole number')
    .min(3, 'Age must be at least 3')
    .max(18, 'Age must be at most 18'),

  audience_gender: z.string().optional().nullable(),

  topic: z
    .string({
      required_error: 'Topic is required',
    })
    .min(1, 'Topic is required')
    .max(200, 'Topic must be at most 200 characters'),

  setting: z
    .string({
      required_error: 'Setting is required',
    })
    .min(1, 'Setting is required')
    .max(200, 'Setting must be at most 200 characters'),

  format: z
    .enum(['storybook', 'comic'], {
      required_error: 'Format is required',
    })
    .default('storybook'),

  illustration_style: z
    .string({
      required_error: 'Illustration style is required',
    })
    .min(1, 'Illustration style is required')
    .max(100, 'Illustration style must be at most 100 characters'),

  characters: z
    .array(
      z.string().min(1, 'Character name cannot be empty').max(100, 'Character name must be at most 100 characters')
    )
    .min(1, 'At least one character is required')
    .max(10, 'Maximum 10 characters allowed'),

  page_count: z
    .number({
      required_error: 'Page count is required',
      invalid_type_error: 'Page count must be a number',
    })
    .int('Page count must be a whole number')
    .min(1, 'At least 1 page is required')
    .max(50, 'Maximum 50 pages allowed')
    .default(10),

  panels_per_page: z
    .number()
    .int('Panels per page must be a whole number')
    .min(1, 'At least 1 panel per page')
    .max(9, 'Maximum 9 panels per page')
    .optional()
    .nullable(),
});

/**
 * Inferred TypeScript type from schema.
 */
export type StoryGenerationFormData = z.infer<typeof storyGenerationSchema>;

/**
 * Settings form schemas.
 */
export const ageRangeSchema = z.object({
  min: z.number().int().min(0).max(100),
  max: z.number().int().min(0).max(100),
  enforce: z.boolean(),
});

export const contentFiltersSchema = z.object({
  nsfw_filter: z.boolean(),
  violence_level: z.enum(['none', 'low', 'medium', 'high']),
  scary_content: z.boolean(),
});

export const generationLimitsSchema = z.object({
  retry_limit: z.number().int().min(1).max(10),
  max_concurrent_pages: z.number().int().min(1).max(20),
  timeout_seconds: z.number().int().min(30).max(1800),
});

export const llmProviderSchema = z.object({
  name: z.enum(['openai', 'anthropic', 'google']),
  api_key: z.string().min(1, 'API key is required'),
  endpoint: z.string().url('Must be a valid URL').optional().nullable(),
  text_model: z.string().min(1, 'Text model is required'),
  image_model: z.string().min(1, 'Image model is required'),
});

export const defaultSettingsSchema = z.object({
  format: z.enum(['storybook', 'comic']),
  illustration_style: z.string().min(1),
  page_count: z.number().int().min(1).max(50),
  panels_per_page: z.number().int().min(1).max(9),
});

export const appSettingsSchema = z.object({
  age_range: ageRangeSchema,
  content_filters: contentFiltersSchema,
  generation_limits: generationLimitsSchema,
  primary_llm_provider: llmProviderSchema,
  fallback_llm_provider: llmProviderSchema.optional().nullable(),
  defaults: defaultSettingsSchema,
});

/**
 * Inferred types from settings schemas.
 */
export type AppSettingsFormData = z.infer<typeof appSettingsSchema>;
