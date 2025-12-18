/**
 * Template picker for story generation.
 * Displays available templates and allows selection to pre-fill the generation form.
 */

import { useState } from 'react';
import { useTemplates, useTemplateCategories } from '@/lib/hooks';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import type { Template } from '@/types/api';

interface TemplatePickerProps {
  onSelect: (template: Template) => void;
  onSkip: () => void;
}

/**
 * Loading skeleton for template cards.
 */
function TemplateCardSkeleton() {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Skeleton className="h-8 w-8 rounded" />
          <Skeleton className="h-5 w-32" />
        </div>
        <Skeleton className="h-4 w-full mt-2" />
        <Skeleton className="h-4 w-2/3" />
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-1">
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-5 w-24" />
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Loading skeleton for the template picker.
 */
function TemplatePickerSkeleton() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <Skeleton className="h-8 w-64 mx-auto" />
        <Skeleton className="h-4 w-96 mx-auto mt-2" />
      </div>
      <div className="flex flex-wrap gap-2 justify-center">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-8 w-20" />
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <TemplateCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

/**
 * Template card component.
 */
function TemplateCard({
  template,
  onSelect
}: {
  template: Template;
  onSelect: (template: Template) => void;
}) {
  return (
    <Card
      className="cursor-pointer hover:border-primary hover:shadow-md transition-all h-full flex flex-col"
      onClick={() => onSelect(template)}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          {template.icon && (
            <span className="text-2xl" role="img" aria-label={template.name}>
              {template.icon}
            </span>
          )}
          <CardTitle className="text-lg line-clamp-1">{template.name}</CardTitle>
        </div>
        <CardDescription className="line-clamp-2">
          {template.description}
        </CardDescription>
      </CardHeader>
      <CardContent className="mt-auto">
        <div className="flex flex-wrap gap-1">
          <Badge variant="secondary">
            Ages {template.age_range_min}-{template.age_range_max}
          </Badge>
          <Badge variant="outline" className="capitalize">
            {template.generation_inputs.format}
          </Badge>
          <Badge variant="outline" className="capitalize">
            {template.generation_inputs.illustration_style.replace(/-/g, ' ')}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Template picker component.
 * Shows a grid of templates with category filtering and a skip option.
 */
export function TemplatePicker({ onSelect, onSkip }: TemplatePickerProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const { data: templatesData, isLoading: templatesLoading } = useTemplates(
    selectedCategory ? { category: selectedCategory } : undefined
  );
  const { data: categoriesData, isLoading: categoriesLoading } = useTemplateCategories();

  const isLoading = templatesLoading || categoriesLoading;

  if (isLoading) {
    return <TemplatePickerSkeleton />;
  }

  const templates = templatesData?.templates || [];
  const categories = categoriesData?.categories || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold">Choose a Template</h2>
        <p className="text-muted-foreground mt-1">
          Start with a pre-made story idea, or create your own from scratch
        </p>
      </div>

      {/* Category filters */}
      {categories.length > 0 && (
        <div className="flex flex-wrap gap-2 justify-center">
          <Button
            variant={selectedCategory === null ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory(null)}
          >
            All
          </Button>
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(category)}
              className="capitalize"
            >
              {category}
            </Button>
          ))}
        </div>
      )}

      {/* Template grid */}
      {templates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onSelect={onSelect}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No templates found.</p>
        </div>
      )}

      {/* Skip button */}
      <div className="text-center pt-4">
        <Button variant="ghost" onClick={onSkip}>
          Skip &mdash; Start from scratch
        </Button>
      </div>
    </div>
  );
}
