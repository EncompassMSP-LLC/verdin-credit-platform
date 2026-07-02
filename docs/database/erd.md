# Database Schema

## Entity Relationship Diagram

```mermaid
erDiagram
    Organization ||--o{ User : has
    Organization ||--o{ Client : has
    Organization ||--o{ Case : has
    Client ||--o{ ClientContact : has
    Client ||--o| ClientPortalUser : "portal login"
    Organization ||--o{ Account : has
    Case ||--o{ Account : "credit tradelines"
    Account ||--o{ DisputeLetter : has
    User ||--o{ Case : "assigned to"
    Case ||--o{ Document : contains
    Case ||--o{ Task : contains
    Case ||--o{ Communication : contains
    Case ||--o{ TimelineEvent : contains
    User ||--o{ Task : "assigned to"
    User ||--o{ Notification : receives
    Organization ||--o{ Notification : has

    Organization {
        uuid id PK
        string name
        string slug UK
        boolean is_active
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    User {
        uuid id PK
        string email UK
        string hashed_password
        string first_name
        string last_name
        enum role
        boolean is_active
        uuid organization_id FK
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    Client {
        uuid id PK
        uuid organization_id FK
        string display_name
        string email
        string phone
        enum status
        text notes
    }

    ClientContact {
        uuid id PK
        uuid organization_id FK
        uuid client_id FK
        string full_name
        string email
        string phone
        enum relationship
        boolean is_primary
        text notes
    }

    ClientPortalUser {
        uuid id PK
        uuid organization_id FK
        uuid client_id FK UK
        string email UK
        string hashed_password
        boolean is_active
        timestamp last_login_at
    }

    Account {
        uuid id PK
        uuid organization_id FK
        uuid case_id FK
        enum bureau
        string creditor_name
        enum account_type
        enum account_status
        enum payment_status
        numeric balance
        enum dispute_status
        int risk_score
        int readiness_score
    }

    DisputeLetter {
        uuid id PK
        uuid organization_id FK
        uuid case_id FK
        uuid account_id FK
        string recipient_type
        enum status
        string template_id
        string subject
        timestamp generated_at
        timestamp sent_at
    }

    Case {
        uuid id PK
        string title
        string client_name
        enum status
        enum stage
        enum priority
        string case_number UK
        uuid organization_id FK
        uuid assigned_to_id FK
    }

    Document {
        uuid id PK
        string title
        string file_name
        string file_path
        string mime_type
        int file_size
        uuid case_id FK
    }

    Task {
        uuid id PK
        string title
        text description
        enum status
        enum priority
        timestamp due_date
        uuid case_id FK
        uuid assigned_to_id FK
    }

    Communication {
        uuid id PK
        string subject
        text body
        string channel
        string direction
        uuid case_id FK
    }

    TimelineEvent {
        uuid id PK
        string event_type
        string title
        text description
        text metadata_json
        timestamp occurred_at
        uuid case_id FK
    }

    Notification {
        uuid id PK
        uuid organization_id FK
        uuid recipient_user_id FK
        string title
        text body
        enum category
        timestamp read_at
        string entity_type
        uuid entity_id
        string source_module
        string action_url
        timestamp created_at
        timestamp updated_at
    }
```

## Conventions

- All tables use UUID primary keys
- All business entities support soft delete (`deleted_at`)
- All entities include audit fields (`created_by_id`, `updated_by_id`)
- All timestamps are UTC with timezone

For authoritative lifecycle and relationship detail, see [Data Model](../architecture/data-model.md).

## Migrations

Migrations are managed with Alembic in `apps/api/alembic/`.

```bash
cd apps/api
alembic upgrade head        # Apply migrations
alembic revision --autogenerate -m "description"  # Create new migration
```
