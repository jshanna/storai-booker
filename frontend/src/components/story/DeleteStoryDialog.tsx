/**
 * Delete story confirmation dialog.
 */

import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={onConfirm}
      title={t('delete.title')}
      description={
        <>
          {t('delete.description', { title: storyTitle })}
          {' '}
          {t('delete.warning')}
        </>
      }
      confirmText={t('delete.confirm')}
      cancelText={t('delete.cancel')}
      variant="destructive"
    />
  );
}
