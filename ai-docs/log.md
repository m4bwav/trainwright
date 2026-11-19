
- 2026-11-19: step D baseline done (ai-docs/notes/baseline.md). Survivors: same-name resume, save-every-100/early peak. `claude -p --model claude-sonnet-5-5` fails (unrecognized_model); use `--model sonnet`.
- 2026-11-19: step E files written (references, evergreen companions, README); owner harvest moved to sidecar notes/harvest.md.
- 2026-11-19: proof case passed. An SD1.5 LoRA (8 synthetic images, 200 steps, seed 42) went through tw.py check, config and run on ai-toolkit, then was rerun from the same recipe. Weights cosine 0.96 (not bit-identical, L-015). On the held-out sheet both runs learned the trigger, matched by eye, and left an unrelated prompt unchanged. Recipes are in the sidecar recipes/.
- 2026-11-19 step F: with-skill 17/17 after tune (bare 5/7), worth KEEP, see notes/proof.md
- 2026-11-19: wiki pages written and verified (ai-docs/notes/2026-11-19-github-wiki.md); push blocked until the wiki's first page is saved in the web UI. Found config-overwrites-recipe bug for non-ai-toolkit trainers.
