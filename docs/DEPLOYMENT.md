# Deployment Options for Bedrock Agent API

This document describes simple deployment options for the Node-based Bedrock API (`src/bedrockApi.js`) used in this repository.

Common environment variables (required):

```
AWS_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=    # optional
BEDROCK_AGENT_ID=
BEDROCK_AGENT_ALIAS_ID=
EN_TRA_APP_ID=
EN_TRA_TENANT_ID=     # recommended
PORT=3000
```

1) Deploy as a standalone Node service (Docker)

- Build image:

```bash
docker build -t myassist-bedrock-api:latest .
```

- Run locally with env vars:

```bash
docker run -e AWS_REGION=... -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -e EN_TRA_APP_ID=... -e EN_TRA_TENANT_ID=... -p 3000:3000 myassist-bedrock-api:latest
```

2) Deploy to Azure App Service

- Use the Docker image above (push to a registry) or deploy the Node app directly using GitHub Actions.
- In App Service configuration, set the environment variables listed above.
- Ensure the app uses a managed identity or secure secret store for AWS credentials when possible.

3) Deploy as an Azure Function (HTTP trigger)

- Create an HTTP-triggered Function app in Node 18.
- Convert `src/bedrockApi.js` into an exported handler or create a small adapter that imports the code and invokes it.
- Set environment variables in the Function App settings.
- Prefer managed identity patterns for production credential management.

Security recommendations

- Never store long-lived AWS credentials in repo. Use Key Vault/Secrets Manager and reference them from the runtime.
- Use `EN_TRA_TENANT_ID` to lock down token validation to a single tenant.
- Use least-privilege IAM policies. Consider an assume-role / STS flow.

CI/CD

- Add a GitHub Actions workflow that builds the Docker image, runs `npm ci` and `node --test`, and optionally pushes to a container registry.

Example GitHub Actions snippet (simplified):

```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - run: node --test
      - run: docker build -t myassist-bedrock-api:latest .
```

That's a minimal set of deployment options. If you want, I can add a fully working GitHub Actions workflow and an Azure Function adapter next.
