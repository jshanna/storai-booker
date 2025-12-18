/**
 * TypeScript type definitions matching backend API models.
 */

// ============================================================================
// Story Types
// ============================================================================

export interface GenerationInputs {
  audience_age: number;
  audience_gender?: string | null;
  topic: string;
  setting: string;
  format: 'storybook' | 'comic';
  illustration_style: string;
  characters: string[];
  page_count: number;
  panels_per_page?: number | null;
}

export interface CharacterDescription {
  name: string;
  physical_description: string;
  personality: string;
  role: string; // protagonist, sidekick, villain, etc.
}

export interface StoryMetadata {
  title?: string | null;
  character_descriptions: CharacterDescription[];
  character_sheet_urls: string[];
  character_relations?: string | null;
  story_outline?: string | null;
  page_outlines: string[];
  illustration_style_guide?: string | null;
}

export interface Page {
  page_number: number;
  text?: string | null;
  illustration_prompt?: string | null;
  illustration_url?: string | null;
  generation_attempts: number;
  validated: boolean;
}

export type StoryStatus = 'pending' | 'generating' | 'complete' | 'error';

export interface Story {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  generation_inputs: GenerationInputs;
  metadata: StoryMetadata;
  pages: Page[];
  status: StoryStatus;
  error_message?: string | null;
  cover_image_url?: string | null;
}

// ============================================================================
// Settings Types
// ============================================================================

export interface AgeRangeSettings {
  min: number;
  max: number;
  enforce: boolean;
}

export type ViolenceLevel = 'none' | 'low' | 'medium' | 'high';

export interface ContentFilterSettings {
  nsfw_filter: boolean;
  violence_level: ViolenceLevel;
  scary_content: boolean;
}

export interface GenerationLimits {
  retry_limit: number;
  max_concurrent_pages: number;
  timeout_seconds: number;
}

export type LLMProviderName = 'openai' | 'anthropic' | 'google';

export interface LLMProviderConfig {
  name: LLMProviderName;
  api_key: string;
  endpoint?: string | null;
  text_model: string;
  image_model: string;
}

export type StoryFormat = 'storybook' | 'comic';

export interface DefaultSettings {
  format: StoryFormat;
  illustration_style: string;
  page_count: number;
  panels_per_page: number;
}

export interface AppSettings {
  id?: string;
  user_id: string;
  age_range: AgeRangeSettings;
  content_filters: ContentFilterSettings;
  generation_limits: GenerationLimits;
  primary_llm_provider: LLMProviderConfig;
  fallback_llm_provider?: LLMProviderConfig | null;
  defaults: DefaultSettings;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface StoryCreateRequest {
  title: string;
  generation_inputs: GenerationInputs;
}

export interface StoryCreateResponse {
  task_id: string;
  story_id: string;
  message: string;
}

export interface StoryListParams {
  skip?: number;
  limit?: number;
  format?: 'storybook' | 'comic';
  status?: StoryStatus;
  search?: string;
}

export interface StoryListResponse {
  stories: Story[];
  total: number;
  skip: number;
  limit: number;
}

export interface StoryStatusResponse {
  story_id: string;
  status: StoryStatus;
  title: string;
  progress?: {
    current_page?: number;
    total_pages?: number;
    current_step?: string;
  };
  error_message?: string | null;
}

export interface SettingsUpdateRequest {
  age_range?: Partial<AgeRangeSettings>;
  content_filters?: Partial<ContentFilterSettings>;
  generation_limits?: Partial<GenerationLimits>;
  primary_llm_provider?: Partial<LLMProviderConfig>;
  fallback_llm_provider?: Partial<LLMProviderConfig> | null;
  defaults?: Partial<DefaultSettings>;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
}

// ============================================================================
// Template Types
// ============================================================================

export interface TemplateGenerationInputs {
  audience_age: number;
  audience_gender?: string | null;
  topic: string;
  setting: string;
  format: 'storybook' | 'comic';
  illustration_style: string;
  characters: string[];
  page_count: number;
  panels_per_page?: number | null;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  generation_inputs: TemplateGenerationInputs;
  age_range_min: number;
  age_range_max: number;
  category: string;
  tags: string[];
  icon?: string | null;
  cover_image_url?: string | null;
}

export interface TemplateListParams {
  category?: string;
  min_age?: number;
  max_age?: number;
  search?: string;
}

export interface TemplateListResponse {
  templates: Template[];
  total: number;
}

export interface TemplateCategoriesResponse {
  categories: string[];
}

// ============================================================================
// Error Types
// ============================================================================

export interface APIError {
  detail: string;
  status_code?: number;
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ValidationErrorResponse {
  detail: ValidationError[];
}
