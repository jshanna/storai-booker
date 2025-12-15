/**
 * Step 3: Characters (dynamic add/remove list).
 */

import { UseFormReturn, useFieldArray } from 'react-hook-form';
import { Plus, Trash2 } from 'lucide-react';
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { StoryGenerationFormData } from '@/lib/schemas/story';

interface CharactersStepProps {
  form: UseFormReturn<StoryGenerationFormData>;
}

export function CharactersStep({ form }: CharactersStepProps) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'characters' as never,
  });

  const handleAddCharacter = () => {
    if (fields.length < 10) {
      append('' as never);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Characters</h3>
        <p className="text-sm text-muted-foreground">
          Add the main characters for your story (1-10 characters)
        </p>
      </div>

      <div className="space-y-4">
        {fields.map((field, index) => (
          <FormField
            key={field.id}
            control={form.control}
            name={`characters.${index}`}
            render={({ field: inputField }) => (
              <FormItem>
                <FormLabel className="sr-only">Character {index + 1}</FormLabel>
                <div className="flex gap-2">
                  <FormControl>
                    <Input
                      placeholder={`Character ${index + 1} (e.g., "Hazel the brave squirrel")`}
                      {...inputField}
                    />
                  </FormControl>
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => remove(index)}
                    disabled={fields.length === 1}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <FormMessage />
              </FormItem>
            )}
          />
        ))}
      </div>

      <Button
        type="button"
        variant="outline"
        onClick={handleAddCharacter}
        disabled={fields.length >= 10}
        className="w-full"
      >
        <Plus className="mr-2 h-4 w-4" />
        Add Character
      </Button>

      <FormDescription>
        You have {fields.length} of 10 characters
      </FormDescription>
    </div>
  );
}
