/**
 * Paginated list of comments with load more functionality.
 */

import { Loader2, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CommentItem } from './CommentItem';
import { CommentForm } from './CommentForm';
import { useInfiniteComments, useDeleteComment } from '@/lib/hooks/useSharing';
import { useAuthStore } from '@/lib/stores/authStore';

interface CommentListProps {
  shareToken: string;
  storyOwnerId?: string;
}

export function CommentList({ shareToken, storyOwnerId }: CommentListProps) {
  const { user } = useAuthStore();
  const {
    data,
    isLoading,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useInfiniteComments(shareToken);

  const deleteComment = useDeleteComment(shareToken);

  const handleDeleteComment = (commentId: string) => {
    deleteComment.mutate(commentId);
  };

  // Flatten pages into single array of comments
  const comments = data?.pages.flatMap((page) => page.comments) ?? [];
  const totalCount = data?.pages[0]?.total ?? 0;

  return (
    <section className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <MessageSquare className="h-5 w-5" />
        <h2 className="text-lg font-semibold">
          Comments {totalCount > 0 && `(${totalCount})`}
        </h2>
      </div>

      {/* Comment Form */}
      <CommentForm shareToken={shareToken} />

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )}

      {/* Comments List */}
      {!isLoading && comments.length === 0 && (
        <p className="text-center text-muted-foreground py-8">
          No comments yet. Be the first to share your thoughts!
        </p>
      )}

      {comments.length > 0 && (
        <div className="divide-y">
          {comments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              currentUserId={user?.id}
              storyOwnerId={storyOwnerId}
              onDelete={handleDeleteComment}
              isDeleting={deleteComment.isPending}
            />
          ))}
        </div>
      )}

      {/* Load More Button */}
      {hasNextPage && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
          >
            {isFetchingNextPage ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              'Load More Comments'
            )}
          </Button>
        </div>
      )}
    </section>
  );
}
