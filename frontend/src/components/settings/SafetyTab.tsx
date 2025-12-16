/**
 * Safety settings tab for AI safety filter configuration.
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface SafetyTabProps {
  form: UseFormReturn<any>;
}

export function SafetyTab({ form }: SafetyTabProps) {
  const bypassSafetyFilters = form.watch('safety_settings.bypass_safety_filters');

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h3 className="text-lg font-medium">AI Safety Filters</h3>
        <p className="text-sm text-muted-foreground">
          Configure how strict the AI safety filters are when generating content.
          These settings help ensure age-appropriate content.
        </p>
      </div>

      {/* Warning if bypassing safety filters */}
      {bypassSafetyFilters && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Warning: Safety Filters Disabled</AlertTitle>
          <AlertDescription>
            You have disabled AI safety filters. This may result in inappropriate
            content being generated. Use with caution and only for testing purposes.
          </AlertDescription>
        </Alert>
      )}

      {/* Safety Threshold */}
      <FormField
        control={form.control}
        name="safety_settings.safety_threshold"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Safety Threshold</FormLabel>
            <Select
              onValueChange={field.onChange}
              value={field.value}
              disabled={bypassSafetyFilters}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select safety threshold" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="block_low_and_above">
                  Strictest (Block Low and Above)
                </SelectItem>
                <SelectItem value="block_medium_and_above">
                  Medium (Block Medium and Above) - Recommended
                </SelectItem>
                <SelectItem value="block_only_high">
                  Lenient (Block Only High Risk)
                </SelectItem>
                <SelectItem value="block_none">
                  None (No Safety Filtering)
                </SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              Controls how aggressively the AI filters potentially inappropriate content.
              Higher settings may reject more content but ensure safer results.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Allow Adult Imagery */}
      <FormField
        control={form.control}
        name="safety_settings.allow_adult_imagery"
        render={({ field }) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
            <div className="space-y-0.5">
              <FormLabel className="text-base">Allow Adult Characters</FormLabel>
              <FormDescription>
                Allow adult (18+) characters in generated images. When disabled,
                only child-friendly characters will be generated.
              </FormDescription>
            </div>
            <FormControl>
              <Switch
                checked={field.value}
                onCheckedChange={field.onChange}
                disabled={bypassSafetyFilters}
              />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Bypass Safety Filters */}
      <FormField
        control={form.control}
        name="safety_settings.bypass_safety_filters"
        render={({ field }) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-destructive p-4">
            <div className="space-y-0.5">
              <FormLabel className="text-base text-destructive">
                Bypass All Safety Filters
              </FormLabel>
              <FormDescription>
                <span className="text-destructive">
                  WARNING: Completely disables all AI safety filters.
                </span>
                <br />
                This should only be used for testing or debugging. Generated content
                may be inappropriate or unsuitable for children.
              </FormDescription>
            </div>
            <FormControl>
              <Switch
                checked={field.value}
                onCheckedChange={field.onChange}
              />
            </FormControl>
          </FormItem>
        )}
      />

      <div className="rounded-md bg-muted p-4 text-sm">
        <p className="font-medium mb-2">About Safety Filters:</p>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground">
          <li>
            Safety filters help ensure generated content is age-appropriate
            and suitable for children.
          </li>
          <li>
            Stricter settings may occasionally reject valid content, while
            lenient settings may allow borderline content.
          </li>
          <li>
            If your stories are frequently rejected, try adjusting topics or
            lowering the safety threshold slightly.
          </li>
          <li>
            These settings apply to both text and image generation from the AI provider.
          </li>
        </ul>
      </div>
    </div>
  );
}
