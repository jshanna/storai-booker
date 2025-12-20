/**
 * Main multi-step story generation form.
 */

import { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronLeft, ChevronRight, Loader2, AlertTriangle, Settings } from 'lucide-react';
import { Form } from '@/components/ui/form';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { createStoryGenerationSchema, StoryGenerationFormData } from '@/lib/schemas/story';
import { useCreateStory, useSettings } from '@/lib/hooks';
import { useAnnouncer } from '@/lib/contexts/AnnouncerContext';
import { FullPageSpinner } from '@/components/shared';
import { FormProgress, Step } from './FormProgress';
import { BasicInfoStep } from './BasicInfoStep';
import { StoryDetailsStep } from './StoryDetailsStep';
import { CharactersStep } from './CharactersStep';
import { StyleStep } from './StyleStep';

interface GenerationFormProps {
  /** Initial values to pre-fill the form (e.g., from a template) */
  initialValues?: Partial<StoryGenerationFormData>;
  /** Callback when user wants to go back to template selection */
  onBack?: () => void;
}

export function GenerationForm({ initialValues, onBack }: GenerationFormProps) {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(1);
  const navigate = useNavigate();
  const { mutate: createStory, isPending } = useCreateStory();
  const { data: settings, isLoading: settingsLoading } = useSettings();
  const { announce } = useAnnouncer();

  // Define steps with translations
  const STEPS: Step[] = useMemo(() => [
    { id: 1, name: t('generate.steps.basics'), description: t('generate.form.age') },
    { id: 2, name: t('generate.steps.details'), description: t('generate.form.setting') },
    { id: 3, name: t('generate.steps.characters'), description: t('generate.form.characters') },
    { id: 4, name: t('generate.steps.review'), description: t('generate.form.illustrationStyle') },
  ], [t]);

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
      audience_age: initialValues?.audience_age ?? defaultAge,
      audience_gender: initialValues?.audience_gender ?? null,
      topic: initialValues?.topic ?? '',
      setting: initialValues?.setting ?? '',
      format: initialValues?.format ?? 'storybook',
      illustration_style: initialValues?.illustration_style ?? 'watercolor',
      characters: initialValues?.characters ?? [],
      page_count: initialValues?.page_count ?? 10,
      panels_per_page: initialValues?.panels_per_page ?? null,
    },
  });

  // Show loading while fetching settings
  if (settingsLoading) {
    return <FullPageSpinner text={t('common.loading')} />;
  }

  // Check if API key is configured
  const hasApiKey = Boolean(settings?.primary_llm_provider?.api_key);

  const validateCurrentStep = async (): Promise<boolean> => {
    let fieldsToValidate: (keyof StoryGenerationFormData)[] = [];

    switch (currentStep) {
      case 1:
        fieldsToValidate = ['audience_age', 'topic', 'audience_gender'];
        break;
      case 2:
        fieldsToValidate = ['setting', 'format', 'page_count'];
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
      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);
      announce(`Step ${nextStep} of ${STEPS.length}: ${STEPS[nextStep - 1].name}`);
    } else if (!isValid) {
      announce('Please fix the form errors before continuing', 'assertive');
    }
  };

  const handlePrevious = (e?: React.MouseEvent<HTMLButtonElement>) => {
    e?.preventDefault();
    if (currentStep > 1) {
      const prevStep = currentStep - 1;
      setCurrentStep(prevStep);
      announce(`Step ${prevStep} of ${STEPS.length}: ${STEPS[prevStep - 1].name}`);
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
        <CardTitle>{t('generate.title')}</CardTitle>
        <CardDescription>
          {t('home.subtitle')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-8">
        {/* API Key Warning */}
        {!hasApiKey && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>{t('settings.apiKeys.title')}</AlertTitle>
            <AlertDescription className="flex items-center justify-between">
              <span>{t('settings.apiKeys.description')}</span>
              <Button variant="outline" size="sm" asChild className="ml-4">
                <Link to="/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  {t('nav.settings')}
                </Link>
              </Button>
            </AlertDescription>
          </Alert>
        )}

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
              <div className="flex gap-2">
                {onBack && currentStep === 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={onBack}
                    disabled={isPending}
                  >
                    <ChevronLeft className="mr-2 h-4 w-4" />
                    {t('generate.templates.title')}
                  </Button>
                )}
                <Button
                  type="button"
                  variant="outline"
                  onClick={handlePrevious}
                  disabled={currentStep === 1 || isPending}
                >
                  <ChevronLeft className="mr-2 h-4 w-4" />
                  {t('generate.buttons.previous')}
                </Button>
              </div>

              {currentStep < STEPS.length ? (
                <Button type="button" onClick={handleNext} disabled={isPending}>
                  {t('generate.buttons.next')}
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button type="submit" disabled={isPending || !hasApiKey}>
                  {isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {t('generate.buttons.generating')}
                    </>
                  ) : (
                    t('generate.buttons.generate')
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
