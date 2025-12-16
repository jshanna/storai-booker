/**
 * Story card component for displaying a story in grid/list view.
 */

import { Link } from 'react-router-dom';
import { BookOpen, Trash2, MoreVertical, Eye, Sparkles } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { formatRelativeTime, formatPageCount, getStatusColor } from '@/lib/utils';
import type { Story } from '@/types/api';
import { Progress } from '@/components/ui/progress';
import { GenerationArtifacts } from '@/components/reader/GenerationArtifacts';
import { useState } from 'react';

interface StoryCardProps {
  story: Story;
  onDelete: (id: string) => void;
}

export function StoryCard({ story, onDelete }: StoryCardProps) {
  const [artifactsOpen, setArtifactsOpen] = useState(false);
  const isGenerating = story.status === 'generating';
  const hasError = story.status === 'error';
  const isComplete = story.status === 'complete';

  // Calculate progress for generating stories
  const progress = isGenerating && story.pages.length > 0
    ? (story.pages.filter(p => p.text).length / story.generation_inputs.page_count) * 100
    : 0;

  return (
    <Card className="overflow-hidden transition-all hover:shadow-lg">
      {/* Cover Image or Placeholder */}
      <div className="aspect-[3/4] bg-muted relative overflow-hidden">
        {story.cover_image_url ? (
          <img
            src={story.cover_image_url}
            alt={story.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <BookOpen className="h-16 w-16 text-muted-foreground" />
          </div>
        )}

        {/* Status Badge Overlay */}
        <div className="absolute top-2 right-2">
          <Badge variant={getStatusColor(story.status)}>
            {story.status}
          </Badge>
        </div>
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg truncate">{story.title}</h3>
            <p className="text-sm text-muted-foreground">
              {formatRelativeTime(story.created_at)}
            </p>
          </div>

          {/* Actions Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {isComplete && (
                <>
                  <DropdownMenuItem asChild>
                    <Link to={`/reader/${story.id}`}>
                      <Eye className="mr-2 h-4 w-4" />
                      Read Story
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setArtifactsOpen(true)}>
                    <Sparkles className="mr-2 h-4 w-4" />
                    View Artifacts
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuItem
                onClick={() => onDelete(story.id)}
                className="text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>

      <CardContent className="pb-3">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Format:</span>
            <span className="font-medium capitalize">{story.generation_inputs.format}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Pages:</span>
            <span className="font-medium">{formatPageCount(story.generation_inputs.page_count)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Age:</span>
            <span className="font-medium">{story.generation_inputs.audience_age}</span>
          </div>
        </div>

        {/* Progress Bar for Generating Stories */}
        {isGenerating && (
          <div className="mt-4 space-y-2">
            <Progress value={progress} />
            <p className="text-xs text-muted-foreground text-center">
              Generating... {Math.round(progress)}%
            </p>
          </div>
        )}

        {/* Error Message */}
        {hasError && story.error_message && (
          <div className="mt-3 p-2 bg-destructive/10 rounded text-xs text-destructive">
            {story.error_message}
          </div>
        )}
      </CardContent>

      <CardFooter>
        {isComplete ? (
          <Button asChild className="w-full" size="sm">
            <Link to={`/reader/${story.id}`}>
              <Eye className="mr-2 h-4 w-4" />
              Read Story
            </Link>
          </Button>
        ) : isGenerating ? (
          <Button disabled className="w-full" size="sm">
            Generating...
          </Button>
        ) : (
          <Button disabled variant="destructive" className="w-full" size="sm">
            Generation Failed
          </Button>
        )}
      </CardFooter>

      {/* Generation Artifacts Dialog */}
      {isComplete && (
        <GenerationArtifacts
          story={story}
          open={artifactsOpen}
          onOpenChange={setArtifactsOpen}
        />
      )}
    </Card>
  );
}
