# Authentication

## Overview

Verdin uses JWT (JSON Web Tokens) for stateless authentication with refresh token rotation.

## Token Types

| Token         | Lifetime   | Purpose                  |
| ------------- | ---------- | ------------------------ |
| Access Token  | 30 minutes | API authorization        |
| Refresh Token | 7 days     | Obtain new access tokens |

## Flow

```
1. Client → POST /auth/login (email + password)
2. Server → Returns access_token + refresh_token
3. Client → Includes access_token in Authorization header
4. On expiry → POST /auth/refresh with refresh_token
5. Server → Returns new token pair
```

## Role-Based Access Control

| Role         | Level | Permissions                |
| ------------ | ----- | -------------------------- |
| Owner        | 5     | Full platform access       |
| Admin        | 4     | Organization management    |
| Case Manager | 3     | Case CRUD, task assignment |
| Reviewer     | 2     | Read cases, add reviews    |
| Read Only    | 1     | View-only access           |

Higher roles inherit permissions of lower roles.

## Implementation

- Passwords hashed with bcrypt via passlib
- Tokens signed with HS256
- Secret key from `SECRET_KEY` environment variable
- Protected endpoints use `get_current_user` dependency
- Role-gated endpoints use `require_role(UserRole.ADMIN)` etc.

## Public Endpoints

These endpoints do not require authentication:

- `GET /api/v1/health`
- `GET /api/v1/version`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

All other endpoints require a valid Bearer token.
