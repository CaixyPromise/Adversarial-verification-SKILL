# Domain Checklists

This file expands the verifier's scope beyond baseline functional testing.

The verifier should not stop at “feature works” or “tests pass.” When relevant, it should probe quality attributes and business constraints too.

## 1. Business correctness first

Before proposing or accepting a fix, ask:

- Does this preserve the business goal, or only satisfy the current tests?
- Does it preserve the user-visible contract?
- Does it avoid “water more flour, flour more water” behavior — adding compensating hacks just to get green checks?
- If a test and the business intent conflict, is the implementation changing the product semantics rather than solving the real defect?

### Anti-cheating rule

The verifier should explicitly warn the main thread if a suggested fix looks like:

- test overfitting
- hardcoded special cases for the fixture data
- fake success states
- swallowing errors to force pass conditions
- weakening validation only to satisfy a path
- adding retries/timeouts/guards that hide the real bug without resolving it

When this pattern appears, the verifier should say so directly:

- this change appears to make the tests pass without solving the underlying business or engineering problem
- the main thread should fix the root cause instead of papering over the symptom

## 2. Performance

Probe performance whenever the change affects:

- hot request paths
- rendering loops
- large lists or tables
- serialization/deserialization
- caching
- background jobs
- data pipelines

### What to look for

- obvious regressions in response time or throughput
- repeated expensive calls inside loops
- accidental O(n^2) behavior
- unnecessary full scans
- large payload inflation
- work duplicated on every render or request
- missing caching where the old design assumed it

### Minimum tactics

- run a representative path with enough volume to expose scaling issues
- compare before/after behavior when possible
- inspect logs/timings/query counts if available
- test a larger input than the happy-path fixture

## 3. Database design and query shape

Probe this whenever the change touches:

- ORM queries
- repository/data-access code
- migrations
- reporting endpoints
- list pages / search APIs

### What to look for

- N+1 query patterns
- too many sequential round trips
- joins that are broader than necessary
- joins across many tables when denormalization, precomputation, or staged querying would be safer
- common filter fields with no index
- indexes with wrong leading columns
- indexes that help one query but degrade the write path too much
- count queries or sort queries doing table scans
- ORM eager/lazy loading surprises

### Specific database checks

- Does this endpoint execute one query per row or per child entity?
- Are common `WHERE`, `ORDER BY`, or join keys indexed?
- Are queries reading far more columns than needed?
- Are joins across 3+ tables actually justified for the request path?
- Does pagination remain stable under realistic data volume?
- Do new indexes match the real access path, not just column existence?

### Anti-pattern warning

Do not recommend “add another join” or “just eager-load everything” unless you can explain why it is acceptable for the real workload.

## 4. Code quality and maintainability

The verifier should look for implementation choices that make the code technically pass but degrade maintainability.

### What to look for

- duplicated logic
- dead branches added only for test fixtures
- hidden coupling
- brittle string matching
- hardcoded environment assumptions
- error handling that obscures real failures
- large functions that mix unrelated concerns
- fixes that bypass the intended abstraction boundary

### Important distinction

Do not fail the implementation for style trivia.
Do fail or flag it if the chosen fix materially increases fragility or future break risk.

## 5. Memory leaks and resource lifecycle

Probe this whenever the change affects:

- listeners/subscriptions
- caches
- timers
- background workers
- browser-side stateful UI
- connection pools
- file handles
- streams

### What to look for

- listeners not removed
- timers not cleared
- unbounded caches
- retained references after navigation/refresh
- repeated initialization without teardown
- file/socket/DB handles not closed
- tasks that keep running after the feature says it is done

### Tactics

- repeat the same action many times
- refresh/reopen/reconnect and observe whether resources accumulate
- check task/process count, open handles, or memory if tooling exists
- look for stale subscriptions or duplicate handlers firing

## 6. Security and penetration mindset

Probe this whenever the change affects:

- auth/authz
- user input handling
- file access
- shell execution
- HTML rendering
- URL fetching
- redirects
- uploads/downloads
- secrets/config
- database query construction

### What to look for

- injection risks
- path traversal
- SSRF-style fetch paths
- open redirect behavior
- auth bypass
- privilege escalation
- unsafe defaults
- secrets exposed in logs or responses
- over-trusting client input
- missing ownership checks

### Minimum tactics

- try malformed or hostile inputs
- try cross-user or cross-resource access if relevant
- try unauthorized actions and observe whether they truly fail
- verify that denial paths are real, not just hidden in the UI

## 7. Test-data and sample-generation rules

When the verifier generates its own test cases, samples, or fixtures:

- do not stay on the happy path
- do not mirror only the examples the implementer already covered
- generate hostile, awkward, boundary, duplicate, malformed, and state-transition cases

If your generated data only proves the feature works when used correctly, you have not done adversarial verification.

## 8. How to report these findings back to the main thread

When you find an issue or suspicious fix pattern, be explicit about the category:

- business correctness
- performance
- database/query design
- code quality / maintainability
- memory / resource lifecycle
- security / penetration

When the issue is “passes tests but is the wrong fix,” say that directly.

Preferred phrasing:

- “This appears to satisfy the current tests without preserving the intended business behavior.”
- “This fix hides the symptom but leaves the underlying race / validation / ownership issue unresolved.”
- “This path is green on the happy path, but breaks under [probe].”
- “This query shape is likely to degrade under real data volume because [reason].”

## 9. Final mindset

The verifier is not there to make the report look thorough.
The verifier is there to protect the product, the system, and the future maintainers from a superficially successful but fundamentally weak change.
