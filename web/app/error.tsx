'use client';

import { useEffect } from 'react';
import { Button } from '@/shared/components/ui/button';
import { AlertTriangle, RefreshCcw, Home } from 'lucide-react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error('Global Error Boundary caught:', error);
    }, [error]);

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <div className="max-w-md w-full text-center space-y-6 animate-in fade-in zoom-in duration-300">
                <div className="flex justify-center">
                    <div className="p-4 bg-destructive/10 rounded-full">
                        <AlertTriangle className="w-12 h-12 text-destructive" />
                    </div>
                </div>

                <div className="space-y-2">
                    <h1 className="text-3xl font-black tracking-tighter">Something went wrong</h1>
                    <p className="text-muted-foreground">
                        An unexpected error occurred. We&apos;ve been notified and are looking into it.
                    </p>
                </div>

                {error.digest && (
                    <div className="p-2 bg-muted rounded-md text-[10px] font-mono text-muted-foreground">
                        Error ID: {error.digest}
                    </div>
                )}

                <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
                    <Button
                        onClick={() => reset()}
                        variant="default"
                        className="font-bold flex items-center gap-2"
                    >
                        <RefreshCcw size={16} />
                        Try again
                    </Button>
                    <Button
                        onClick={() => window.location.href = '/'}
                        variant="outline"
                        className="font-bold flex items-center gap-2"
                    >
                        <Home size={16} />
                        Go home
                    </Button>
                </div>
            </div>
        </div>
    );
}
