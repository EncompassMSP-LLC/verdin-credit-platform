# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## System

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | Public | Health check |
| GET | `/version` | Public | API version |

## Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | Public | Login with email/password |
| POST | `/auth/refresh` | Public | Refresh access token |
| GET | `/auth/me` | Required | Get current user |

### Login

```json
POST /api/v1/auth/login
{
  "email": "owner@verdin.demo",
  "password": "changeme123"
}
```

Response:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Refresh Token

```json
POST /api/v1/auth/refresh
{
  "refresh_token": "eyJ..."
}
```

### Current User

```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

| Status | Meaning |
|--------|---------|
| 401 | Invalid or missing authentication |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (e.g., duplicate email) |
| 422 | Validation error |
