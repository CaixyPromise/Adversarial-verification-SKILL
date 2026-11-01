# Review Playbook (read only relevant sections)

This is a menu of **risk-driven** probes, not a mandatory checklist. Start from the requirement, affected business flow, and risk allocation in `SKILL.md`. Select probes that can actually falsify an important assumption.

## Functional and business flow

- Translate the request into observable success criteria; identify preserved invariants and intended state transitions.
- Follow the real path: entry point → validation → decisions → state/data changes → external effects → response.
- Inspect affected upstream callers and downstream consumers; contrast against the previous contract.
- Try missing fields, invalid types, boundary values, conflicting inputs and unsupported transitions when relevant.
- Check actual outputs and side effects, not only green tests or success codes.

## State, persistence and async

- Retry/repeat mutating operations: idempotency, duplicate side effects, partial completion.
- Concurrent requests: races, stale reads, lost updates, duplicate creation, inconsistent ordering.
- Restart/reopen/reconnect: persisted state, resume/cancellation semantics, resource cleanup.
- Failure halfway through a business operation: rollback, compensation, recoverability and observability.
- Queue/worker/webhook: duplicate or out-of-order messages, timeouts, dead letters, replay.

## Data and performance

- Migrations with existing data: constraints, defaults, compatibility, rollback when supported.
- Query paths: N+1, scans, stable pagination, excessive round trips and missing useful indexes.
- Hot paths and large inputs: time/space growth, allocations, unnecessary loops, caches without bounds.
- Measure with representative data when feasible; separate measurements from hypotheses.

## UI / client / CLI / operations

- UI: complete user interaction, form validation, navigation, refresh, assets/network failures, accessibility where impacted.
- Desktop/mobile: session lifecycle, offline/reconnect, deep-link or bridge boundary, repeated event subscriptions.
- CLI: help/errors, stdout/stderr/exit code, malformed flags, quoting, dry-run behavior.
- Infrastructure: config actually wired, deployment readiness, backward compatibility, rollback and safe failure modes.
- Agent workflows: prompt/tool contract, authorization, state/memory boundaries, tool errors, retries, completion criteria.

## Evidence and coverage

A useful finding explains **what breaks, for whom, under what conditions**, and cites a reproducible observation or specific code path. If a runtime is unavailable, disclose that limitation. Do not inflate hypothetical or stylistic concerns into defects.

For substantial work, mentally check coverage across: requirement, main flow, neighboring regressions, errors, and the top material technical risks. For small changes, skip irrelevant categories. Inspect the applicable scope before returning a consolidated report.

After repair, re-run the failing probe and impacted regressions; avoid repeated full-suite review unless the change's blast radius genuinely increased.
