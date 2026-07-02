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
  status: caseStatusSchema,
  stage: caseStageSchema,
  priority: casePrioritySchema,
  assigned_user_id: z.string().uuid().optional().nullable(),
  summary: z.string().optional(),
  notes: z.string().optional(),
});

export const updateCaseSchema = createCaseSchema.partial();

export const accountBureauSchema = z.enum([
  'equifax',
  'experian',
  'transunion',
  'innovis',
  'unknown',
]);

export const accountTypeSchema = z.enum([
  'mortgage',
  'auto',
  'credit_card',
  'collection',
  'personal_loan',
  'student_loan',
  'medical',
  'utility',
  'telecom',
  'other',
]);

export const accountStatusSchema = z.enum([
  'open',
  'closed',
  'collection',
  'charge_off',
  'repossession',
  'foreclosure',
  'transferred',
  'paid',
  'settled',
  'deleted',
  'unknown',
]);

export const paymentStatusSchema = z.enum([
  'current',
  'late_30',
  'late_60',
  'late_90',
  'late_120',
  'charge_off',
  'collection',
  'repossession',
  'foreclosure',
  'unknown',
]);

export const createAccountSchema = z.object({
  case_id: z.string().uuid('Case is required'),
  bureau: accountBureauSchema,
  creditor_name: z.string().min(1, 'Creditor name is required').max(255),
  original_creditor: z.string().max(255).optional(),
  account_number_masked: z.string().max(50).optional(),
  account_type: accountTypeSchema,
  account_status: accountStatusSchema,
  payment_status: paymentStatusSchema,
  balance: z.string().optional(),
  past_due_amount: z.string().optional(),
  remarks: z.string().optional(),
});

export const updateAccountSchema = createAccountSchema.omit({ case_id: true }).partial();

export const taskStatusSchema = z.enum(['open', 'in_progress', 'blocked', 'completed', 'canceled']);

export const taskPrioritySchema = z.enum(['low', 'medium', 'high', 'critical']);

export const createTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().optional().nullable(),
  status: taskStatusSchema,
  priority: taskPrioritySchema,
  due_date: z.string().optional().nullable(),
  case_id: z.string().uuid().optional().nullable(),
  account_id: z.string().uuid().optional().nullable(),
  document_id: z.string().uuid().optional().nullable(),
  assigned_user_id: z.string().uuid().optional().nullable(),
  source_module: z.string().max(50).optional().nullable(),
  source_event_id: z.string().uuid().optional().nullable(),
});

export const updateTaskSchema = createTaskSchema.partial();

export const paginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  page_size: z.coerce.number().int().min(1).max(100).default(20),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RefreshTokenInput = z.infer<typeof refreshTokenSchema>;
export type CreateUserInput = z.infer<typeof createUserSchema>;
export type CreateCaseInput = z.infer<typeof createCaseSchema>;
export type UpdateCaseInput = z.infer<typeof updateCaseSchema>;
export type CreateAccountInput = z.infer<typeof createAccountSchema>;
export type UpdateAccountInput = z.infer<typeof updateAccountSchema>;
export type CreateTaskInput = z.infer<typeof createTaskSchema>;
export type UpdateTaskInput = z.infer<typeof updateTaskSchema>;
export type PaginationInput = z.infer<typeof paginationSchema>;

export const clientStatusSchema = z.enum(['active', 'inactive']);

export const contactRelationshipSchema = z.enum([
  'primary',
  'spouse',
  'attorney',
  'authorized',
  'other',
]);

export const createClientSchema = z.object({
  display_name: z.string().min(1, 'Display name is required').max(255),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  phone: z.string().max(50).optional().or(z.literal('')),
  status: clientStatusSchema,
  notes: z.string().optional().or(z.literal('')),
});

export const updateClientSchema = createClientSchema.partial();

export const createClientContactSchema = z.object({
  full_name: z.string().min(1, 'Full name is required').max(255),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  phone: z.string().max(50).optional().or(z.literal('')),
  relationship_type: contactRelationshipSchema,
  is_primary: z.boolean(),
  notes: z.string().optional().or(z.literal('')),
});

export const updateClientContactSchema = createClientContactSchema.partial();

export type CreateClientInput = z.infer<typeof createClientSchema>;
export type UpdateClientInput = z.infer<typeof updateClientSchema>;
export type CreateClientContactInput = z.infer<typeof createClientContactSchema>;
export type UpdateClientContactInput = z.infer<typeof updateClientContactSchema>;
