# Onboarding an existing Bedrock (Classic / AgentCore) Agent into Agent365 with an Entra Agent ID

This document explains how to integrate an existing Amazon Bedrock agent (Classic / AgentCore) into an Agent365 workflow while preserving Microsoft identity (Entra) and telemetry signals. It references the sample SDK layer in `src/bedrockGovernance.js` included in this repo.

**Goals**
- Ensure calls to Bedrock include identity & correlation metadata for governance and auditing.
- Provide a minimal, secure pattern you can adopt in your Agent365 backend.
- Show options (SDK-first, HTTP) and testing/validation steps.

**Files added/used**
- [src/bedrockGovernance.js](src/bedrockGovernance.js)
- [test/bedrockGovernance.test.js](test/bedrockGovernance.test.js)

**Prerequisites**
- AWS Bedrock access in your account (agent created and usable).
- Credentials or an IAM role that allows calling Bedrock agent runtime APIs from your backend.
- An Entra (Azure AD) App Registration for your Agent365 integration (this is the Entra Agent ID). Store the `clientId` and, if using confidential flow, `clientSecret`.
- A backend service (Node.js in this sample) that will receive requests from your Agent365 flow and call Bedrock.

High-level overview
1. User interacts with Agent365 (M365/declarative agent). Agent365/your frontend sends a request to your backend to fulfill the prompt.
2. Your backend extracts Entra identity claims (subject/upn/email, tenant id, app id) and a request/session id.
3. Build a governance context (identity + telemetry + correlation id) and pass it to Bedrock as session attributes.
4. Call Bedrock using the SDK or a signed HTTP request; include the governance data so downstream systems can audit and correlate.

Recommended minimal environment variables
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...           # optional (for STS)
BEDROCK_AGENT_ID=...
BEDROCK_AGENT_ALIAS_ID=...
EN_TRA_APP_ID=...               # your Entra (Azure AD) Application (Agent) ID
EN_TRA_TENANT_ID=...            # (recommended) lock token validation to a tenant id (GUID)

Security note: When `EN_TRA_TENANT_ID` is set, the service enforces exact `iss` (issuer) equality to the tenant-specific issuer URL. The primary expected issuer format is:

```
https://login.microsoftonline.com/<TENANT_ID>/v2.0
```

We also accept the tenant-specific v1 issuer and the STS issuer forms:

```
https://login.microsoftonline.com/<TENANT_ID>/
https://sts.windows.net/<TENANT_ID>/
```

Setting `EN_TRA_TENANT_ID` prevents tokens from other tenants from being accepted.
```

SDK-first example (Node.js)
- We provide `src/bedrockGovernance.js` which exposes:
  - `buildGovernanceContext({ user, requestId, sessionId })`
  - `invokeBedrockAgent({ prompt, governanceContext, agentId, agentAliasId, credentials })`

Example usage (pseudo-code):
```js
const { buildGovernanceContext, invokeBedrockAgent } = require('../src/bedrockGovernance');

// Extract Entra token / claims in your backend (see "Entra identity extraction" below).
const governanceContext = buildGovernanceContext({
  user: { upn: 'alice@contoso.com', tid: 'tenant-123', appid: process.env.EN_TRA_APP_ID },
  requestId: 'req-123',
  sessionId: 'sess-123'
});

const result = await invokeBedrockAgent({
  prompt: 'Summarize the changes',
  governanceContext,
  agentId: process.env.BEDROCK_AGENT_ID,
  agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    sessionToken: process.env.AWS_SESSION_TOKEN,
  }
});
```

Entra identity extraction (server-side)
- If the request to your backend includes an ID token (JWT) issued by Entra, validate it and extract the claims you need:
  - `sub`, `preferred_username` / `upn` / `email` (subject)
  - `tid` (tenant id)
  - `appid` or `azp` (app id / client id)
- If using delegated flows, call the Microsoft identity libraries (MSAL for your platform) to obtain/validate tokens. Always validate issuer, audience, and signature.

Telemetry and correlation
- Generate or accept a `requestId`/`correlationId` from the frontend and propagate it through all layers.
- Include `correlationId`, `traceId`, `sessionId`, and `requestId` in Bedrock session attributes (see sample code). Also emit these IDs to your logs and APM (Application Insights, New Relic, etc.).

Security, compliance and governance notes
- Minimize PII in what you forward to Bedrock. If you must include user data, document why and ensure appropriate retention/approval.
- Log only what is necessary for auditing. Store mapping of correlation IDs → user identities in a protected audit store for compliance.
- Use least-privilege IAM credentials for the backend. If possible, run the Bedrock call under an IAM role with restricted permissions and assume-role or use short-lived credentials.

Options other than the SDK
- Signed HTTP calls: you can call Bedrock APIs via HTTPS with AWS SigV4 signing. Use SDKs for convenience and correct signing, but HTTP is viable when integrating in constrained environments.
- AWS Lambda: host the Bedrock caller as a Lambda that your backend invokes. Useful if you want to centralize permissions and logging.

Testing & validation
1. Unit tests: there is a small test in `test/bedrockGovernance.test.js` that asserts governance payload creation.
2. End-to-end: run the backend with valid AWS credentials and your Bedrock agent ids, send a sample prompt from your Agent365 frontend, and validate:
   - Bedrock response is returned
   - Logs include correlation IDs and identity mapping
3. Audit: confirm logs are collected into your security/observability stack with proper retention and access controls.

Quick commands
```
# install deps
npm install

# run the sample unit tests
node --test
```

Troubleshooting
- If Bedrock returns authentication errors, verify AWS credentials and region.
- If identity fields are empty, confirm the token extraction/validation step and that the frontend supplied an ID token or user context.

Next steps I can take for you
- Implement Entra (MSAL) server-side token validation and claim extraction code and wire it into `src/bedrockGovernance.js`.
- Extend the sample to emit logs to Application Insights or another APM with the same correlation IDs.
- Add a minimal API endpoint that Agent365 can call directly (Express or Azure Function) and demonstrate the full flow.

If you want, I can add the Entra auth extraction code and an Express endpoint in this repo and run the local verification tests—tell me which option you prefer.
