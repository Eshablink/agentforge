# Phase 14: security and supply-chain hardening

Phase 14 adds repository-level security controls around the already hardened application.

## Deliverables

- GitHub CodeQL analysis for Python and TypeScript/JavaScript using the current supported CodeQL Action major.
- Dependabot configuration for backend Python packages, frontend npm packages and GitHub Actions.
- A repository security policy with private-reporting guidance and explicit secret boundaries.
- Documentation for enabling GitHub dependency review when the repository dependency graph is available.

## Why this phase matters

The application already enforces authentication, ownership, bounded resources and fail-closed production settings. Phase 14 protects the software-delivery boundary as well: insecure dependency changes, vulnerable code paths and stale workflow actions should be detected before they become part of the portfolio artifact.

GitHub currently documents dependency review as a way to catch vulnerable dependency changes in pull requests. This repository is ready for that control, but the linked GitHub configuration currently does not have the dependency graph enabled. The official CodeQL Action currently supports v4 as the latest major.

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
\n### Dependency review enablement\n\nOnce GitHub Dependency Graph is enabled for the repository, re-add actions/dependency-review-action@v4 to the pull-request security job with a high-severity gate. The current security workflow intentionally omits it rather than producing a permanently failing check.\n