import { z } from 'zod';

export const userRoleSchema = z.enum(['owner', 'admin', 'case_manager', 'reviewer', 'read_only']);

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

export const caseStatusSchema = z.enum(['open', 'active', 'on_hold', 'resolved', 'closed']);

export const caseStageSchema = z.enum([
  'intake',
  'review',
  'evidence_gathering',
  'dispute_preparation',
  'awaiting_response',
  'monitoring',
  'complete',
]);

export const casePrioritySchema = z.enum(['low', 'medium', 'high', 'critical']);

export const createCaseSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  client_name: z.string().min(1, 'Client name is required').max(255),
  client_email: z.string().email('Invalid email').optional().or(z.literal('')),
  case_number: z.string().max(50).optional(),
  status: caseStatusSchema.default('open'),
  stage: caseStageSchema.default('intake'),
  priority: casePrioritySchema.default('medium'),
  assigned_user_id: z.string().uuid().optional().nullable(),
  summary: z.string().optional(),
  notes: z.string().optional(),
});

export const updateCaseSchema = createCaseSchema.partial();

export const paginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  page_size: z.coerce.number().int().min(1).max(100).default(20),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RefreshTokenInput = z.infer<typeof refreshTokenSchema>;
export type CreateUserInput = z.infer<typeof createUserSchema>;
export type CreateCaseInput = z.infer<typeof createCaseSchema>;
export type UpdateCaseInput = z.infer<typeof updateCaseSchema>;
export type PaginationInput = z.infer<typeof paginationSchema>;
