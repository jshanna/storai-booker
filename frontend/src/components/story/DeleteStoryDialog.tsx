/**
 * Delete story confirmation dialog.
 */

import { ConfirmDialog } from '@/components/shared';

interface DeleteStoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  storyTitle: string;
}

export function DeleteStoryDialog({
  open,
  onOpenChange,
  onConfirm,
  storyTitle,
}: DeleteStoryDialogProps) {
  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={onConfirm}
      title="Delete Story"
      description={
        <>
          Are you sure you want to delete <strong>"{storyTitle}"</strong>?
          This action cannot be undone.
        </>
      }
      confirmText="Delete"
      cancelText="Cancel"
      variant="destructive"
    />
  );
}
