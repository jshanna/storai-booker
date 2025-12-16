/**
 * Settings page - application configuration.
 */

import { SettingsForm } from '@/components/settings';

export function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Configure your story generation preferences
        </p>
      </div>

      <SettingsForm />
    </div>
  );
}
