/**
 * API Keys settings tab for LLM provider configuration.
 */

import { UseFormReturn } from 'react-hook-form';
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface APIKeysTabProps {
  form: UseFormReturn<any>;
}

// Model options for each provider
const MODEL_OPTIONS = {
  google: {
    text: [
      { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash (Fast, Recommended)' },
      { value: 'gemini-2.0-flash-exp', label: 'Gemini 2.0 Flash Experimental' },
      { value: 'gemini-1.5-pro-latest', label: 'Gemini 1.5 Pro (Latest)' },
      { value: 'gemini-1.5-flash-latest', label: 'Gemini 1.5 Flash (Latest)' },
    ],
    image: [
      { value: 'gemini-2.5-flash-image', label: 'Gemini 2.5 Flash Image (Recommended)' },
      { value: 'gemini-3-pro-preview-image', label: 'Gemini 3 Pro Preview (Higher Quality)' },
    ],
  },
  openai: {
    text: [
      { value: 'gpt-4-turbo-preview', label: 'GPT-4 Turbo Preview' },
      { value: 'gpt-4', label: 'GPT-4' },
      { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    ],
    image: [
      { value: 'dall-e-3', label: 'DALL-E 3 (Recommended)' },
      { value: 'dall-e-2', label: 'DALL-E 2' },
    ],
  },
  anthropic: {
    text: [
      { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus (Highest Quality)' },
      { value: 'claude-3-sonnet-20240229', label: 'Claude 3 Sonnet (Balanced)' },
      { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku (Fast)' },
    ],
    image: [
      { value: 'N/A', label: 'Not Supported (Anthropic does not generate images)' },
    ],
  },
};

export function APIKeysTab({ form }: APIKeysTabProps) {
  // Watch the selected provider to show relevant model options
  const selectedProvider = form.watch('primary_llm_provider.name') || 'google';
  const textModels = MODEL_OPTIONS[selectedProvider as keyof typeof MODEL_OPTIONS]?.text || [];
  const imageModels = MODEL_OPTIONS[selectedProvider as keyof typeof MODEL_OPTIONS]?.image || [];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">API Configuration</h3>
        <p className="text-sm text-muted-foreground">
          Configure your LLM provider API keys and models
        </p>
      </div>

      {/* Primary Provider */}
      <div className="space-y-4 p-4 border rounded-lg">
        <h4 className="font-medium">Primary LLM Provider</h4>

        <FormField
          control={form.control}
          name="primary_llm_provider.name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Provider</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="google">Google (Gemini)</SelectItem>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                The LLM provider to use for story generation
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="primary_llm_provider.api_key"
          render={({ field }) => (
            <FormItem>
              <FormLabel>API Key</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Enter your API key"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Your API key will be encrypted and stored securely
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="primary_llm_provider.text_model"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Text Model</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select text model" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {textModels.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      {model.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>
                Model to use for text generation
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="primary_llm_provider.image_model"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Image Model</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select image model" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {imageModels.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      {model.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>
                Model to use for image generation
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="primary_llm_provider.endpoint"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Custom Endpoint (Optional)</FormLabel>
              <FormControl>
                <Input
                  placeholder="https://api.example.com"
                  {...field}
                  value={field.value || ''}
                />
              </FormControl>
              <FormDescription>
                Custom API endpoint URL (leave empty for default)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
