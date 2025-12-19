/**
 * Step 2: Story Details (setting, format, page count).
 */

import { UseFormReturn } from 'react-hook-form';
import { Book, LayoutGrid } from 'lucide-react';
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
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { StoryGenerationFormData } from '@/lib/schemas/story';
import { cn } from '@/lib/utils';

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
          <FormItem className="space-y-3">
            <FormLabel>Format</FormLabel>
            <FormControl>
              <RadioGroup
                onValueChange={field.onChange}
                defaultValue={field.value}
                className="grid grid-cols-2 gap-4"
              >
                <div>
                  <RadioGroupItem
                    value="storybook"
                    id="format-storybook"
                    className="peer sr-only"
                  />
                  <Label
                    htmlFor="format-storybook"
                    className={cn(
                      'flex flex-col items-center justify-center rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground cursor-pointer',
                      'peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary'
                    )}
                  >
                    <Book className="mb-2 h-8 w-8" />
                    <span className="font-medium">Storybook</span>
                    <span className="text-xs text-muted-foreground text-center mt-1">
                      Full-page illustrations with text
                    </span>
                  </Label>
                </div>
                <div>
                  <RadioGroupItem
                    value="comic"
                    id="format-comic"
                    className="peer sr-only"
                  />
                  <Label
                    htmlFor="format-comic"
                    className={cn(
                      'flex flex-col items-center justify-center rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground cursor-pointer',
                      'peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary'
                    )}
                  >
                    <LayoutGrid className="mb-2 h-8 w-8" />
                    <span className="font-medium">Comic Book</span>
                    <span className="text-xs text-muted-foreground text-center mt-1">
                      Panel layouts with speech bubbles
                    </span>
                  </Label>
                </div>
              </RadioGroup>
            </FormControl>
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
        <div className="rounded-lg border bg-muted/50 p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 text-muted-foreground">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Dynamic Panel Layout</p>
              <p className="text-sm text-muted-foreground mt-1">
                Each page will have 1-6 panels based on story pacing. Dramatic moments get fewer,
                larger panels while action sequences get more panels.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
