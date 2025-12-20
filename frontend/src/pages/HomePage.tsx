/**
 * Home page - welcome page with quick actions.
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { BookOpen, Sparkles, Library } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function HomePage() {
  const { t } = useTranslation();

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          {t('home.title')}
        </h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto px-4">
          {t('home.subtitle')}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <Button asChild size="lg" className="w-full sm:w-auto">
            <Link to="/generate">
              <Sparkles className="mr-2 h-5 w-5" />
              {t('home.cta')}
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
            <Link to="/library">
              <Library className="mr-2 h-5 w-5" />
              {t('home.viewLibrary')}
            </Link>
          </Button>
        </div>
      </div>

      {/* Features */}
      <div className="grid gap-6 md:grid-cols-3 pt-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              {t('home.features.stories.title')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              {t('home.features.stories.description')}
            </CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              {t('home.features.illustrations.title')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              {t('home.features.illustrations.description')}
            </CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Library className="h-5 w-5 text-primary" />
              {t('home.features.export.title')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              {t('home.features.export.description')}
            </CardDescription>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
