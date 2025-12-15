/**
 * Library page - story list and filters (placeholder).
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function LibraryPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Story Library</h1>
        <p className="text-muted-foreground">Browse and manage your generated stories</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Your Stories</CardTitle>
          <CardDescription>
            All your generated storybooks and comics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Library view will be implemented in Phase 4.4
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
