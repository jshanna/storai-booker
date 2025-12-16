/**
 * Step 1: Basic Information (age and topic).
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
import { Textarea } from '@/components/ui/textarea';
import { StoryGenerationFormData } from '@/lib/schemas/story';
import { useSettings } from '@/lib/hooks';

interface BasicInfoStepProps {
  form: UseFormReturn<StoryGenerationFormData>;
}

export function BasicInfoStep({ form }: BasicInfoStepProps) {
  const topicValue = form.watch('topic') || '';
  const { data: settings } = useSettings();

  // Determine age range text
  const ageRangeText = settings && settings.age_range.enforce
    ? `${settings.age_range.min}-${settings.age_range.max} years (configured in settings)`
    : '3-18 years';

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Basic Information</h3>
        <p className="text-sm text-muted-foreground">
          Tell us about your story and the target audience
        </p>
      </div>

      <FormField
        control={form.control}
        name="audience_age"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Audience Age</FormLabel>
            <FormControl>
              <Input
                type="number"
                placeholder="7"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
              />
            </FormControl>
            <FormDescription>
              Target age for the story ({ageRangeText})
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="topic"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Story Topic</FormLabel>
            <FormControl>
              <Textarea
                placeholder="A brave squirrel exploring a magical forest..."
                className="resize-none"
                rows={4}
                {...field}
              />
            </FormControl>
            <FormDescription>
              What should the story be about? ({topicValue.length}/200 characters)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="audience_gender"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Audience Gender (Optional)</FormLabel>
            <FormControl>
              <Input
                placeholder="Any, Boy, Girl, etc."
                {...field}
                value={field.value || ''}
              />
            </FormControl>
            <FormDescription>
              Optionally specify the target gender
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
