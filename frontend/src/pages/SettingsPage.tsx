/**
 * Settings page - application configuration.
 */

import { useTranslation } from 'react-i18next';
import { SettingsForm } from '@/components/settings';

export function SettingsPage() {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t('settings.title')}</h1>
        <p className="text-muted-foreground">
          {t('settings.subtitle')}
        </p>
      </div>

      <SettingsForm />
    </div>
  );
}
