/**
 * Shared Reader page - public story reader with comments.
 */

import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User } from 'lucide-react';
import { BookReader } from '@/components/reader';
import { CommentList } from '@/components/comments';
import { FullPageSpinner } from '@/components/shared';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';
import { useSharedStory } from '@/lib/hooks/useSharing';

export function SharedReaderPage() {
  const { token } = useParams<{ token: string }>();
  const { data: story, isLoading, error } = useSharedStory(token!);

  if (isLoading) {
    return <FullPageSpinner text="Loading shared story..." />;
  }

  if (error || !story) {
    return (
      <div className="max-w-2xl mx-auto space-y-4 px-4 py-8">
        <Button asChild variant="ghost">
          <Link to="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Home
          </Link>
        </Button>
        <Alert variant="destructive">
          <AlertTitle>Story Not Found</AlertTitle>
          <AlertDescription>
            This shared story doesn't exist or is no longer available.
            The owner may have disabled sharing.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (story.status !== 'complete') {
    return (
      <div className="max-w-2xl mx-auto space-y-4 px-4 py-8">
        <Button asChild variant="ghost">
          <Link to="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Home
          </Link>
        </Button>
        <Alert>
          <AlertTitle>Story Not Ready</AlertTitle>
          <AlertDescription>
            This story is still being generated. Please check back later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Get the story owner ID from the shared story (if available)
  // Note: We don't have direct access to user_id in SharedStory for privacy reasons
  // Story owner can still delete comments because the backend checks ownership

  return (
    <div className="space-y-6 max-w-6xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <Button asChild variant="ghost" size="sm">
          <Link to="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Home
          </Link>
        </Button>

        {story.owner_name && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <User className="h-4 w-4" />
            <span>Shared by {story.owner_name}</span>
          </div>
        )}
      </div>

      {/* Story Reader */}
      <BookReader story={story} />

      {/* Comments Section */}
      <Card>
        <CardContent className="pt-6">
          <CommentList shareToken={token!} />
        </CardContent>
      </Card>
    </div>
  );
}
