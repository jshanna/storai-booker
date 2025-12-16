/**
 * Content Filters settings tab.
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
import { Input } from '@/components/ui/input';

interface ContentFiltersTabProps {
  form: UseFormReturn<any>;
}

export function ContentFiltersTab({ form }: ContentFiltersTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Content Filters</h3>
        <p className="text-sm text-muted-foreground">
          Configure content filtering for generated stories
        </p>
      </div>

      <FormField
        control={form.control}
        name="content_filters.nsfw_filter"
        render={({ field }) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
            <div className="space-y-0.5">
              <FormLabel className="text-base">NSFW Filter</FormLabel>
              <FormDescription>
                Block inappropriate content for children
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

      <FormField
        control={form.control}
        name="content_filters.violence_level"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Violence Level</FormLabel>
            <Select onValueChange={field.onChange} value={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select violence level" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="none">None - No violence allowed</SelectItem>
                <SelectItem value="low">Low - Minimal cartoon violence</SelectItem>
                <SelectItem value="medium">Medium - Moderate action scenes</SelectItem>
                <SelectItem value="high">High - More intense action</SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              Maximum level of violence allowed in stories
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="content_filters.scary_content"
        render={({ field }) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
            <div className="space-y-0.5">
              <FormLabel className="text-base">Allow Scary Content</FormLabel>
              <FormDescription>
                Allow mildly scary or spooky themes
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

      {/* Age Range */}
      <div className="space-y-4 p-4 border rounded-lg">
        <h4 className="font-medium">Age Range Restrictions</h4>

        <FormField
          control={form.control}
          name="age_range.min"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Minimum Age</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="3"
                  {...field}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || 3)}
                />
              </FormControl>
              <FormDescription>
                Minimum target audience age (0-100)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="age_range.max"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Maximum Age</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="12"
                  {...field}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || 12)}
                />
              </FormControl>
              <FormDescription>
                Maximum target audience age (0-100)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="age_range.enforce"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between">
              <div className="space-y-0.5">
                <FormLabel>Enforce Age Range</FormLabel>
                <FormDescription>
                  Prevent story generation outside this age range
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
      </div>
    </div>
  );
}
