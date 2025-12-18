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
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { StoryGenerationFormData } from '@/lib/schemas/story';
import { cn } from '@/lib/utils';

interface StoryDetailsStepProps {
  form: UseFormReturn<StoryGenerationFormData>;
}

/**
 * Visual preview of panel layout based on panel count.
 */
function PanelLayoutPreview({ panelCount }: { panelCount: number }) {
  const getGridClasses = (count: number): string => {
    switch (count) {
      case 1:
        return 'grid-cols-1 grid-rows-1';
      case 2:
        return 'grid-cols-2 grid-rows-1';
      case 3:
        return 'grid-cols-2 grid-rows-2';
      case 4:
        return 'grid-cols-2 grid-rows-2';
      case 6:
        return 'grid-cols-3 grid-rows-2';
      case 9:
        return 'grid-cols-3 grid-rows-3';
      default:
        return 'grid-cols-2 grid-rows-2';
    }
  };

  // For special layouts like 3 panels, we need custom rendering
  if (panelCount === 3) {
    return (
      <div className="w-24 h-32 border rounded bg-muted/30">
        <div className="w-full h-1/2 border-b bg-muted/50" />
        <div className="flex h-1/2">
          <div className="w-1/2 border-r bg-muted/50" />
          <div className="w-1/2 bg-muted/50" />
        </div>
      </div>
    );
  }

  return (
    <div className={cn('w-24 h-32 border rounded bg-muted/30 grid gap-0.5 p-0.5', getGridClasses(panelCount))}>
      {Array.from({ length: panelCount }).map((_, i) => (
        <div key={i} className="bg-muted/50 rounded-sm" />
      ))}
    </div>
  );
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
        <FormField
          control={form.control}
          name="panels_per_page"
          render={({ field }) => {
            const panelCount = field.value || 4;
            return (
              <FormItem>
                <FormLabel>Panels Per Page</FormLabel>
                <div className="flex gap-6 items-start">
                  <div className="flex-1 space-y-4">
                    <FormControl>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">1</span>
                          <span className="text-lg font-bold">{panelCount}</span>
                          <span className="text-sm text-muted-foreground">9</span>
                        </div>
                        <Slider
                          value={[panelCount]}
                          onValueChange={(values: number[]) => field.onChange(values[0])}
                          min={1}
                          max={9}
                          step={1}
                          className="w-full"
                        />
                      </div>
                    </FormControl>
                    <FormDescription>
                      More panels = more images per page (longer generation time)
                    </FormDescription>
                  </div>
                  <div className="flex-shrink-0">
                    <p className="text-xs text-muted-foreground mb-2 text-center">Preview</p>
                    <PanelLayoutPreview panelCount={panelCount} />
                  </div>
                </div>
                <FormMessage />
              </FormItem>
            );
          }}
        />
      )}
    </div>
  );
}
