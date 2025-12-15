/**
 * Generate page - story generation form (placeholder).
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function GeneratePage() {
  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Generate a New Story</CardTitle>
          <CardDescription>
            Create a custom children's storybook or comic book
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Story generation form will be implemented in Phase 4.3
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
