# Offline Review Dossier (optional)

The reporting helper is **not a gate**: do not spend more tokens documenting a trivial change than reviewing it. Use when the user requests an archive, review telemetry, or a concise deliverable. It is a **Python 3 standard-library-only** tool and a self-contained static HTML template (no server or external assets).

## One task -> one dossier (important)

Supply a **stable task ID** (issue / ticket / PR / requirement key) consistently across all calls, regardless of review rounds. If no --task-id is given, the script uses the feature branch when possible, otherwise the normalized task description; this fallback assumes the branch serves one requirement. For multiple tasks on one branch, pass distinct --task-id values.

The script first looks for **existing archives from this skill inside the project**, preferring an established folder. Otherwise it creates .adversarial-verification/reports at the Git repository root. It places a directory pattern in the repository's **local .git/info/exclude** (not committed .gitignore), checks that exclusion works, and refuses to overwrite files already Git-tracked. Never deliberately git add/force-add these reports. If safe exclusion cannot be assured, the script stops instead of writing.

Reports are pairs of review-<task>-<hash>.json and .html. **Calling start again on the same task does not create a second pair**: it reuses the existing report and opens a new review round when the previous one is closed, preserving previous findings and fixes. A repeated start while the round is open resumes that round. The report has a bounded project-local discovery strategy and never searches the entire home folder.

## Minimal command sequence

Run the tool from the repo containing the installed skill, using the **target project's path**. Commands below assume the script path is available as `python3 /path/to/skill/scripts/review_report.py`.

```bash
R=python3
S=/path/to/skill/scripts/review_report.py
P=/path/to/target-project
ID=ISSUE-123

$R "$S" --project "$P" start --task-id "$ID" --task "Implement permission package cloning" --risk 5 --agents 2
$R "$S" --project "$P" finding --task-id "$ID" --title "Missing ownership check" --category authorization --severity high --attribution introduced --reviewer A --evidence "permission.go:42; cross-user request permitted" --proposal "Enforce owner check at service boundary"
# Use returned finding_id, e.g. F001:
$R "$S" --project "$P" fix --task-id "$ID" --id F001 --status verified --actor parent --description "Added server-side owner validation" --verification "Unauthorized request now rejected; regression suite passed"
$R "$S" --project "$P" event --task-id "$ID" --kind test --text "Ran targeted integration checks"
$R "$S" --project "$P" finish --task-id "$ID" --assessment READY --summary "Critical paths verified; no known blockers"
```

The commands print existing JSON/HTML paths. Open HTML directly in a browser. The HTML allows search, severity/status/attribution filtering, finding expansion, per-round review, print/PDF, and JSON export. JSON is the authoritative structured record.

## Division of responsibility

- **Reviewer(s):** add/update findings with **evidence, severity, change attribution and a proposed fix**. Do not claim a fix was applied.
- **Parent/implementer:** after an actual change, use `fix` on the *same finding ID*, recording the actual repair and verification result; add concise events for tests, decisions or material activity. Never rewrite proposals to look like fixes.
- **Parent on exit:** call `finish` to store actual end time, assessment and short summary. Later reviews call `start` with the same ID and update the same report. If a title/category already exists, the script automatically reuses the previous finding ID. Use explicit --id for stable tracking if titles change. If a previously fixed/verified issue appears again, the same ID is reopened; prior repair records remain available.

## Telemetry provenance and accuracy

- Start/end timestamps and round elapsed durations are measured only between **script invocations**; this is a *recorded review window*, not a guaranteed measure of human/AI active effort.
- Token numbers are **optional**. Only pass `--input-tokens`, `--output-tokens` and the required `--token-source` on `finish` when trustworthy runtime telemetry is available. The helper never calls a model, introspects private runtime counters or estimates tokens. Unavailable data remains **unknown**, not zero. HTML totals clearly show the number of rounds with complete usage data.
- Counts represent **deduplicated findings across the task**, not the total number of mentions across rounds. Each fix appends a durable repair record.
- The JSON/HTML may contain sensitive snippets: keep them local, do not upload/commit without explicit user request. Avoid pasting secrets or personal data into finding text.

If reporting setup fails, **do not turn it into a blocking Review failure**. Provide a concise review outcome in chat, disclose the reporting limitation, and never claim that a file was archived.
