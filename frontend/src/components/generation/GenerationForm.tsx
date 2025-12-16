/**
 * Main multi-step story generation form.
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { Form } from '@/components/ui/form';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { storyGenerationSchema, StoryGenerationFormData } from '@/lib/schemas/story';
import { useCreateStory } from '@/lib/hooks';
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

  const form = useForm<StoryGenerationFormData>({
    resolver: zodResolver(storyGenerationSchema),
    defaultValues: {
      audience_age: 7,
      audience_gender: null,
      topic: '',
      setting: '',
      format: 'storybook',
      illustration_style: 'watercolor',
      characters: [''],
      page_count: 10,
      panels_per_page: null,
    },
  });

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

  const handleNext = async () => {
    const isValid = await validateCurrentStep();
    if (isValid && currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = (data: StoryGenerationFormData) => {
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
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
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
