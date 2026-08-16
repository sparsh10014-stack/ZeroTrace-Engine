# ZeroTrace QA Test Report

## API Endpoint

POST /verify

## Test Cases

| ID | Test | Expected | Result |
|---|---|---|---|
| API-001 | Empty request | 400 | PASS |
| API-002 | Missing proof | 400 | PASS |
| API-003 | Missing public signals | 400 | PASS |
| API-004 | Valid proof | 200 + valid=true | PENDING |
| API-005 | Invalid proof | 400 + valid=false | PENDING |
| API-006 | Wrong verification key | 400 | PENDING |
| API-007 | Malformed JSON | 400 | PENDING |
| API-008 | GET /verify | 405 | PASS |
| API-009 | Unknown endpoint | 404 | PASS |

## Database Tests

| Test | Expected |
|---|---|
| Exactly 3 columns | PASS |
| PASS logging | PASS |
| FAIL logging | PASS |
| Timestamp generated | PASS |
| No personal data columns | PASS |

## Privacy Verification

The verification_logs table contains only:

- Log_ID
- Timestamp
- Status

No names, ages, locations, phone numbers, emails, or government identifiers are stored.