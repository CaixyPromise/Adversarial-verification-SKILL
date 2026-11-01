# Code Structure & Naming Governance

**When relevant:** Agent B examines changed files, newly created modules, directory reorganizations and code whose structure makes a current requirement risky to change. This is a **reasoning aid, not a file-size limit, file-count quota, or mandatory repository-wide cleanup**. Project conventions in `project-conventions.md` take priority over generic naming preferences.

## Quality objective

Organize code around **stable responsibilities, high cohesion, manageable coupling and change locality**. A useful structure makes a function or module easy to find, understand, change and test without surprising unrelated behavior. Aim for the **smallest justified change**: splitting and consolidating are both tools, not goals.

### Four high-signal checks

| Aspect | Investigate | Reasonable direction |
| --- | --- | --- |
| **Responsibility and cohesion** | Does one file implement several independently changing domains, business flows, lifecycle stages or low-level utilities? Or is a long file actually one cohesive state machine / orchestration? | Extract genuinely independent responsibilities into existing domain modules or focused collaborators. Keep cohesive orchestration together. |
| **Coupling and dependency boundaries** | Do files pass hidden shared mutable state, import each other cyclically, bypass layer ownership or expose private details just to permit splitting? | Move logic to its rightful owner, reduce unnecessary cross-module knowledge; never trade one large file for a mesh of tightly coupled tiny files. |
| **Directory organization and fragmentation** | Does a flat directory mix unrelated domains or layer responsibilities? Are numerous single-function wrappers, pass-through modules or nearly empty files multiplying navigation cost? | Group by existing project domain/feature boundaries; consolidate wrappers only when they offer no meaningful contract, ownership or independent evolution. |
| **Change locality** | Does one small requirement repeatedly require editing many unrelated files, or does touching one monolithic module routinely affect unrelated features? What files change together? | Centralize shared business decisions in the owning service/policy, or separate independent responsibilities where evidence shows unnecessary coupling. |

**Evidence signals, not automatic blockers:** file length or function length, number of files in a folder, many exports, repeated wrapper layers, circular imports, unrelated changes concentrated in one file, and frequent co-change in Git history. Consider complexity and behavior together. Never mandate splitting at a fixed line threshold or merging below a fixed file count.

## Stable names, not conversation-stage names

**Names should identify durable business/technical roles, not the moment, prompt, rejected idea or AI-assisted iteration that created them.** Review changed file/directory names (and related exported symbols) for user-conversation leakage:

| Suspicious name if discussion-only | Better direction |
| --- | --- |
| `g0-bootstrap.ts` if `g0` means only a development phase | Name by the actual bootstrapping responsibility, e.g. `runtime-bootstrap.ts` *if accurate* |
| `user-management-no-id.tsx` | `user-management.tsx` |
| `new-driver-final.ts` / `driver-fixed2.ts` | A stable driver role or domain-specific name |
| `phase2-cache-handler.ts` if `phase2` is only a task label | A cache responsibility such as `cache-invalidation.ts`, if it matches the contents |
| `permissions-without-popup.tsx` | The feature/component name, without discussion commentary |

**Avoid conversation-driven overengineering:** Negative requests such as no ID, no modal or no option B normally constrain the final behavior; they do not automatically justify a persistent toggle, duplicate path, wrapper or abstraction that proves the rejected option was avoided. Prefer omission or existing compatible components unless independently needed for real runtime configuration, release, migration or compatibility.

Ask whether the added mechanism has a durable responsibility, and whether removing it preserves intended behavior. Keep necessary API versions, real feature flags and audit/compatibility evidence. Reviewers propose changes; they do not silently expand implementation scope.

A requirement to **hide an ID from users** is not a reason to name a code file "no ID version". Equally, "not using option B" must not become a filename or exported symbol. The codebase should make sense to someone **who never saw the AI conversation**.

**Exceptions:** G0, V2, legacy, experimental, migration, compatibility, rollout or protocol labels may be perfectly valid if they are **real, documented, durable distinctions** necessary for correct operation or coexistence. Verify actual meaning; do not rename based solely on an unusual filename, and do not erase legitimate migration or audit metadata.

Use the existing naming scheme (e.g. kebab-case or camelCase) consistently. Avoid generic `helpers2`, `utils-final`, `common-stuff` and unnecessary renames whose only benefit is aesthetics.

## Decision ladder: leave / reuse / extract / consolidate / reorganize

1. **Leave unchanged** when existing responsibilities and references are clear, even if a file is long or a folder has many files.
2. **Reuse** existing helpers, business services and modules with matching semantics instead of creating competing copies.
3. **Extract** an independent responsibility when it has a real owner, separate evolution or testing boundary, and reduces coupling or risk.
4. **Consolidate** fragmented wrappers or near-duplicate modules when they implement the same stable concept and merging lowers navigation/maintenance cost.
5. **Reorganize** a directory only when existing project structure is meaningfully obscuring domain boundaries; prefer incremental moves over a sweeping rewrite.

Every structural proposal should answer **what changes, why the current structure impedes the requested work, what gets simpler, what might break, and how to verify**. For nontrivial renames/moves, inspect:

- imports/exports, package entry points, aliases, generated code, path-sensitive tooling, case-sensitive filesystems and module resolution;
- dependency cycles, module initialization order, reflection or dynamic imports, runtime file lookups;
- tests, documentation, CI/build/package manifests, public APIs and backward-compatibility contracts.

**Important:** a verifier is read-only. It **proposes** a minimal change; the parent/implementer executes authorized refactors and records actual outcomes. Unrelated pre-existing structure issues should usually be non-blocking recommendations, not unrequested cleanup. Treat a structure/naming concern as blocking only when it demonstrably breaks the user's requirement, a binding project convention, an external contract, or material reliability/maintenance safety.

## Focused reviewer output

When relevant, report a concise **structure finding**: affected paths → responsibility/semantic mismatch → actual maintenance or behavioral impact → minimal rename/extraction/merge proposal → compatibility/test implications. Label historical debt versus an issue introduced by this change, and avoid inventing metrics. Do not request project-wide LOC or file-count scans for trivial edits.

## Further reading

- [Martin Fowler — Extract Class](https://refactoring.com/catalog/extractClass.html)
- [Martin Fowler — Move Function](https://refactoring.com/catalog/moveFunction.html)
- [Google Engineering Practices — What to look for](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
