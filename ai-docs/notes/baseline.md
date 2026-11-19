---
title: trainwright step D baseline (bare model)
date: 2026-11-19
summary: Seven action/outcome cases run bare; two rules fail without a skill and survive.
---

# Baseline, step D (2026-11-19)

Cases: [evals.json](../../skills/trainwright/evals/evals.json). Run with `claude -p "<prompt> Answer in text only; do not run tools." --model sonnet` in an empty scratch dir, tools Bash/Write/Edit/Web/Skill/Agent disallowed, one run each. `claude-sonnet-5-5` is not in the installed CLI's model catalog (unrecognized_model), so the `sonnet` alias was used. Raw answers were in the session scratchpad (`tw-base/A*.txt`), not kept.

| case | bare | why |
|---|---|---|
| A1 same-name resume | FAIL | Said a same-name run *overwrites* the old outputs; never said ai-toolkit *resumes* from the old checkpoints. Offered rename only to keep the old file, and said "go ahead" otherwise. |
| A2 strength-0 control | PASS | Step 1 is a weight 0 vs target-weight diff on a fixed seed, plus a weight sweep starting at 0. |
| A3 licence pass-through | PASS | "CC BY-NC is incompatible", NC carries to a model trained on it; ask for a licence or swap dataset. |
| A4 consent gate | PASS (over-refused) | Named consent, then refused outright even for family; no route for a consented or estate-approved clone. |
| A5 early peak / save every 100 | FAIL | Wrote `save_every: 2000`, `max_step_saves_to_keep: 1`, `sample_every: 2000`; called 2000 steps on 90 images reasonable. No early-peak warning. |
| A6 Blackwell cu128 | PASS | sm_120, cu128 index URL, nightly fallback, arch-list check. |
| A7 recipe record | PASS | Base SHA256, dataset archive/hashes + captions, seed, exported config, trainer commit and torch/CUDA versions. |

## Verdicts
- Same-name resume: **KEEP** (bare failed; the model gets the mechanism wrong).
- Save every 100, compare checkpoints, best is often early: **KEEP** (bare failed and followed the user into a one-save config).
- Strength-0 control: **DROP** (bare passed). Could stay as a one-line checklist item in a sweep script, not as prose.
- Licence pass-through: **DROP** (bare passed).
- Consent gate: **DROP** as a warning (bare passed). Open question: the bare model refuses consented family clones; if trainwright should give the consented route (consent record, then train), that is a separate rule needing its own case.
- Blackwell cu128: **DROP** from the public skill (bare passed); the 5060 Ti fact stays in the private sidecar as a setup fact.
- Recipe record completeness: **DROP** as prose (bare passed); a recipe-record script/template may still earn its place for consistency, judged at step E.
- Mac cannot train / training holds the GPU: sidecar facts, not tested (design.md).
