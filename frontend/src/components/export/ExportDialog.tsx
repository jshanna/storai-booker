/**
 * Export dialog component for downloading stories in various formats.
 */

import { useState } from 'react';
import { FileText, Image, BookOpen, Download, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useToast } from '@/lib/hooks/use-toast';
import { downloadExport, type ExportFormat } from '@/lib/api/exports';

interface ExportOption {
  format: ExportFormat;
  name: string;
  description: string;
  icon: React.ReactNode;
}

const exportOptions: ExportOption[] = [
  {
    format: 'pdf',
    name: 'PDF Document',
    description: 'Best for printing and reading on any device',
    icon: <FileText className="h-5 w-5" />,
  },
  {
    format: 'epub',
    name: 'EPUB E-book',
    description: 'Best for e-readers like Kindle, Kobo, or Apple Books',
    icon: <BookOpen className="h-5 w-5" />,
  },
  {
    format: 'images',
    name: 'Images (ZIP)',
    description: 'Download all images as a ZIP archive',
    icon: <Image className="h-5 w-5" />,
  },
  {
    format: 'cbz',
    name: 'Comic Book (CBZ)',
    description: 'Best for comic reader apps',
    icon: <BookOpen className="h-5 w-5" />,
  },
];

interface ExportDialogProps {
  storyId: string;
  storyTitle: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ExportDialog({
  storyId,
  storyTitle,
  open,
  onOpenChange,
}: ExportDialogProps) {
  const { toast } = useToast();
  const [downloading, setDownloading] = useState<ExportFormat | null>(null);

  const handleExport = async (format: ExportFormat) => {
    setDownloading(format);
    try {
      await downloadExport(storyId, format);
      toast({
        title: 'Download started',
        description: `Your ${format.toUpperCase()} file is downloading.`,
      });
      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: 'Export failed',
        description: error.response?.data?.detail || 'Failed to export story',
        variant: 'destructive',
      });
    } finally {
      setDownloading(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Story</DialogTitle>
          <DialogDescription>
            Download "{storyTitle}" in your preferred format.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-3 py-4">
          {exportOptions.map((option) => (
            <Button
              key={option.format}
              variant="outline"
              className="h-auto p-4 justify-start text-left"
              onClick={() => handleExport(option.format)}
              disabled={downloading !== null}
            >
              <div className="flex items-center gap-3 w-full">
                <div className="flex-shrink-0 text-muted-foreground">
                  {downloading === option.format ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    option.icon
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium">{option.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {option.description}
                  </div>
                </div>
                <Download className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
              </div>
            </Button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
