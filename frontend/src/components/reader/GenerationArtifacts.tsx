/**
 * Dialog showing generation artifacts including character sheets and prompts.
 */

import * as React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Users, Sparkles } from 'lucide-react';
import type { Story } from '@/types/api';

interface GenerationArtifactsProps {
  story: Story;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  trigger?: React.ReactNode;
}

export function GenerationArtifacts({ story, open, onOpenChange, trigger }: GenerationArtifactsProps) {
  const hasCharacterSheets = story.metadata.character_sheet_urls && story.metadata.character_sheet_urls.length > 0;
  const hasPagePrompts = story.pages.some(page => page.illustration_prompt);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {trigger && (
        <DialogTrigger asChild>
          {trigger}
        </DialogTrigger>
      )}
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>Generation Artifacts</DialogTitle>
          <DialogDescription>
            View character reference sheets and generation prompts for "{story.title}"
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="characters" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="characters" disabled={!hasCharacterSheets}>
              <Users className="h-4 w-4 mr-2" />
              Character Sheets
            </TabsTrigger>
            <TabsTrigger value="prompts" disabled={!hasPagePrompts}>
              <FileText className="h-4 w-4 mr-2" />
              Page Prompts
            </TabsTrigger>
          </TabsList>

          <TabsContent value="characters" className="mt-4">
            {hasCharacterSheets ? (
              <ScrollArea className="h-[60vh]">
                <div className="space-y-6">
                  {story.metadata.character_sheet_urls.map((url, idx) => {
                    const character = story.metadata.character_descriptions[idx];
                    return (
                      <div key={idx} className="space-y-2">
                        {character && (
                          <div className="space-y-1">
                            <h3 className="text-lg font-semibold">{character.name}</h3>
                            <p className="text-sm text-muted-foreground">
                              <span className="font-medium">Role:</span> {character.role}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              <span className="font-medium">Description:</span> {character.physical_description}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              <span className="font-medium">Personality:</span> {character.personality}
                            </p>
                          </div>
                        )}
                        <div className="rounded-lg border overflow-hidden bg-muted">
                          <img
                            src={url}
                            alt={`Character sheet for ${character?.name || `Character ${idx + 1}`}`}
                            className="w-full h-auto"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            ) : (
              <div className="flex flex-col items-center justify-center h-[40vh] text-muted-foreground">
                <Users className="h-12 w-12 mb-2" />
                <p>No character sheets available</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="prompts" className="mt-4">
            {hasPagePrompts ? (
              <ScrollArea className="h-[60vh]">
                <div className="space-y-4">
                  {story.pages.map((page) => (
                    <div key={page.page_number} className="space-y-2">
                      <h3 className="text-sm font-semibold">
                        Page {page.page_number}
                        {page.text && (
                          <span className="ml-2 text-xs text-muted-foreground font-normal">
                            ({page.generation_attempts} {page.generation_attempts === 1 ? 'attempt' : 'attempts'})
                          </span>
                        )}
                      </h3>
                      {page.text && (
                        <div className="rounded-md bg-muted p-3 mb-2">
                          <p className="text-xs font-medium text-muted-foreground mb-1">Story Text:</p>
                          <p className="text-sm">{page.text}</p>
                        </div>
                      )}
                      {page.illustration_prompt && (
                        <div className="rounded-md bg-muted p-3">
                          <p className="text-xs font-medium text-muted-foreground mb-1">Illustration Prompt:</p>
                          <p className="text-sm font-mono">{page.illustration_prompt}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            ) : (
              <div className="flex flex-col items-center justify-center h-[40vh] text-muted-foreground">
                <FileText className="h-12 w-12 mb-2" />
                <p>No page prompts available</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
