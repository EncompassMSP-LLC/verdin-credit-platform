import { z } from 'zod';

export const userRoleSchema = z.enum([
  'owner',
  'admin',
  'case_manager',
  'reviewer',
  'read_only',
]);

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const refreshTokenSchema = z.object({
  refresh_token: z.string().min(1, 'Refresh token is required'),
});

export const createUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  first_name: z.string().min(1).max(100),
  last_name: z.string().min(1).max(100),
  role: userRoleSchema.default('read_only'),
  organization_id: z.string().uuid().optional(),
});

export const caseStatusSchema = z.enum(['open', 'in_review', 'closed', 'archived']);

export const createCaseSchema = z.object({
  title: z.string().min(1).max(255),
  description: z.string().optional(),
  account_id: z.string().uuid().optional(),
  assigned_to_id: z.string().uuid().optional(),
});

export const paginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  page_size: z.coerce.number().int().min(1).max(100).default(20),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RefreshTokenInput = z.infer<typeof refreshTokenSchema>;
export type CreateUserInput = z.infer<typeof createUserSchema>;
export type CreateCaseInput = z.infer<typeof createCaseSchema>;
export type PaginationInput = z.infer<typeof paginationSchema>;
