import { z } from "zod";

export const feedbackResponseSchema = z.object({
  feedback: z.string(),
});

export type FeedbackResponse = z.infer<typeof feedbackResponseSchema>;
