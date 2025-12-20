/**
 * Reader page - book-style story reader.
 */

import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, MessageSquare } from 'lucide-react';
import { BookReader } from '@/components/reader';
import { CommentList } from '@/components/comments';
import { FullPageSpinner } from '@/components/shared';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useStory } from '@/lib/hooks';

export function ReaderPage() {
  const { id } = useParams<{ id: string }>();
  const { data: story, isLoading, error } = useStory(id!);

  if (isLoading) {
    return <FullPageSpinner text="Loading story..." />;
  }

  if (error || !story) {
    return (
      <div className="max-w-2xl mx-auto space-y-4">
        <Button asChild variant="ghost">
          <Link to="/library">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Library
          </Link>
        </Button>
        <Alert variant="destructive">
          <AlertTitle>Story Not Found</AlertTitle>
          <AlertDescription>
            The story you're looking for doesn't exist or couldn't be loaded.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (story.status !== 'complete') {
    return (
      <div className="max-w-2xl mx-auto space-y-4">
        <Button asChild variant="ghost">
          <Link to="/library">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Library
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

  return (
    <div className="space-y-6">
      <Button asChild variant="ghost" size="sm">
        <Link to="/library">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Library
        </Link>
      </Button>

      <BookReader story={story} />

      {/* Comments Section - only shown for shared stories */}
      {story.is_shared && story.share_token && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Comments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CommentList shareToken={story.share_token} isOwner />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
