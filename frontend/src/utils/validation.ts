import { z } from 'zod';

export function validateResponse<T>(
  data: unknown,
  schema: z.ZodSchema<T>
): T {
  const result = schema.safeParse(data);
  
  if (!result.success) {
    console.error('Validation error:', result.error);
    throw new Error('Invalid response format from server');
  }
  
  return result.data;
}

