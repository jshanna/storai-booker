/**
 * Language selector dropdown component.
 * Allows users to switch between supported languages.
 */

import { Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useUIStore } from '@/lib/stores/uiStore';
import { supportedLanguages, type SupportedLanguage } from '@/lib/i18n';

export function LanguageSelector() {
  const { i18n, t } = useTranslation();
  const setLocale = useUIStore((s) => s.setLocale);

  const currentLang =
    supportedLanguages.find((l) => l.code === i18n.language?.substring(0, 2)) ||
    supportedLanguages[0];

  const handleLanguageChange = (code: SupportedLanguage) => {
    setLocale(code);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="h-9 gap-1.5"
          aria-label={t('common.language')}
        >
          <Globe className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">{currentLang.flag}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {supportedLanguages.map((lang) => (
          <DropdownMenuItem
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code)}
            className={lang.code === currentLang.code ? 'bg-accent' : ''}
          >
            <span className="mr-2">{lang.flag}</span>
            {lang.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
