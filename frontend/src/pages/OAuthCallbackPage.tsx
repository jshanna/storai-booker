/**
 * OAuth callback page that handles the redirect from OAuth providers.
 */

import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useOAuth } from '@/lib/hooks/useAuth';

export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { handleCallback } = useOAuth();
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const errorParam = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      // Check for OAuth error
      if (errorParam) {
        setError(errorDescription || errorParam);
        setIsProcessing(false);
        return;
      }

      // Validate required parameters
      if (!code || !state) {
        setError('Missing required OAuth parameters');
        setIsProcessing(false);
        return;
      }

      // Get stored provider
      const storedProvider = sessionStorage.getItem('oauth_provider') as 'google' | 'github' | null;
      if (!storedProvider) {
        setError('OAuth session expired. Please try again.');
        setIsProcessing(false);
        return;
      }

      try {
        await handleCallback(storedProvider, code, state);
        // Redirect to home on success
        navigate('/', { replace: true });
      } catch (err: any) {
        setError(err.message || 'Failed to complete authentication');
        setIsProcessing(false);
      }
    };

    processCallback();
  }, [searchParams, handleCallback, navigate]);

  if (isProcessing) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2">
              <Loader2 className="h-5 w-5 animate-spin" />
              Processing
            </CardTitle>
            <CardDescription>
              Completing your sign in...
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            Authentication Failed
          </CardTitle>
          <CardDescription>
            We couldn't complete your sign in
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>

          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => navigate('/login')}
            >
              Back to Login
            </Button>
            <Button
              className="flex-1"
              onClick={() => navigate('/register')}
            >
              Create Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
