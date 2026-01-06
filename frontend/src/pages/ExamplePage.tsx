/**
 * Example Page Component
 * Page that displays the training runs list
 */

import { TrainingRunsList } from '../components/example/TrainingRunsList';

export function ExamplePage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="container mx-auto">
        <TrainingRunsList />
      </div>
    </div>
  );
}

