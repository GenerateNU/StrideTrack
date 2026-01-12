import { useState } from "react";
import {
  useGetAllTrainingRuns,
  useCreateTrainingRun,
  useUpdateTrainingRun,
  useDeleteTrainingRun,
} from "@/hooks/exampleTrainingRuns.hooks";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TrainingRunForm } from "./TrainingRunForm";
import type {
  TrainingRunCreate,
  TrainingRunResponse,
} from "@/types/example.types";
import { formatDuration, formatDistance } from "@/utils/format";

export function TrainingRunsList() {
  const {
    trainingRuns,
    trainingRunsIsLoading,
    trainingRunsError,
    trainingRunsRefetch,
  } = useGetAllTrainingRuns();
  const { createTrainingRun, createTrainingRunIsLoading } =
    useCreateTrainingRun();
  const { updateTrainingRun, updateTrainingRunIsLoading } =
    useUpdateTrainingRun();
  const { deleteTrainingRun, deleteTrainingRunIsLoading } =
    useDeleteTrainingRun();

  const [showForm, setShowForm] = useState(false);
  const [editingRun, setEditingRun] = useState<TrainingRunResponse | null>(
    null
  );
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [runToDelete, setRunToDelete] = useState<string | null>(null);

  const handleCreate = async (data: TrainingRunCreate) => {
    await createTrainingRun(data);
    setShowForm(false);
  };

  const handleUpdate = async (data: TrainingRunCreate) => {
    if (editingRun) {
      await updateTrainingRun({ id: editingRun.id, data });
      setEditingRun(null);
      setShowForm(false);
    }
  };

  const handleDeleteClick = (id: string) => {
    setRunToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (runToDelete) {
      await deleteTrainingRun(runToDelete);
      setRunToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  const handleEdit = (run: TrainingRunResponse) => {
    setEditingRun(run);
    setShowForm(true);
  };

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
              {editingRun ? "Edit Training Run" : "Create Training Run"}
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
              isLoading={
                createTrainingRunIsLoading || updateTrainingRunIsLoading
              }
              submitLabel={editingRun ? "Update" : "Create"}
            />
          </CardContent>
        </Card>
      )}

      {trainingRunsIsLoading ? (
        <div className="h-64">
          <QueryLoading />
        </div>
      ) : trainingRunsError ? (
        <QueryError error={trainingRunsError} refetch={trainingRunsRefetch} />
      ) : trainingRuns.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center">
              No training runs found. Create your first one!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {trainingRuns.map((run) => (
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
                          Avg GCT: {run.avg_ground_contact_time_ms.toFixed(1)}{" "}
                          ms
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
                      disabled={
                        updateTrainingRunIsLoading || deleteTrainingRunIsLoading
                      }
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteClick(run.id)}
                      disabled={deleteTrainingRunIsLoading}
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
              disabled={deleteTrainingRunIsLoading}
            >
              {deleteTrainingRunIsLoading ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
