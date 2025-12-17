/**
 * Login page with email/password and OAuth options.
 */

import { BookOpen } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LoginForm, OAuthButtons } from '@/components/auth';
import { useRedirectIfAuthenticated, useAuthInit } from '@/lib/hooks/useAuth';

export function LoginPage() {
  // Initialize auth and check OAuth providers
  useAuthInit();

  // Redirect if already authenticated
  useRedirectIfAuthenticated();

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-2">
            <BookOpen className="h-10 w-10 text-primary" />
          </div>
          <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
          <CardDescription>
            Sign in to your account to continue
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* OAuth buttons */}
          <OAuthButtons />

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Or continue with email
              </span>
            </div>
          </div>

          {/* Login form */}
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  );
}
