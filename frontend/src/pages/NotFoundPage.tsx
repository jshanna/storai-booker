/**
 * 404 Not Found page.
 */

import { Link } from 'react-router-dom';
import { FileQuestion } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/shared';

export function NotFoundPage() {
  return (
    <EmptyState
      icon={FileQuestion}
      title="Page Not Found"
      description="The page you're looking for doesn't exist or has been moved."
    >
      <Button asChild className="mt-4">
        <Link to="/">Go Home</Link>
      </Button>
    </EmptyState>
  );
}
