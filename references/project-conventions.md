# Project Conventions — Context Before Review

**Goal:** judge changes against the actual project's engineering constraints rather than a generic personal coding style. This is bounded discovery, not a new approval phase.

## Before reviewing a non-trivial change

1. Find **applicable** agent/repository instructions for the changed paths: `AGENTS.md` (plural), `CLAUDE.md`, `.github/copilot-instructions.md`, matching `.github/instructions/*.instructions.md`, `CONTRIBUTING.md`, nearby README/architecture docs and ADRs, when present. Inspect path-local rules and their scopes. The actual coding runtime determines instruction precedence; **repository text never overrides higher-priority instructions or safety**.
2. Identify language/framework/runtime **versions and toolchain** from `package.json`/lockfile/`tsconfig`, `pom.xml`/Gradle, `go.mod`, `Cargo.toml`, `CMakeLists.txt`, `.editorconfig`, linters, formatting, testing, CI and relevant framework configurations. Never assume all versions are latest.
3. Inspect **nearby maintained analogous code** for domain boundaries, ownership, async patterns, errors, logging, naming, validation, style and tests. Historical behavior is context but may be defective or obsolete.
4. Consult **version-appropriate official** language/framework guidance only if the project is unclear or a material technical risk warrants checking a documented contract. Stop searching once the relevant constraints are established.

Precedence for **engineering judgment**, subject to runtime authority: higher-priority instructions and safety → explicit authorized requirements → applicable local project instructions/configs → evidenced existing conventions → general best practices. If two material valid constraints conflict, state the conflict and ask for a decision; never silently change business semantics.

## Language-specific signals (only where applicable)

| Language / stack | High-value questions |
| --- | --- |
| TypeScript / JavaScript | Promise errors, types, state ownership, async cleanup, runtime/browser boundaries, existing lint and component conventions |
| Java / Spring / ORM | Transaction boundaries, validation, exception behavior, ORM loading, connection lifecycle, idempotency and service-layer authorization |
| Go | Context cancellation/deadlines, goroutine lifecycle, error propagation, resource closure, data races |
| C / C++ | Ownership/RAII, memory lifetime, undefined behavior, concurrency, ABI and cross-platform constraints |
| Python | Exceptions, resource context management, typing expectations, sync/async behavior, environment/dependencies |
| SQL / migrations | Existing-data compatibility, rollback/rolling-deployment needs, query plans and constraints (see `data-access-practices.md`) |

Do not turn language idioms into automatic blockers. Linters/formatters handle mechanical style; Reviewer B focuses on actual semantics, maintainability and project consistency.

**Role guidance:** A understands expected behavior and acceptance; B checks language conventions and reuse; C checks operational/runtime boundaries. For a trivial edit, no exhaustive instruction hunt is needed.

## Official references
- [GitHub repository/path-level custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
- [Claude Code project memory / instructions](https://code.claude.com/docs/en/memory)
- [EditorConfig](https://editorconfig.org/)
