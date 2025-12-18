/**
 * Generate page - story generation with template selection.
 */

import { useState } from 'react';
import { GenerationForm } from '@/components/generation/GenerationForm';
import { TemplatePicker } from '@/components/generation/TemplatePicker';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { Template } from '@/types/api';
import type { StoryGenerationFormData } from '@/lib/schemas/story';

type PageState = 'template-picker' | 'form';

/**
 * Convert template generation inputs to form data format.
 */
function templateToFormData(template: Template): Partial<StoryGenerationFormData> {
  const inputs = template.generation_inputs;
  return {
    audience_age: inputs.audience_age,
    audience_gender: inputs.audience_gender,
    topic: inputs.topic,
    setting: inputs.setting,
    format: inputs.format,
    illustration_style: inputs.illustration_style,
    characters: inputs.characters,
    page_count: inputs.page_count,
    panels_per_page: inputs.panels_per_page,
  };
}

export function GeneratePage() {
  const [pageState, setPageState] = useState<PageState>('template-picker');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
    setPageState('form');
  };

  const handleSkipTemplates = () => {
    setSelectedTemplate(null);
    setPageState('form');
  };

  const handleBackToTemplates = () => {
    setPageState('template-picker');
  };

  if (pageState === 'template-picker') {
    return (
      <Card className="max-w-5xl mx-auto">
        <CardHeader>
          <CardTitle>Create a New Story</CardTitle>
          <CardDescription>
            Choose a template to get started quickly, or create your own story from scratch
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TemplatePicker
            onSelect={handleTemplateSelect}
            onSkip={handleSkipTemplates}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <GenerationForm
      initialValues={selectedTemplate ? templateToFormData(selectedTemplate) : undefined}
      onBack={handleBackToTemplates}
    />
  );
}
