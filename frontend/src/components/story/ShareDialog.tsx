/**
 * Dialog for managing story sharing.
 */

import { useState } from 'react';
import { Copy, Check, Share2, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useEnableSharing, useDisableSharing } from '@/lib/hooks/useSharing';
import { useToast } from '@/lib/hooks/use-toast';
import type { Story } from '@/types/api';

interface ShareDialogProps {
  story: Story;
  trigger?: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function ShareDialog({ story, trigger, open: controlledOpen, onOpenChange }: ShareDialogProps) {
  const [uncontrolledOpen, setUncontrolledOpen] = useState(false);

  // Support both controlled and uncontrolled modes
  const open = controlledOpen ?? uncontrolledOpen;
  const setOpen = onOpenChange ?? setUncontrolledOpen;
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const enableSharing = useEnableSharing();
  const disableSharing = useDisableSharing();

  const isShared = story.is_shared ?? false;
  const shareUrl = story.share_token
    ? `${window.location.origin}/shared/${story.share_token}`
    : null;

  const handleToggleSharing = async (enabled: boolean) => {
    if (enabled) {
      await enableSharing.mutateAsync(story.id);
    } else {
      await disableSharing.mutateAsync(story.id);
    }
  };

  const handleCopyUrl = async () => {
    if (!shareUrl) return;

    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      toast({
        title: 'Link copied',
        description: 'Share link has been copied to clipboard.',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast({
        title: 'Copy failed',
        description: 'Could not copy link to clipboard.',
        variant: 'destructive',
      });
    }
  };

  const isPending = enableSharing.isPending || disableSharing.isPending;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        )}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Share Story</DialogTitle>
          <DialogDescription>
            Share your story with others via a unique link.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Sharing Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="sharing-toggle">Public sharing</Label>
              <p className="text-sm text-muted-foreground">
                Anyone with the link can view this story
              </p>
            </div>
            <Switch
              id="sharing-toggle"
              checked={isShared}
              onCheckedChange={handleToggleSharing}
              disabled={isPending}
              aria-describedby="sharing-description"
            />
          </div>

          {/* Share URL */}
          {isShared && shareUrl && (
            <div className="space-y-2">
              <Label>Share link</Label>
              <div className="flex items-center gap-2">
                <div className="flex-1 p-3 bg-muted rounded-md font-mono text-sm break-all">
                  {shareUrl}
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleCopyUrl}
                  disabled={copied}
                  aria-label={copied ? 'Copied' : 'Copy link'}
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Viewers can read the story and leave comments.
              </p>
            </div>
          )}

          {/* Loading State */}
          {isPending && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          )}

          {/* Sharing Info */}
          {isShared && story.shared_at && (
            <p className="text-xs text-muted-foreground text-center">
              Shared since {new Date(story.shared_at).toLocaleDateString()}
            </p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
