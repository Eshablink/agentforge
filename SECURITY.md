# Security

## Supported scope

AgentForge is a portfolio project and is currently supported on the latest main branch. Security fixes are prioritized for authentication, authorization, document ownership, provider integration, streaming lifecycle, resource bounds and deployment configuration.

## Reporting a vulnerability

Please do not publish credentials, exploit details or sensitive information in a public issue.

Use GitHub's private vulnerability reporting feature for this repository when available. Otherwise, contact the repository owner privately through GitHub and include:

- A clear description of the vulnerability.
- Reproduction steps or a minimal proof of concept.
- The affected component or endpoint.
- The security impact.
- Any suggested mitigation.

Please allow reasonable time for validation and remediation before public disclosure.

## Security boundaries

The application intentionally does not allow model output to execute arbitrary shell commands, Python, filesystem operations, generated SQL or unrestricted network requests.

Production configuration fails closed when shared rate limiting is missing, Redis is not TLS-protected, providers are fake, CORS is wildcarded or non-HTTPS, or database credentials look like development defaults.

## Secrets

Never commit:

- API keys.
- Database passwords.
- Redis credentials.
- Session tokens.
- Private documents.
- Provider prompts or hidden reasoning traces.

CI uses fake/test provider credentials and local disposable infrastructure only; it does not make paid model calls.

## Dependency hygiene

Dependabot tracks Python, npm and GitHub Actions dependencies. CodeQL performs security analysis for Python and TypeScript/JavaScript code. GitHub dependency review is documented for later enablement once this repository's dependency graph is enabled.
