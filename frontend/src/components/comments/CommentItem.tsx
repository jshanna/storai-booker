/**
 * Single comment display component.
 */

import { useState } from 'react';
import { Trash2, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { formatRelativeTime } from '@/lib/utils/formatters';
import type { Comment } from '@/types/api';

interface CommentItemProps {
  comment: Comment;
  currentUserId?: string;
  storyOwnerId?: string;
  onDelete: (commentId: string) => void;
  isDeleting?: boolean;
}

export function CommentItem({
  comment,
  currentUserId,
  storyOwnerId,
  onDelete,
  isDeleting,
}: CommentItemProps) {
  const [deleteOpen, setDeleteOpen] = useState(false);

  // Can delete if user is author or story owner
  const canDelete =
    currentUserId &&
    (comment.user_id === currentUserId || storyOwnerId === currentUserId);

  const handleDelete = () => {
    onDelete(comment.id);
    setDeleteOpen(false);
  };

  return (
    <article className="flex gap-3 py-4 border-b last:border-b-0">
      {/* Avatar */}
      <div className="flex-shrink-0">
        {comment.author_avatar_url ? (
          <img
            src={comment.author_avatar_url}
            alt=""
            className="h-10 w-10 rounded-full object-cover"
          />
        ) : (
          <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
            <User className="h-5 w-5 text-muted-foreground" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium text-sm">{comment.author_name}</span>
          <span className="text-xs text-muted-foreground">
            {formatRelativeTime(comment.created_at)}
          </span>
          {comment.is_edited && (
            <span className="text-xs text-muted-foreground">(edited)</span>
          )}
        </div>
        <p className="mt-1 text-sm whitespace-pre-wrap break-words">
          {comment.text}
        </p>
      </div>

      {/* Delete Button */}
      {canDelete && (
        <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <AlertDialogTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="flex-shrink-0 h-8 w-8 text-muted-foreground hover:text-destructive"
              disabled={isDeleting}
              aria-label="Delete comment"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete comment?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. The comment will be permanently
                removed.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </article>
  );
}
