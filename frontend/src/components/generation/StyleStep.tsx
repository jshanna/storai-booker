/**
 * Step 4: Illustration Style.
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
import { Input } from '@/components/ui/input';
import { StoryGenerationFormData } from '@/lib/schemas/story';

interface StyleStepProps {
  form: UseFormReturn<StoryGenerationFormData>;
}

const ILLUSTRATION_STYLES = [
  { value: 'watercolor', label: 'Watercolor' },
  { value: 'cartoon', label: 'Cartoon' },
  { value: 'digital-painting', label: 'Digital Painting' },
  { value: 'comic-book', label: 'Comic Book' },
  { value: 'anime', label: 'Anime' },
  { value: 'realistic', label: 'Realistic' },
  { value: 'pencil-sketch', label: 'Pencil Sketch' },
  { value: 'oil-painting', label: 'Oil Painting' },
  { value: 'custom', label: 'Custom Style' },
];

export function StyleStep({ form }: StyleStepProps) {
  const styleValue = form.watch('illustration_style');
  const isCustomStyle = styleValue === 'custom' || !ILLUSTRATION_STYLES.find(s => s.value === styleValue);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Illustration Style</h3>
        <p className="text-sm text-muted-foreground">
          Choose the visual style for your story illustrations
        </p>
      </div>

      <FormField
        control={form.control}
        name="illustration_style"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Style</FormLabel>
            <Select
              onValueChange={(value) => {
                if (value === 'custom') {
                  field.onChange('');
                } else {
                  field.onChange(value);
                }
              }}
              value={isCustomStyle ? 'custom' : field.value}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select an illustration style" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {ILLUSTRATION_STYLES.map((style) => (
                  <SelectItem key={style.value} value={style.value}>
                    {style.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormDescription>
              Select a preset style or enter a custom description
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {isCustomStyle && (
        <FormField
          control={form.control}
          name="illustration_style"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Custom Style Description</FormLabel>
              <FormControl>
                <Input
                  placeholder="e.g., Vintage children's book illustration with soft pastels"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Describe your desired illustration style ({field.value?.length || 0}/100 characters)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      )}

      <div className="rounded-lg border p-4 space-y-2">
        <h4 className="font-medium text-sm">Review Your Story</h4>
        <div className="text-sm text-muted-foreground space-y-1">
          <p><strong>Age:</strong> {form.watch('audience_age') || 'Not set'}</p>
          <p><strong>Topic:</strong> {form.watch('topic')?.slice(0, 50) || 'Not set'}{form.watch('topic')?.length > 50 ? '...' : ''}</p>
          <p><strong>Setting:</strong> {form.watch('setting')?.slice(0, 50) || 'Not set'}{form.watch('setting')?.length > 50 ? '...' : ''}</p>
          <p><strong>Format:</strong> {form.watch('format') || 'Not set'}</p>
          <p><strong>Pages:</strong> {form.watch('page_count') || 'Not set'}</p>
          <p><strong>Characters:</strong> {form.watch('characters')?.length || 0}</p>
        </div>
      </div>
    </div>
  );
}
