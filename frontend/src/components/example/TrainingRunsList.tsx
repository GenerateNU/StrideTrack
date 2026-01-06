/**
 * Training Runs List Component
 * Mirrors: backend/app/routes/example_routes.py
 * UI component that displays and manages training runs
 */

import { useState } from 'react';
import {
  useGetAllTrainingRuns,
  useCreateTrainingRun,
  useUpdateTrainingRun,
  useDeleteTrainingRun,
} from '@/hooks/useExampleTrainingRuns';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { TrainingRunForm } from './TrainingRunForm';
import type { TrainingRunCreate, TrainingRunResponse } from '@/types/example_types';

export function TrainingRunsList() {
  const { runs, loading, error, refetch } = useGetAllTrainingRuns();
  const { create, loading: creating } = useCreateTrainingRun();
  const { update, loading: updating } = useUpdateTrainingRun();
  const { remove, loading: deleting } = useDeleteTrainingRun();

  const [showForm, setShowForm] = useState(false);
  const [editingRun, setEditingRun] = useState<TrainingRunResponse | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [runToDelete, setRunToDelete] = useState<string | null>(null);

  const handleCreate = async (data: TrainingRunCreate) => {
    await create(data);
    setShowForm(false);
    refetch();
  };

  const handleUpdate = async (data: TrainingRunCreate) => {
    if (editingRun) {
      await update(editingRun.id, data);
      setEditingRun(null);
      refetch();
    }
  };

  const handleDeleteClick = (id: string) => {
    setRunToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (runToDelete) {
      await remove(runToDelete);
      setRunToDelete(null);
      setDeleteDialogOpen(false);
      refetch();
    }
  };

  const handleEdit = (run: TrainingRunResponse) => {
    setEditingRun(run);
    setShowForm(true);
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDistance = (meters: number) => {
    if (meters >= 1000) {
      return `${(meters / 1000).toFixed(2)} km`;
    }
    return `${meters} m`;
  };

  if (loading) {
    return (
      <div className="p-8">
        <p className="text-muted-foreground">Loading training runs...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 space-y-4">
        <p className="text-destructive">Error: {error}</p>
        <Button onClick={refetch} variant="outline">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Training Runs</h2>
        <Button
          onClick={() => {
            setEditingRun(null);
            setShowForm(true);
          }}
        >
          + Add Training Run
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>
              {editingRun ? 'Edit Training Run' : 'Create Training Run'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TrainingRunForm
              initialData={editingRun || undefined}
              onSubmit={editingRun ? handleUpdate : handleCreate}
              onCancel={() => {
                setShowForm(false);
                setEditingRun(null);
              }}
              isLoading={creating || updating}
              submitLabel={editingRun ? 'Update' : 'Create'}
            />
          </CardContent>
        </Card>
      )}

      {runs.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center">
              No training runs found. Create your first one!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {runs.map((run) => (
            <Card key={run.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{run.athlete_name}</CardTitle>
                    <div className="mt-2 space-y-1 text-sm text-muted-foreground">
                      <p>Distance: {formatDistance(run.distance_meters)}</p>
                      <p>Duration: {formatDuration(run.duration_seconds)}</p>
                      {run.avg_ground_contact_time_ms && (
                        <p>
                          Avg GCT: {run.avg_ground_contact_time_ms.toFixed(1)} ms
                        </p>
                      )}
                      <p className="text-xs">
                        Created: {new Date(run.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(run)}
                      disabled={updating || deleting}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteClick(run.id)}
                      disabled={deleting}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Training Run</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this training run? This action
              cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleting}
            >
              {deleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
