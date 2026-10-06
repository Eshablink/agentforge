# AgentForge progress

**Merged baseline:** Phases 0–8 are complete on main at `97934d7dd7f016a4d13f17b2afd4e577024d85a1` (Phase 8 PR #10). Phase 9 and Phase 10 are implemented and have passed targeted GitHub Actions on PR #11. Phase 11 is implemented on the same branch; final status must be read from checks on the final HEAD. No real cloud environment has been deployed.

## Separate phase gates

| Phase | Implemented on PR #11 | Verified scope |
|---|---|---|
| 9 | Native final-answer OpenAI-compatible deltas, fake simulation/fallback, controlled lifecycle, cancellation-safe frontend | Offline provider/mock tests plus full backend/frontend CI; native live provider not exercised by paid CI |
| 10 | Static non-root frontend image, trusted edge reference proxy, real deployment-validation workflow | Deployment Validation run 37430440521 and AgentForge CI run 37430440494 succeeded on pre-Phase-11 HEAD `84ce290b1544bd50cae17b62d6fd0998304aad41` |
| 11 | Small vector candidate pool, deterministic lexical reranking/threshold/duplicate suppression, bounded grounded context, expanded offline metrics | Phase 11 pytest/evaluation and both workflows must pass again on final HEAD |

## Evaluation and limitations

The runner prints deterministic fixture pass rates for RAG, tool, agent and stream case groups. It does not use paid APIs, a live LLM as scoring oracle, or prove model-generated factual accuracy. PostgreSQL integration tests retain owner isolation. Source references only include selected context chunks. Redis, managed PostgreSQL and TLS must be provisioned for real deployment; the reference proxy config does not deploy infrastructure. Phases 9–11 are not merged until PR #11 is reviewed and merged by a human.
