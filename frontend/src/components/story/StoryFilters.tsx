/**
 * Story filters component with search and filter controls.
 */

import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import type { StoryFormat, StoryStatus } from '@/types/api';

type SharedFilter = 'all' | 'shared' | 'not_shared';

interface StoryFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  format: StoryFormat | 'all';
  onFormatChange: (value: StoryFormat | 'all') => void;
  status: StoryStatus | 'all';
  onStatusChange: (value: StoryStatus | 'all') => void;
  shared?: SharedFilter;
  onSharedChange?: (value: SharedFilter) => void;
}

export function StoryFilters({
  search,
  onSearchChange,
  format,
  onFormatChange,
  status,
  onStatusChange,
  shared = 'all',
  onSharedChange,
}: StoryFiltersProps) {
  return (
    <div className="space-y-4">
      {/* Search */}
      <div>
        <Label htmlFor="search" className="sr-only">
          Search stories
        </Label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="search"
            type="text"
            placeholder="Search stories..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Format Filter */}
        <div>
          <Label htmlFor="format-filter">Format</Label>
          <Select
            value={format}
            onValueChange={(value) => onFormatChange(value as StoryFormat | 'all')}
          >
            <SelectTrigger id="format-filter">
              <SelectValue placeholder="All formats" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Formats</SelectItem>
              <SelectItem value="storybook">Storybook</SelectItem>
              <SelectItem value="comic">Comic</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Status Filter */}
        <div>
          <Label htmlFor="status-filter">Status</Label>
          <Select
            value={status}
            onValueChange={(value) => onStatusChange(value as StoryStatus | 'all')}
          >
            <SelectTrigger id="status-filter">
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="generating">Generating</SelectItem>
              <SelectItem value="complete">Complete</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Sharing Filter */}
        {onSharedChange && (
          <div>
            <Label htmlFor="shared-filter">Sharing</Label>
            <Select
              value={shared}
              onValueChange={(value) => onSharedChange(value as SharedFilter)}
            >
              <SelectTrigger id="shared-filter">
                <SelectValue placeholder="All stories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Stories</SelectItem>
                <SelectItem value="shared">Shared Only</SelectItem>
                <SelectItem value="not_shared">Not Shared</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>
    </div>
  );
}
