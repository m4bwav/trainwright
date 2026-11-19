# Tests: trainwright

Test runs for [SKILL.md](SKILL.md). Cases live in [evals/evals.json](evals/evals.json). The bare-model baseline (step D, 2026-11-19) is in the repo's `ai-docs/notes/baseline.md`: same-name resume and save-every-100 failed bare, the other five cases passed. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; counts and the failing list are in `evergreen.json` under `tests`. Rules: [MAINTENANCE.md](MAINTENANCE.md) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines.

## Runs

### T-20261119-1 · 2026-11-19 · claude -p bare (sonnet) · windows · baseline 5/7
- A1 same-name resume · behaviour · wrong-outcome · said a same-name run overwrites; never named the resume.
- A5 early peak · behaviour · wrong-outcome · wrote save_every 2000 and kept one save.
- Skill-on runs and decoys owed.
- led to: R-20261119-3, C-20261119-1
