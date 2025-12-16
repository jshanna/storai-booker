/**
 * Generation Limits settings tab.
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

interface GenerationLimitsTabProps {
  form: UseFormReturn<any>;
}

export function GenerationLimitsTab({ form }: GenerationLimitsTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Generation Limits</h3>
        <p className="text-sm text-muted-foreground">
          Configure limits for story generation process
        </p>
      </div>

      <FormField
        control={form.control}
        name="generation_limits.retry_limit"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Retry Limit</FormLabel>
            <FormControl>
              <Input
                type="number"
                placeholder="3"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 3)}
              />
            </FormControl>
            <FormDescription>
              Maximum number of retries for failed generations (1-10)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="generation_limits.max_concurrent_pages"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Max Concurrent Pages</FormLabel>
            <FormControl>
              <Input
                type="number"
                placeholder="5"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 5)}
              />
            </FormControl>
            <FormDescription>
              Maximum number of pages to generate concurrently (1-20)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="generation_limits.timeout_seconds"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Generation Timeout</FormLabel>
            <FormControl>
              <Input
                type="number"
                placeholder="300"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 300)}
              />
            </FormControl>
            <FormDescription>
              Timeout in seconds for generation process (30-1800)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="rounded-lg bg-muted p-4">
        <p className="text-sm text-muted-foreground">
          <strong>Note:</strong> Higher concurrency may result in faster story generation
          but will use more API quota. Lower timeout values may cause incomplete stories
          for complex prompts.
        </p>
      </div>
    </div>
  );
}
