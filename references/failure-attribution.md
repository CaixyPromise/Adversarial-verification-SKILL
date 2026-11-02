# Failure Attribution & Upstream Boundaries

**When to read:** a code review or test encounters an error that might belong to a browser, automation driver, third-party package, OS, runtime, external API, CI sandbox or environment. Mainly Agent C, supported by B for dependency integration and A for observable business impact. **This guide is not an additional review phase or mandatory diagnostics checklist.**

## 1. Determine who owns the failure

Distinguish **observed symptom**, **root-cause component**, and **actionable responsibility**. A stack trace mentioning a third-party package does not prove that package is defective. Nor does an upstream issue absolve our integration if it uses unsupported versions or misuses the API.

| Attribution | Evidence to seek | Review outcome |
| --- | --- | --- |
| Project-owned implementation/integration | Wrong API usage, invalid assumptions, unsupported version pin, changed code path, missing required error handling | Repair the smallest project-owned cause; targeted regression tests |
| Environment/CI/tooling | Missing executable, bad permissions/path, unsupported platform, incompatible installed binary, disk/full sandbox restrictions | Document the environment gap; do not call it a product defect without evidence |
| Confirmed upstream defect/limitation | Reproduced independently of project logic, or authoritative upstream bug/release note matching the version/conditions | Record upstream evidence and business impact; avoid modifying upstream internals |
| Upstream suspected / origin unknown | Insufficient/conflicting evidence | Classify as unverified, state what would distinguish hypotheses, stop bounded exploration |

If an upstream limitation affects a **supported, approved product behavior**, a project-side mitigation may still be worth proposing. It is not automatically required or permitted; evaluate security, correctness, test coverage and compatibility, and obtain user approval when it changes scope/policy.

## 2. Evidence-first, bounded investigation

1. **Capture the exact failure**: observed command/result, error message, stack location, reproducibility, affected contract, and first failing stage. Redact secrets and private data.
2. **Inspect before modifying**: project lockfiles and dependency version, existing browser/driver executable, OS/architecture, browser channel and launch options, expected upstream compatibility, local path/configuration and relevant logs.
3. **Isolate cheaply**: one focused rerun or minimal reproducer using already installed dependencies. Compare baseline or independent example when feasible. Do not repeat a broad flaky E2E suite, mutate the environment or download multiple browsers to chase PASS.
4. **Corroborate upstream claims** using exact-version official docs/release notes/known issue or a reproducible independent failure. Clearly distinguish confirmed from suspected.
5. **Stop and report** when root-cause evidence is sufficient or further work would require high cost/authorization. Record observations, attribution confidence, remaining uncertainties and next action.

Use the smallest reliable diagnostic, not the most elaborate environment. Prefer read-only version/path/log checks to destructive installation or cleanup.

## 3. Playwright / browser example: no reflexive downloads

For a browser launch failure, first inspect the installed Playwright version and lockfile, the **currently installed** compatible browser revision, channel/executablePath, CI/OS requirements and browser launch logs. The official Playwright documentation notes that browser revisions are version-coupled and that browser binaries can occupy **hundreds of MB**; do not assume a newly downloaded Chrome/Chromium fixes the application.

An optional **targeted** diagnostic is `DEBUG=pw:browser` for one relevant Playwright invocation. Inspect existing browser installations (for example `npx playwright install --list`, if available) before considering an install command.

**Do not autonomously run** `npx playwright install`, `playwright install`, `install --with-deps`, download a different browser, change system packages, switch global runtimes or install tools just to see whether a test turns green. Do not silently change browser test channels, bypass assertions, suppress exceptions or install a second browser variant as a workaround.

Before any *unrequested* material download, installation, persistent environment change or disk-intensive trace/video/screenshot generation:

- Explain the **reason**, expected network/disk cost, target location, reversibility and cleanup scope.
- Require the user's **explicit authorization**. Review-only verifier agents are read-only and cannot install dependencies.
- Prefer existing approved supported binaries and bounded artifacts; never delete shared caches or user files without consent.

Normal setup that the user already explicitly authorized is different; this rule prevents **review-triggered environment escalation**, not legitimate setup.

## 4. Repairs versus limitations and human decisions

- **Project-owned issue:** fix our source/configuration at its root and verify with focused tests.
- **Confirmed upstream fault:** do not patch third-party/browser internals or add broad speculative compatibility branches. Record exact version, minimal reproducer or upstream issue link and impact. Suggest a supported, minimal mitigation *only if genuinely required* and appropriately authorized.
- **Environment/CI issue:** do not label it an introduced product bug. If it blocks essential verification, mark the relevant evidence unavailable and use `PARTIAL` with precise limits; do not claim `READY` without required verification.
- **Unknown:** do not assert blame on either side. Summarize competing hypotheses and the cheapest next diagnostic, then stop.
- **New compatibility/product policy:** when choosing a different browser, disabling a feature, introducing a fallback or supporting an additional platform would expand requirements, record a **D### decision** and ask the user before implementing it. A separate upstream improvement proposal does not automatically block authorized delivery.

Never solve a blocked check by weakening test assertions, swallowing errors, silently changing the requested behavior, or claiming tests passed without execution.

## 5. Concise handoff evidence

**Symptom → command/error → versions and configuration → minimal isolation result → attribution & confidence → affected approved requirement → project-owned fix OR upstream/environment limitation → suggested next step and required approval**.

No speculative local fix is required simply because a failure occurred outside project ownership.

## Sources (load only if needed)

- [Playwright Browsers: version mapping, binary storage, installation and listing](https://playwright.dev/docs/browsers)
- [Playwright CI: targeted browser-launch logs](https://playwright.dev/docs/ci)
- [Playwright debugging guidance](https://playwright.dev/docs/debug)
- [Google Code Review: tests and complexity](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
