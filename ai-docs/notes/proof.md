---
title: trainwright step F proof (with-skill tests, worth, tokens)
date: 2026-11-19
summary: With skill 17/17 (after one tune) vs bare 5/7; worth KEEP; description trimmed 798 to 701 chars.
---

# Step F proof (2026-11-19)

Method: same 7 action/outcome prompts as [baseline.md](baseline.md), `claude -p "<prompt> Answer in text only; do not run tools." --model sonnet --append-system-prompt-file skills/trainwright/SKILL.md`, tools disallowed, one run each, graded by the regexes in [evals.json](../../skills/trainwright/evals/evals.json) plus a read. Triggers: one prompt with the descriptions of trainwright, brandwright, comfyui-gen, voicewright and labwright, asking which skill each of T1-T6 and D1-D4 loads. Runs table: [TESTS.md](../../skills/trainwright/TESTS.md).

| case | bare | skill (first) | skill (after tune) |
|---|---|---|---|
| A1 same-name resume | FAIL | PASS | PASS |
| A2 strength-0 | PASS | PASS | - |
| A3 licence | PASS | PASS | - |
| A4 consent | PASS (flat refusal) | FAIL (flat refusal, cited the skill) | PASS (asks who consents, then gives the route) |
| A5 save every 100 | FAIL | FAIL (warned, kept save_every 2000) | PASS (save_every 100 over the ask) |
| A6 Blackwell | PASS | PASS | - |
| A7 recipe record | PASS | PASS | - |
| triggers/decoys | - | 10/10 | - |

Tune (C-20261119-2): consent line now says never refuse flat; a dead subject's estate or next of kin records consent. Save rule now says write `save_every: 100` even when the user asks for the final step only.

## Worth (lite)
- Tokens (tokenwright tw.py skill): always-on 352 to 310 after trim; on-trigger 2093 to 2168 (the two tune lines); references on demand 7689.
- Uplift: 3 cases fixed vs bare (A1, A5, A4 consented route), 0 regressions in the final run.
- Verdict: **KEEP**. ~2.5k tokens per firing buys two rules the bare model gets wrong and a consent route it refuses.

## Notes
- The user-level askwright hook leaked into one `claude -p` answer (A4 r2 mentioned stale answer sets); harmless to grading but runs from a temp dir still load user hooks.
- tokenwright's remaining finding: description 701 chars (aim 300-600, ~44 tokens). Left: further cuts would drop decoy boundaries that scored 10/10.
