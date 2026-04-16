# Security Review Checklist

Use this when the verifier is handling security-sensitive work and needs a structured output format rather than a loose narrative.

This checklist is for evidence-based adversarial verification. It is not a generic best-practices essay. The verifier should only mark `PASS` when it ran a real probe or inspected a directly relevant runtime signal.

## Output template

For each relevant security area, use this structure:

### Security Check: [short label]
- Asset / trust boundary:
- Threat or abuse case:
- Command run:
- Output observed:
- Expected security property:
- Actual behavior:
- Impact if exploitable:
- Result: PASS or FAIL

End the report with one of:
- `VERDICT: PASS`
- `VERDICT: FAIL`
- `VERDICT: PARTIAL`

## Minimum rule

For security-sensitive changes, do not stop at “authorized happy path works”. At minimum, verify one hostile or unauthorized path.

## High-severity vulnerability prioritization

When a security issue is confirmed or strongly indicated, lead with the highest-severity finding first.

Use this practical priority scale:

- `Critical`: remote code execution, auth bypass to privileged actions, arbitrary file read/write outside intended boundaries, cross-tenant admin access, high-value secret exfiltration, or a vulnerability that can directly compromise the system or many users.
- `High`: cross-user data exposure, broken ownership checks, SQL/command/template injection with meaningful impact, SSRF to sensitive/internal targets, stored XSS in privileged surfaces, unsafe upload/download or traversal behavior that exposes sensitive data, or any exploit that materially breaks confidentiality/integrity for real users.
- `Medium`: exploitable weakness with narrower scope, lower privilege gain, or stronger preconditions, but still a real security defect.
- `Low`: hardening gap, noisy leak, or weak security signal that should be addressed but is not an urgent exploitable break on its own.

Rules:

- If `Critical` or `High` is confirmed, the report must not read like a soft cautionary note. Treat it as a primary finding.
- If a `Critical` or `High` issue is confirmed, the overall verdict should not be `PASS`.
- If severity depends on an environmental assumption you could not verify, say that explicitly instead of downgrading by guesswork.

## Checklist categories

Work through the categories that apply. Skip only when the category is clearly irrelevant to the change.

### 1. Authentication and identity
- Can an unauthenticated caller reach a protected path?
- Can an expired, malformed, or missing credential still get partial access?
- Is identity derived from a trusted runtime source instead of user-controlled input?

### 2. Authorization and ownership
- Can one user/tenant access another user/tenant resource?
- Are ownership checks enforced server-side/runtime-side rather than only hidden in UI?
- Are role or permission checks derived from trusted state rather than user-provided flags/claims without verification?

### 3. Input handling and injection
- Does hostile input change query meaning, command meaning, template meaning, or interpreter behavior?
- Are path, query, header, body, and metadata fields normalized and validated before use?
- Is there any place where raw input is interpolated into SQL, shell, HTML, Markdown, templates, or structured queries?

### 4. File access and path safety
- Can path traversal escape the intended root?
- Are symlink or normalization edge cases handled?
- Are uploads/downloads authorized by object identity rather than filename alone?

### 5. Network fetch, redirect, and URL trust
- Can attacker-controlled URLs trigger SSRF-style access or internal network fetches?
- Are redirects restricted to intended destinations?
- Is URL parsing/normalization robust against alternate schemes, encoded forms, or host confusion?

### 6. Process and tool execution
- Can user input alter shell/process arguments in unsafe ways?
- Are execution surfaces constrained by allowlists, safe APIs, or escaping rules?
- Are unsafe execution fallbacks hidden behind “temporary” or “debug” logic?

### 7. Data exposure and secrets
- Do logs, errors, traces, or debug output leak tokens, keys, credentials, file paths, or sensitive payloads?
- Does the response expose data the caller should not see?
- Are secrets/config values loaded from trusted sources and kept out of user-visible output?

### 8. Failure behavior
- When unauthorized or malformed input is used, does the system deny safely?
- Does the denial path leak internals, stack traces, or resource existence details?
- Does “error recovery” silently widen access or downgrade the security property?

## False-pass warnings

Call `FAIL` if the change appears to pass because of any of these patterns:

- security checks exist only in the UI, not at the trust boundary
- failures are hidden by generic success wrappers or error swallowing
- the implementation trusts client-controlled state for role, ownership, or capability
- tests pass only because fixtures never attempt cross-user or hostile input cases
- the patch reduces visible failure by weakening validation rather than fixing the vulnerability

## Security summary block

At the end of a security-sensitive verifier report, add a short summary:

- Highest-risk finding:
- Highest-risk severity:
- Confirmed safe boundaries:
- Unverified areas due to environment limits:
- Recommended next probe if follow-up is needed:
