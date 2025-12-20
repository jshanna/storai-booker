/**
 * Story filters component with search and filter controls.
 */

import { Search } from 'lucide-react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      {/* Search */}
      <div>
        <Label htmlFor="search" className="sr-only">
          {t('library.filters.search')}
        </Label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="search"
            type="text"
            placeholder={t('library.filters.search')}
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="grid gap-4 sm:grid-cols-3">
        {/* Format Filter */}
        <div>
          <Label htmlFor="format-filter">{t('library.filters.format')}</Label>
          <Select
            value={format}
            onValueChange={(value) => onFormatChange(value as StoryFormat | 'all')}
          >
            <SelectTrigger id="format-filter">
              <SelectValue placeholder={t('library.filters.allFormats')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('library.filters.allFormats')}</SelectItem>
              <SelectItem value="storybook">{t('library.filters.storybook')}</SelectItem>
              <SelectItem value="comic">{t('library.filters.comic')}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Status Filter */}
        <div>
          <Label htmlFor="status-filter">{t('library.filters.status')}</Label>
          <Select
            value={status}
            onValueChange={(value) => onStatusChange(value as StoryStatus | 'all')}
          >
            <SelectTrigger id="status-filter">
              <SelectValue placeholder={t('library.filters.allStatuses')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('library.filters.allStatuses')}</SelectItem>
              <SelectItem value="pending">{t('library.filters.pending')}</SelectItem>
              <SelectItem value="generating">{t('library.filters.generating')}</SelectItem>
              <SelectItem value="complete">{t('library.filters.complete')}</SelectItem>
              <SelectItem value="error">{t('library.filters.error')}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Sharing Filter */}
        {onSharedChange && (
          <div>
            <Label htmlFor="shared-filter">{t('library.filters.sharing')}</Label>
            <Select
              value={shared}
              onValueChange={(value) => onSharedChange(value as SharedFilter)}
            >
              <SelectTrigger id="shared-filter">
                <SelectValue placeholder={t('library.filters.allSharing')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('library.filters.allSharing')}</SelectItem>
                <SelectItem value="shared">{t('library.filters.shared')}</SelectItem>
                <SelectItem value="not_shared">{t('library.filters.notShared')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>
    </div>
  );
}
