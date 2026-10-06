# Phase 14: security and supply-chain hardening

Phase 14 adds repository-level security controls around the already hardened application.

## Deliverables

- GitHub CodeQL analysis for Python and TypeScript/JavaScript using the current supported CodeQL Action major.
- Pull-request dependency review that blocks newly introduced high-severity dependency vulnerabilities.
- Dependabot configuration for backend Python packages, frontend npm packages and GitHub Actions.
- A repository security policy with private-reporting guidance and explicit secret boundaries.

## Why this phase matters

The application already enforces authentication, ownership, bounded resources and fail-closed production settings. Phase 14 protects the software-delivery boundary as well: insecure dependency changes, vulnerable code paths and stale workflow actions should be detected before they become part of the portfolio artifact.

GitHub currently documents dependency review as a way to catch vulnerable dependency changes in pull requests, and the official CodeQL Action currently supports v4 as the latest major.

## Verification

Security checks run:

- On pull requests targeting main.
- On pushes to main.
- Weekly on a schedule.
- Manually through GitHub Actions.

The existing application CI and Deployment Validation workflows remain unchanged and continue to provide the primary correctness and deployment gates.

## Non-goals

This phase does not introduce a third-party security vendor, paid observability platform, SSO/MFA, production traffic monitoring, or automated cloud provisioning.

No credentials are added to the repository.
