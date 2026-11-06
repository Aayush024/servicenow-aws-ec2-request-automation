# Setup and Testing Guide

## Prerequisites

- ServiceNow development instance with access to Service Catalog, approvals, Flow Designer, and REST Messages.
- AWS account with API Gateway, Lambda, CloudWatch, and permissions to inspect the deployed integration.
- Existing working integration configured with the project's authentication method.

## ServiceNow Configuration Checklist

1. Confirm the catalog item collects `server_name`, `environment`, and `instance_type`.
2. Confirm the approval flow is connected to the correct Requested Item and that rejection stops the AWS action.
3. Confirm the custom Flow Designer action maps its inputs to the REST Message payload.
4. Confirm REST authentication is configured through a secure credential mechanism; do not hardcode tokens.
5. Confirm the REST response is parsed and mapped to RITM work notes or a status field.
6. If the UI displays request state, verify the state transitions reflect the actual workflow rather than only the approval label.

## AWS Configuration Checklist

1. Inspect the API Gateway route and attached Lambda authorizer.
2. Inspect the validation Lambda's request checks and enforce `dry_run` server-side.
3. Confirm the validation Lambda has no unnecessary EC2 creation privileges.
4. Review CloudWatch logs for successful and failed calls without exposing secrets.

## End-to-End Test Plan

1. Submit a catalog request using harmless test values.
2. Confirm the RITM exists and is awaiting approval.
3. Approve it and confirm the approved branch executes exactly once.
4. Verify the AWS API returns `200` and `instance_created: false`.
5. Verify ServiceNow records the response in the correct RITM.
6. Submit a second request and reject it; confirm no outbound AWS call occurs.
7. Test an invalid credential; confirm API authorization fails.
8. Attempt a request with `dry_run: false`; confirm no instance is created and the backend enforces validation-only mode.
9. Review logs and capture sanitized screenshots.

## Troubleshooting

| Symptom | Check |
|---|---|
| 401 Unauthorized | Authorizer credential, request header, token/secret configuration |
| 403 Forbidden | API policy, authorizer result, route authorization settings |
| 4xx input error | Variable mapping, required fields, JSON serialization |
| 5xx API error | Lambda exception, integration response, CloudWatch logs |
| RITM unchanged | Flow execution, output mappings, work-note update step |
| Flow not running | Trigger table, conditions, approval outcome, activation |

## Screenshot Hygiene

Blur or crop tokens, authorization headers, secrets, passwords, account IDs, internal usernames/emails, private instance URLs, and personal details. Never publish credential-bearing REST configuration or unredacted logs.
