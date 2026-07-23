# Page spec — SMS workspace

| Field       | Value                    |
| ----------- | ------------------------ |
| Page name   | SMS                      |
| Route       | `/crm/sms`               |
| Volume      | 21                       |
| Status      | `draft`                  |
| Actors      | Case managers            |
| Permissions | Comms send + SMS consent |

## 1. Purpose

Consent-gated SMS to borrowers for appointments / doc reminders.

## 2. Entry / exit

- Entered from: nav
- Navigates to: case

## 3. Layout

Consent indicator · templates · thread.

## 4. Fields

| ID      | Label       | Type | Required | Source  | Validation        | PII |
| ------- | ----------- | ---- | -------- | ------- | ----------------- | --- |
| phone   | Phone       | tel  | y        | profile | E.164             | Y   |
| body    | Message     | text | y        | form    | max SMS len       | N   |
| consent | SMS consent | bool | y        | profile | must true to send | N   |

## 5. Actions

| ID   | Control  | Result  | API  | Audit   | Errors         |
| ---- | -------- | ------- | ---- | ------- | -------------- |
| send | Send SMS | enqueue | POST | **yes** | 403 no consent |

## 6. States

No consent lock / provider error / success

## 7. Compliance copy

TCPA-oriented consent; no marketing blasts from this screen in v1.

## 8. Analytics events

`crm_sms_send`

## 9. Open questions

- [x] Live SMS v1 → **defer; UI stub OK** (P2-10)
