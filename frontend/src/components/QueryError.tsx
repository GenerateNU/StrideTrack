import { AlertCircle, RefreshCw } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface QueryErrorProps {
  error: Error;
  refetch: () => void;
}

export function QueryError({ error, refetch }: QueryErrorProps) {
  return (
    <Card className="w-full">
      <CardContent className="flex flex-col items-center gap-4 p-6">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <div className="text-center space-y-2">
          <p className="font-medium text-destructive">Something went wrong</p>
          <div className="max-h-32 overflow-y-auto">
            <p className="text-sm text-muted-foreground">{error.message}</p>
          </div>
        </div>
        <Button onClick={refetch} variant="outline" className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Retry
        </Button>
      </CardContent>
    </Card>
  );
}
