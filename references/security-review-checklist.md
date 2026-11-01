# Security Review Checklist (optional)

Use only for security-sensitive changes. This is a focused threat-and-evidence aid, **not** an obligation to run every probe or perform unauthorized penetration testing.

## Establish the boundary

- Protected asset, actor, trust boundary, intended permission and business rule.
- Relevant call path and enforcement point; client-side hidden UI is not server-side authorization.
- Assumptions about authentication, roles, tenant/resource ownership and production configuration.

## Relevant checks

- **Identity and authorization:** absent/expired credentials, forged identities, cross-user or cross-tenant object access, privilege changes, ownership enforcement.
- **Input and execution:** injection in SQL/shell/templates/HTML, unsafe process arguments, file traversal, untrusted URL fetch/redirect and upload paths.
- **Sensitive data:** secrets in logs, traces, errors and responses; unnecessary exposure or retention.
- **Failure semantics:** denial fails closed; no fake success, exception swallowing or unauthorized fallback.
- **Abuse and state:** replay, races, duplicates, rate limits or resource exhaustion when material to the changed surface.

Use harmless, isolated reproductions or code-path reasoning. Do not access others' data, attack production, or mutate external systems without authorization.

## Findings

For each material issue provide:
- affected asset/actor and trust boundary
- trigger and concrete evidence (or clearly labeled unverified hypothesis)
- expected security property versus actual behavior
- impact and severity: Critical / High / Medium / Low
- minimal repair direction and verification gap

Confirmed Critical/High exploitation or authorization/integrity violations block `READY`. An uncertain security assumption is not a confirmed defect; escalate or mark residual risk as appropriate.
