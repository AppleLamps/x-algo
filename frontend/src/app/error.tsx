'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-white py-20 px-4 flex items-center justify-center">
      <Card className="max-w-2xl w-full shadow-2xl border border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-red-900">
            Something went wrong!
          </CardTitle>
          <CardDescription className="text-lg text-red-700">
            An unexpected error occurred while processing your request.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-white p-4 rounded-lg border border-red-300">
            <p className="text-sm text-gray-700 font-mono">
              {error.message || 'Unknown error'}
            </p>
          </div>
          <Button onClick={reset} className="w-full bg-red-600 hover:bg-red-700 text-white">
            Try Again
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

