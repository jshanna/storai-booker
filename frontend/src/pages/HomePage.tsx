/**
 * Home page - welcome page with quick actions.
 */

import { Link } from 'react-router-dom';
import { BookOpen, Sparkles, Library } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function HomePage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          Welcome to StorAI Booker
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Create magical children's storybooks and comic books powered by AI.
          Generate custom illustrated stories in minutes.
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <Button asChild size="lg">
            <Link to="/generate">
              <Sparkles className="mr-2 h-5 w-5" />
              Create Story
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link to="/library">
              <Library className="mr-2 h-5 w-5" />
              View Library
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
              AI-Powered Generation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Advanced AI creates unique stories with character development,
              plot outlines, and custom illustrations tailored to your preferences.
            </CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              Custom Stories
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Choose your topic, characters, setting, and illustration style.
              Every story is unique and personalized to your specifications.
            </CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Library className="h-5 w-5 text-primary" />
              Story Library
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Save and organize all your generated stories. Browse, read,
              and manage your collection in one place.
            </CardDescription>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
