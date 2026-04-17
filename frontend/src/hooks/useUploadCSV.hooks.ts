import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { UploadCSVPayload } from "@/types/csv.types";

export function useUploadCSV() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async ({ athleteId, eventType, file }: UploadCSVPayload) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("event_type", eventType);

      const response = await api.post(
        `/athletes/${athleteId}/csv/upload-run`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });

  return {
    uploadCSV: mutation.mutateAsync,
    uploadCSVIsLoading: mutation.isPending,
    uploadCSVError: mutation.error,
  };
}
