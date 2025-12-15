/**
 * Reader page - book-style story reader (placeholder).
 */

import { useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function ReaderPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Story Reader</CardTitle>
          <CardDescription>
            Reading story: {id}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Book-style reader with page flipping will be implemented in Phase 4.5
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
