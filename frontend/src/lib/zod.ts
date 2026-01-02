import { z } from "zod";

export const serviceObj = z.object({
  name: z.string().min(1, "Service name is required"),
  category: z.string().min(1, "Category is required"),
  description: z.string().min(1, "Description is required"),
});

export const citizenObj = z.object({
  name: z.string().min(1),
  status: z.string().min(1),
  number: z.number().min(1000000000).max(9999999999),
});

export type CitizenType = z.infer<typeof citizenObj>;
