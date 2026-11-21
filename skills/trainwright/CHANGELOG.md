# Changelog: trainwright

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261121-1 · 2026-11-21 · LLM eval honesty: loss floor, eval-setup match, answer-token scoring, paired compare
- because: Cohen, 50 ML Projects to Understand LLMs (2025), ch. 4
- files: references/eval.md (LLMs), references/llm.md (Pitfalls), SKILL.md (verbs), scripts/tw.py (record --vocab, diff, compare)
- `record` warns LOSS-AT-CHANCE, `diff` refuses EVAL-MISMATCH, new `compare --paired` (exact McNemar, Bonferroni, indicative under 200 items, EVAL-NAN).

### C-20261119-1 · 2026-11-19 · 0.1.0: created as an evergreen unit
- because: user request, R-20261119-1, R-20261119-2, R-20261119-3
- files: SKILL.md, references/ (image, video, voice, llm, eval, ship, hardware), scripts/tw.py, RESEARCH.md, LEARNINGS.md, TESTS.md, evergreen.json, harvest.json, evals/evals.json
- Initial version. Tier `fast`, interval 14 days. Core rules (same-name resume, save every 100 and pick early) kept because the bare baseline failed them.

- C-20261119-2 · 2026-11-19 · consent: never refuse a clone flat, estate/next of kin records consent for the deceased; save rule: write save_every 100 even when asked for the final step only; description trimmed 798 to 701 chars. because: T-20261119-2
