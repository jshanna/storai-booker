/**
 * Main settings form with tabbed interface.
 */

import { useForm } from 'react-hook-form';
import { Loader2, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useSettings, useUpdateSettings, useResetSettings } from '@/lib/hooks';
import { FullPageSpinner } from '@/components/shared';
import { APIKeysTab } from './APIKeysTab';
import { DefaultsTab } from './DefaultsTab';
import { ContentFiltersTab } from './ContentFiltersTab';
import { GenerationLimitsTab } from './GenerationLimitsTab';
import { SafetyTab } from './SafetyTab';
import { ConfirmDialog } from '@/components/shared';
import { useState } from 'react';

export function SettingsForm() {
  const { data: settings, isLoading } = useSettings();
  const { mutate: updateSettings, isPending: isUpdating } = useUpdateSettings();
  const { mutate: resetSettings, isPending: isResetting } = useResetSettings();
  const [resetDialogOpen, setResetDialogOpen] = useState(false);

  // Show loading state while fetching settings
  if (isLoading || !settings) {
    return <FullPageSpinner text="Loading settings..." />;
  }

  return <SettingsFormContent
    settings={settings}
    updateSettings={updateSettings}
    resetSettings={resetSettings}
    isUpdating={isUpdating}
    isResetting={isResetting}
    resetDialogOpen={resetDialogOpen}
    setResetDialogOpen={setResetDialogOpen}
  />;
}

interface SettingsFormContentProps {
  settings: any;
  updateSettings: any;
  resetSettings: any;
  isUpdating: boolean;
  isResetting: boolean;
  resetDialogOpen: boolean;
  setResetDialogOpen: (open: boolean) => void;
}

function SettingsFormContent({
  settings,
  updateSettings,
  resetSettings,
  isUpdating,
  isResetting,
  resetDialogOpen,
  setResetDialogOpen,
}: SettingsFormContentProps) {
  // Ensure settings has all required fields before initializing form
  const defaultSettings = {
    primary_llm_provider: {
      name: '',
      api_key: '',
      text_model: '',
      image_model: '',
      endpoint: null,
    },
    defaults: {
      format: 'storybook',
      illustration_style: '',
      page_count: 10,
      panels_per_page: 4,
    },
    content_filters: {
      nsfw_filter: true,
      violence_level: 'low',
      scary_content: false,
    },
    safety_settings: {
      safety_threshold: 'block_medium_and_above',
      allow_adult_imagery: false,
      bypass_safety_filters: false,
    },
    generation_limits: {
      retry_limit: 3,
      max_concurrent_pages: 5,
      timeout_seconds: 300,
    },
    age_range: {
      min: 3,
      max: 12,
      enforce: true,
    },
    ...settings,
  };

  const form = useForm({
    defaultValues: defaultSettings,
    values: defaultSettings,
  });

  const onSubmit = (data: any) => {
    updateSettings(data);
  };

  const handleReset = () => {
    setResetDialogOpen(true);
  };

  const confirmReset = () => {
    resetSettings(undefined, {
      onSuccess: (newSettings: any) => {
        form.reset(newSettings);
        setResetDialogOpen(false);
      },
    });
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Application Settings</CardTitle>
          <CardDescription>
            Configure your story generation preferences and API settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <Tabs defaultValue="api-keys" className="w-full">
                <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 md:grid-cols-5">
                  <TabsTrigger value="api-keys">API Keys</TabsTrigger>
                  <TabsTrigger value="defaults">Defaults</TabsTrigger>
                  <TabsTrigger value="content-filters">Content</TabsTrigger>
                  <TabsTrigger value="safety">Safety</TabsTrigger>
                  <TabsTrigger value="generation-limits">Limits</TabsTrigger>
                </TabsList>

                <TabsContent value="api-keys" className="mt-6">
                  <APIKeysTab form={form} />
                </TabsContent>

                <TabsContent value="defaults" className="mt-6">
                  <DefaultsTab form={form} />
                </TabsContent>

                <TabsContent value="content-filters" className="mt-6">
                  <ContentFiltersTab form={form} />
                </TabsContent>

                <TabsContent value="safety" className="mt-6">
                  <SafetyTab form={form} />
                </TabsContent>

                <TabsContent value="generation-limits" className="mt-6">
                  <GenerationLimitsTab form={form} />
                </TabsContent>
              </Tabs>

              {/* Action Buttons */}
              <div className="flex justify-between pt-6 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleReset}
                  disabled={isUpdating || isResetting}
                >
                  <RotateCcw className="mr-2 h-4 w-4" />
                  Reset to Defaults
                </Button>

                <Button type="submit" disabled={isUpdating || isResetting}>
                  {isUpdating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Reset Confirmation Dialog */}
      <ConfirmDialog
        open={resetDialogOpen}
        onOpenChange={setResetDialogOpen}
        onConfirm={confirmReset}
        title="Reset Settings"
        description="Are you sure you want to reset all settings to their default values? This action cannot be undone."
        confirmText="Reset"
        cancelText="Cancel"
        variant="destructive"
      />
    </>
  );
}
