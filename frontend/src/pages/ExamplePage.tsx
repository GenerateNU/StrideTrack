import { TrainingRunsList } from '../components/example/TrainingRunsList';

export function ExamplePage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto">
        <TrainingRunsList />
      </div>
    </div>
  );
}

