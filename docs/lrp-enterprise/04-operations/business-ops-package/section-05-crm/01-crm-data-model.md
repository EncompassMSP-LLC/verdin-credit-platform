# LRP CRM Data Model

**Document owner:** Operations
**Applies to:** Lending Readiness Partners partner-development and referral operations
**System of record:** Shared Lending Readiness Platform monorepo
**Status:** Operational specification

## 1. Purpose

This model defines the minimum CRM records needed to manage mortgage companies, loan officers, Realtors, attorneys, financial planners, insurance agents, builders, and title companies without creating a separate product fork or duplicate shadow database.

The CRM must support four business outcomes:

1. Identify and qualify prospective referral partners.
2. preserve the relationship between a partner organization, its contacts, and referred borrowers.
3. Assign accountable owners and next actions.
4. Produce auditable reporting without exposing borrower information beyond authorized roles.

## 2. Core entities

### 2.1 PartnerOrganization

Represents the company, office, branch, firm, brokerage, agency, builder, or title operation.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| organization_id | UUID | Yes | Immutable internal identifier |
| legal_name | Text | Yes | Registered or contracted name |
| display_name | Text | Yes | Name used in UI and reports |
| organization_type | Enum | Yes | `MORTGAGE_COMPANY`, `CREDIT_UNION`, `BANK`, `REAL_ESTATE_BROKERAGE`, `LAW_FIRM`, `FINANCIAL_PLANNING_FIRM`, `INSURANCE_AGENCY`, `BUILDER`, `TITLE_COMPANY`, `OTHER` |
| parent_organization_id | UUID | No | Supports corporate parent / branch hierarchy |
| nmls_id | Text | Conditional | Store only when relevant and verified |
| website | URL | No | Public website |
| main_phone | Text | No | Normalized E.164 where possible |
| address_line_1 | Text | No | Business address |
| address_line_2 | Text | No | Suite or unit |
| city | Text | No |  |
| state | Text | No | Two-letter state code |
| postal_code | Text | No |  |
| service_area | Text array | No | States, counties, or markets served |
| lifecycle_stage | Enum | Yes | See Section 4 below |
| relationship_status | Enum | Yes | `PROSPECT`, `ACTIVE_PARTNER`, `PAUSED`, `INACTIVE`, `DO_NOT_CONTACT` |
| assigned_owner_user_id | UUID | Yes | Internal accountable owner |
| source | Enum | Yes | `OUTBOUND`, `INBOUND`, `REFERRAL`, `EVENT`, `WEBSITE`, `EXISTING_NETWORK`, `OTHER` |
| source_detail | Text | No | Campaign, event, or referrer detail |
| last_activity_at | Timestamp | No | Derived from logged activities |
| next_action_at | Timestamp | No | Required for active prospects |
| risk_flags | Text array | No | Compliance, duplicate, complaint, or relationship flags |
| created_at | Timestamp | Yes | System generated |
| updated_at | Timestamp | Yes | System generated |
| archived_at | Timestamp | No | Soft deletion only |

### 2.2 PartnerContact

Represents a person associated with a partner organization.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| contact_id | UUID | Yes | Immutable internal identifier |
| organization_id | UUID | Yes | Parent partner organization |
| first_name | Text | Yes |  |
| last_name | Text | Yes |  |
| job_title | Text | No |  |
| contact_role | Enum | Yes | `LOAN_OFFICER`, `BRANCH_MANAGER`, `BROKER_OWNER`, `REALTOR`, `ATTORNEY`, `FINANCIAL_PLANNER`, `INSURANCE_AGENT`, `BUILDER_REP`, `TITLE_REP`, `OPERATIONS`, `EXECUTIVE`, `OTHER` |
| email | Email | Conditional | Required when email outreach is used |
| mobile_phone | Text | No | Consent rules apply before SMS |
| office_phone | Text | No |  |
| nmls_id | Text | Conditional | Relevant for licensed mortgage contacts |
| license_state_codes | Text array | No | Verified states only |
| preferred_channel | Enum | No | `EMAIL`, `PHONE`, `SMS`, `PORTAL`, `NONE` |
| communication_consent_status | Enum | Yes | `UNKNOWN`, `BUSINESS_CONTACT_ONLY`, `OPTED_IN`, `OPTED_OUT`, `DO_NOT_CONTACT` |
| email_opt_out_at | Timestamp | No |  |
| sms_opt_in_at | Timestamp | No | Evidence reference required |
| sms_opt_out_at | Timestamp | No |  |
| relationship_status | Enum | Yes | `PROSPECT`, `ACTIVE`, `PAUSED`, `INACTIVE`, `DO_NOT_CONTACT` |
| assigned_owner_user_id | UUID | Yes | Internal owner |
| last_activity_at | Timestamp | No | Derived |
| next_action_at | Timestamp | No |  |
| created_at | Timestamp | Yes | System generated |
| updated_at | Timestamp | Yes | System generated |
| archived_at | Timestamp | No | Soft deletion only |

### 2.3 PartnerRelationship

Captures the commercial and operational relationship, separate from organization identity.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| relationship_id | UUID | Yes | Immutable identifier |
| organization_id | UUID | Yes | Partner organization |
| relationship_type | Enum | Yes | `REFERRAL_PARTNER`, `CO_MARKETING_PARTNER`, `EDUCATION_PARTNER`, `VENDOR`, `STRATEGIC_ALLIANCE` |
| effective_date | Date | No | After agreement approval |
| termination_date | Date | No |  |
| agreement_status | Enum | Yes | `NOT_REQUIRED`, `DRAFT`, `COUNSEL_REVIEW`, `PENDING_SIGNATURE`, `ACTIVE`, `EXPIRED`, `TERMINATED` |
| agreement_document_id | UUID | No | Secure document reference |
| primary_contact_id | UUID | No |  |
| internal_owner_user_id | UUID | Yes |  |
| referral_method | Enum | No | `PORTAL`, `SECURE_FORM`, `PHONE_HANDOFF`, `OTHER_APPROVED` |
| reporting_cadence | Enum | No | `MILESTONE`, `WEEKLY`, `MONTHLY`, `NONE` |
| notes | Text | No | No unnecessary borrower PII |
| created_at | Timestamp | Yes |  |
| updated_at | Timestamp | Yes |  |

### 2.4 PartnerActivity

Every meaningful touchpoint must be logged.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| activity_id | UUID | Yes |  |
| organization_id | UUID | Yes |  |
| contact_id | UUID | No |  |
| activity_type | Enum | Yes | `CALL`, `EMAIL`, `MEETING`, `VOICEMAIL`, `SMS`, `PORTAL_MESSAGE`, `EVENT`, `NOTE`, `TASK`, `AGREEMENT_CHANGE`, `REFERRAL_RECEIVED` |
| direction | Enum | Yes | `INBOUND`, `OUTBOUND`, `INTERNAL` |
| occurred_at | Timestamp | Yes |  |
| subject | Text | Yes | Short operational summary |
| outcome | Enum | No | `CONNECTED`, `NO_ANSWER`, `LEFT_MESSAGE`, `MEETING_BOOKED`, `FOLLOW_UP_REQUIRED`, `DECLINED`, `COMPLETED`, `OTHER` |
| next_action_at | Timestamp | No | Required when follow-up is needed |
| created_by_user_id | UUID | Yes |  |
| visibility | Enum | Yes | `INTERNAL`, `PARTNER_SAFE`, `RESTRICTED` |
| content | Text | No | Avoid sensitive borrower detail |
| created_at | Timestamp | Yes |  |

### 2.5 PartnerReferralLink

Links the CRM relationship to the existing referral and loan-readiness workflow.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| partner_referral_link_id | UUID | Yes |  |
| relationship_id | UUID | Yes | Active or approved relationship |
| organization_id | UUID | Yes | Denormalized for reporting |
| contact_id | UUID | No | Referring contact |
| referral_id | UUID | Yes | Existing referral record from Section 4 |
| loan_pipeline_id | UUID | No | Existing platform pipeline record |
| attribution_source | Enum | Yes | `DIRECT_CONTACT`, `ORGANIZATION`, `CAMPAIGN`, `EVENT`, `OTHER` |
| attribution_campaign | Text | No |  |
| referred_at | Timestamp | Yes |  |
| created_at | Timestamp | Yes |  |

Borrower PII remains on borrower/referral records. The CRM should reference those records by identifier and role-aware links, not duplicate sensitive data into partner notes.

## 3. Partner-type views

The following are filtered views over the same entities, not separate databases:

- Mortgage company database: `organization_type` in bank, credit union, or mortgage company.
- Loan officer database: `contact_role = LOAN_OFFICER`.
- Realtor database: brokerage organizations and `contact_role = REALTOR`.
- Attorney database: law firms and attorney contacts.
- Financial planner database: planning firms and planner contacts.
- Insurance agent database: agencies and agent contacts.
- Builder database: builder organizations and builder representatives.
- Title company database: title organizations and title representatives.

## 4. Lifecycle stages

| Stage | Definition | Entry requirement | Exit requirement |
| --- | --- | --- | --- |
| TARGET | Identified but not contacted | Basic organization/contact record | First outreach logged |
| CONTACTED | Initial outreach completed | Activity logged | Response or follow-up sequence decision |
| ENGAGED | Two-way communication established | Verified response | Discovery meeting or disqualification |
| DISCOVERY | Needs and fit being assessed | Meeting scheduled or held | Qualified, nurture, or closed-lost decision |
| QUALIFIED | Meets partner profile and compliance gates | Owner approval | Agreement/onboarding started |
| ONBOARDING | Operational setup underway | Welcome process initiated | Training and referral path activated |
| ACTIVE_PARTNER | Approved to refer and receive allowed updates | Required agreement/controls active | Pause, inactivity, or termination |
| NURTURE | Valid future opportunity, not currently active | Reason and next review date | Re-engagement or closure |
| PAUSED | Temporarily suspended | Pause reason documented | Reactivation or termination |
| CLOSED_LOST | Not proceeding | Loss reason documented | Reopen only with owner approval |
| DO_NOT_CONTACT | No outreach permitted | Opt-out, legal, or policy reason | Compliance-approved removal only |

## 5. Required deduplication keys

Automated and manual duplicate checks should use:

1. Exact normalized organization legal name plus postal code.
2. Verified domain name.
3. NMLS identifier when applicable.
4. Exact normalized email for contacts.
5. Normalized phone number plus contact name.

Potential duplicates are queued for review. Records are merged only by authorized users, with a retained audit record of source IDs and field decisions.

## 6. Role and visibility rules

- Partner-development users may view partner organizations, contacts, activities, and aggregate referral metrics.
- Loan officers and external partners may view only their authorized organization, contacts, referrals, and approved status summaries.
- Borrower notes, credit details, identity documents, and dispute evidence remain restricted to authorized borrower-service roles.
- Compliance and administrators may review communication consent, opt-outs, complaints, and audit logs.
- Export permissions must be explicit and logged.

## 7. Data quality controls

- Every active prospect must have an assigned owner and next action date.
- Every active partner must have a primary contact and approved referral method.
- Every contact must have a communication consent status.
- No borrower Social Security number, full date of birth, credit report, or identity document may be pasted into CRM notes.
- Organization and contact records are archived rather than hard deleted.
- Required fields and validation rules apply equally to manual entry, CSV import, API ingestion, and form submissions.

## 8. Metrics enabled by this model

- Prospects by lifecycle stage and owner.
- Contact-to-discovery and discovery-to-active conversion rates.
- Active partners by organization and partner type.
- Referrals received by organization, contact, campaign, and period.
- Borrowers returned to lender by source.
- Stale records with no activity or overdue next action.
- Opt-out and do-not-contact counts.
- Duplicate rate and unresolved data-quality exceptions.
