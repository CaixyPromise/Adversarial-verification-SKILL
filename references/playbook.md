# Adversarial Verification Playbook

## Core idea

The verifier does not try to prove the implementation is probably fine. It tries to find failure conditions the implementer did not cover.

## Universal baseline

Always start with:

1. read project instructions and conventions
2. run build if applicable
3. run tests if present
4. run linters/type-checkers if configured
5. check nearby regressions

Passing tests are not enough.

## Adversarial probes

### Boundary values

Try values such as:

- 0
- negative values
- empty string
- very long strings
- unicode
- maximum-sized inputs
- null-like or malformed structures

### Error paths

Try:

- missing fields
- wrong types
- invalid identifiers
- invalid state transitions
- unsupported flags or arguments

### Concurrency

For APIs, sessions, create-if-not-exists flows, and shared-state paths, try parallel calls and look for:

- duplicate creation
- lost writes
- race conditions

### Idempotency

Run the same mutating action twice and look for:

- duplicate side effects
- wrong second failure
- correct no-op behavior

### Orphan or nonexistent resources

Try reads, updates, deletes, or references against things that do not exist.

### Persistence and restart

For stateful UI or storage changes, test:

- refresh
- relaunch
- reopen
- fresh session behavior

### Response-shape validation

Do not trust:

- HTTP 200
- exit code 0
- “tests passed”

Check actual response shape, stdout/stderr, and field meanings.

### Business-correctness validation

Do not assume that a green test means the right product behavior. Ask:

- does this preserve the intended business rule?
- does this preserve the user-visible contract?
- is this a root-cause fix, or a fixture-specific workaround?

If the implementation appears to pass by weakening the contract, hiding errors, or special-casing the test data, call it out explicitly.

### Performance and query-shape validation

When the change touches data access or hot paths, check for:

- N+1 queries
- repeated round trips inside loops
- unstable pagination
- missing indexes on common filters or sort keys
- joins broader than needed, especially 3+ table joins on request paths

### Security-minded validation

When relevant, probe:

- auth / authz bypass
- ownership checks
- injection and traversal
- open redirect / SSRF-style fetch behavior
- secrets leaking in logs or responses

### Memory and resource lifecycle validation

When relevant, repeat actions and look for:

- duplicate listeners
- timers not cleaned up
- unbounded caches
- handles, workers, or tasks that keep accumulating

## Change-type guidance

### Frontend

- start the app
- use browser automation if available
- click and type for real
- inspect console logs
- refresh and retest
- check static assets or API subresources if relevant

### Backend / API

- start server
- call real endpoints
- validate response body and shape
- test malformed inputs
- test repeat requests
- test missing-resource behavior

### CLI / scripts

- run representative inputs
- inspect stdout/stderr/exit code
- test empty and malformed inputs
- verify --help output

### Infrastructure / config

- validate syntax
- dry-run where possible
- verify config is actually wired and effective

### Database migrations

- run up
- verify schema/result
- run down if supported
- test on existing data, not only empty state

### Refactors

- run unchanged tests
- diff public API surface if relevant
- spot-check same inputs produce same outputs

## Evidence standard

A verification result is not valid unless each check includes:

- what was checked
- exact command run
- actual output observed
- PASS or FAIL

Final output must end with exactly one of:

- `VERDICT: PASS`
- `VERDICT: FAIL`
- `VERDICT: PARTIAL`

## Practical anti-patterns

Do not allow the verifier to get away with:

- only reading code
- trusting the implementer's tests
- saying “probably fine”
- saying “I can't verify” without first checking available tools
- reporting PASS without command evidence
