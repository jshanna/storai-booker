/**
 * Main multi-step story generation form.
 */

import { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { Form } from '@/components/ui/form';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { createStoryGenerationSchema, StoryGenerationFormData } from '@/lib/schemas/story';
import { useCreateStory, useSettings } from '@/lib/hooks';
import { FullPageSpinner } from '@/components/shared';
import { FormProgress, Step } from './FormProgress';
import { BasicInfoStep } from './BasicInfoStep';
import { StoryDetailsStep } from './StoryDetailsStep';
import { CharactersStep } from './CharactersStep';
import { StyleStep } from './StyleStep';

const STEPS: Step[] = [
  { id: 1, name: 'Basic Info', description: 'Age & topic' },
  { id: 2, name: 'Details', description: 'Setting & format' },
  { id: 3, name: 'Characters', description: 'Main characters' },
  { id: 4, name: 'Style', description: 'Illustration style' },
];

export function GenerationForm() {
  const [currentStep, setCurrentStep] = useState(1);
  const navigate = useNavigate();
  const { mutate: createStory, isPending } = useCreateStory();
  const { data: settings, isLoading: settingsLoading } = useSettings();

  // Create schema based on settings age range
  const schema = useMemo(() => {
    if (!settings || !settings.age_range.enforce) {
      return createStoryGenerationSchema(3, 18);
    }
    return createStoryGenerationSchema(settings.age_range.min, settings.age_range.max);
  }, [settings]);

  // Calculate default age (midpoint of allowed range)
  const defaultAge = useMemo(() => {
    if (!settings || !settings.age_range.enforce) return 7;
    return Math.floor((settings.age_range.min + settings.age_range.max) / 2);
  }, [settings]);

  const form = useForm<StoryGenerationFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      audience_age: defaultAge,
      audience_gender: null,
      topic: '',
      setting: '',
      format: 'storybook',
      illustration_style: 'watercolor',
      characters: [],
      page_count: 10,
      panels_per_page: null,
    },
  });

  // Show loading while fetching settings
  if (settingsLoading) {
    return <FullPageSpinner text="Loading settings..." />;
  }

  const validateCurrentStep = async (): Promise<boolean> => {
    let fieldsToValidate: (keyof StoryGenerationFormData)[] = [];

    switch (currentStep) {
      case 1:
        fieldsToValidate = ['audience_age', 'topic', 'audience_gender'];
        break;
      case 2:
        fieldsToValidate = ['setting', 'format', 'page_count', 'panels_per_page'];
        break;
      case 3:
        fieldsToValidate = ['characters'];
        break;
      case 4:
        fieldsToValidate = ['illustration_style'];
        break;
    }

    const result = await form.trigger(fieldsToValidate);
    return result;
  };

  const handleNext = async (e?: React.MouseEvent<HTMLButtonElement>) => {
    e?.preventDefault();
    const isValid = await validateCurrentStep();
    if (isValid && currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = (e?: React.MouseEvent<HTMLButtonElement>) => {
    e?.preventDefault();
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = async (data: StoryGenerationFormData) => {
    // Prevent submission if not on the last step
    if (currentStep !== STEPS.length) {
      console.warn(`Form submitted on step ${currentStep} but should be on step ${STEPS.length}. Advancing to next step instead.`);
      await handleNext();
      return;
    }

    // Transform form data to match backend API format
    const requestData = {
      title: data.topic.substring(0, 100), // Use topic as title, truncate to 100 chars
      generation_inputs: {
        audience_age: data.audience_age,
        audience_gender: data.audience_gender,
        topic: data.topic,
        setting: data.setting,
        format: data.format,
        illustration_style: data.illustration_style,
        characters: data.characters,
        page_count: data.page_count,
        panels_per_page: data.panels_per_page,
      },
    };

    createStory(requestData, {
      onSuccess: () => {
        // Navigate to library after successful creation
        navigate('/library');
      },
    });
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <BasicInfoStep form={form} />;
      case 2:
        return <StoryDetailsStep form={form} />;
      case 3:
        return <CharactersStep form={form} />;
      case 4:
        return <StyleStep form={form} />;
      default:
        return null;
    }
  };

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Create a New Story</CardTitle>
        <CardDescription>
          Follow the steps to generate a custom children's storybook or comic
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-8">
        {/* Progress Indicator */}
        <FormProgress steps={STEPS} currentStep={currentStep} />

        {/* Form */}
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            onKeyDown={(e) => {
              // Prevent Enter key from submitting form unless on last step
              if (e.key === 'Enter' && currentStep !== STEPS.length) {
                e.preventDefault();
              }
            }}
            className="space-y-8"
          >
            {/* Current Step */}
            {renderStep()}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={handlePrevious}
                disabled={currentStep === 1 || isPending}
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>

              {currentStep < STEPS.length ? (
                <Button type="button" onClick={handleNext} disabled={isPending}>
                  Next
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button type="submit" disabled={isPending}>
                  {isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Story'
                  )}
                </Button>
              )}
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
