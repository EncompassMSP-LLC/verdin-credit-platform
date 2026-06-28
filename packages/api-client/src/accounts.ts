import type { PaginatedResponse } from '@verdin/shared';

import { apiPath, notImplemented } from './http';

export interface Account {
  id: string;
  name: string;
  account_number: string | null;
  email: string | null;
  phone: string | null;
  organization_id: string;
  created_at: string;
}

export interface ListAccountsParams {
  page?: number;
  page_size?: number;
}

export async function listAccounts(
  _params: ListAccountsParams = {},
): Promise<PaginatedResponse<Account>> {
  notImplemented(`GET ${apiPath('/accounts')}`);
}

export async function getAccount(_accountId: string): Promise<Account> {
  notImplemented(`GET ${apiPath('/accounts/:id')}`);
}
