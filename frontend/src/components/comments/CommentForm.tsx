/**
 * Form for submitting comments.
 */

import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useCreateComment } from '@/lib/hooks/useSharing';
import { useAuthStore } from '@/lib/stores/authStore';

interface CommentFormProps {
  shareToken: string;
}

export function CommentForm({ shareToken }: CommentFormProps) {
  const [text, setText] = useState('');
  const { user, status } = useAuthStore();
  const createComment = useCreateComment(shareToken);

  const isAuthenticated = status === 'authenticated';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    await createComment.mutateAsync(text.trim());
    setText('');
  };

  // Not authenticated - show login prompt
  if (!isAuthenticated || !user) {
    return (
      <div className="p-4 bg-muted/50 rounded-lg text-center">
        <p className="text-sm text-muted-foreground mb-3">
          Sign in to leave a comment
        </p>
        <Button asChild variant="outline" size="sm">
          <Link to="/login">Sign In</Link>
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-3">
        {/* User Avatar */}
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt=""
            className="h-10 w-10 rounded-full object-cover flex-shrink-0"
          />
        ) : (
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-medium text-primary">
              {(user.full_name || user.email)?.[0]?.toUpperCase() || 'U'}
            </span>
          </div>
        )}

        {/* Input */}
        <div className="flex-1">
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Write a comment..."
            className="min-h-[80px] resize-none"
            maxLength={2000}
            disabled={createComment.isPending}
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-muted-foreground">
              {text.length}/2000
            </span>
            <Button
              type="submit"
              size="sm"
              disabled={!text.trim() || createComment.isPending}
            >
              {createComment.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Post
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </form>
  );
}
