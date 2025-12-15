/**
 * Step 2: Story Details (setting, format, page count).
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { StoryGenerationFormData } from '@/lib/schemas/story';

interface StoryDetailsStepProps {
  form: UseFormReturn<StoryGenerationFormData>;
}

export function StoryDetailsStep({ form }: StoryDetailsStepProps) {
  const settingValue = form.watch('setting') || '';
  const formatValue = form.watch('format');
  const isComic = formatValue === 'comic';

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Story Details</h3>
        <p className="text-sm text-muted-foreground">
          Configure the setting, format, and length of your story
        </p>
      </div>

      <FormField
        control={form.control}
        name="setting"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Setting</FormLabel>
            <FormControl>
              <Textarea
                placeholder="A magical forest with talking animals and hidden treasures..."
                className="resize-none"
                rows={4}
                {...field}
              />
            </FormControl>
            <FormDescription>
              Where does the story take place? ({settingValue.length}/200 characters)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="format"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Format</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select a format" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="storybook">Storybook</SelectItem>
                <SelectItem value="comic">Comic Book</SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              Choose between traditional storybook or comic book format
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="page_count"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Page Count</FormLabel>
            <FormControl>
              <Input
                type="number"
                placeholder="10"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 10)}
              />
            </FormControl>
            <FormDescription>
              Number of pages (1-50)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {isComic && (
        <FormField
          control={form.control}
          name="panels_per_page"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Panels Per Page</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="4"
                  {...field}
                  value={field.value || ''}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || null)}
                />
              </FormControl>
              <FormDescription>
                Number of comic panels per page (1-9)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      )}
    </div>
  );
}
