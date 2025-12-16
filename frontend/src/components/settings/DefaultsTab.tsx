/**
 * Defaults settings tab for default generation settings.
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

interface DefaultsTabProps {
  form: UseFormReturn<any>;
}

export function DefaultsTab({ form }: DefaultsTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Default Settings</h3>
        <p className="text-sm text-muted-foreground">
          Set default values for story generation
        </p>
      </div>

      <FormField
        control={form.control}
        name="defaults.format"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Default Format</FormLabel>
            <Select onValueChange={field.onChange} value={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select format" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="storybook">Storybook</SelectItem>
                <SelectItem value="comic">Comic Book</SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              Default format for new stories
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="defaults.illustration_style"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Default Illustration Style</FormLabel>
            <FormControl>
              <Input
                placeholder="e.g., watercolor, cartoon, digital-painting"
                {...field}
              />
            </FormControl>
            <FormDescription>
              Default illustration style for new stories
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="defaults.page_count"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Default Page Count</FormLabel>
            <FormControl>
              <Input
                type="number"
                placeholder="10"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 10)}
              />
            </FormControl>
            <FormDescription>
              Default number of pages (1-50)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="defaults.panels_per_page"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Default Panels Per Page (Comics)</FormLabel>
            <FormControl>
              <Input
                type="number"
                placeholder="4"
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 4)}
              />
            </FormControl>
            <FormDescription>
              Default number of panels per page for comics (1-9)
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
