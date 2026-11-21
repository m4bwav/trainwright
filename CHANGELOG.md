# Changelog

## Unreleased

## 0.2.0 (2026-11-21)
- `tw.py compare --paired` (exact McNemar on per-item results), `record --vocab` warns LOSS-AT-CHANCE, `diff` refuses scores from different eval setups (EVAL-MISMATCH); LLM eval and pitfall rules from Cohen's 50 ML Projects to Understand LLMs.

## 0.1.1 (2026-11-19)
- Fix: `config` for trainers other than ai-toolkit no longer overwrites the recipe; configs are named `<name>.<trainer>.yaml|json`. README examples fixed.

## 0.1.0 · 2026-11-19

- First version: the trainwright skill, `tw.py` (new, hash, check, config, run, record, rerun, diff, leak), references for image, video, voice and LLM training, evaluation, shipping and hardware, and the evergreen companions. Skill-level changes: [skills/trainwright/CHANGELOG.md](skills/trainwright/CHANGELOG.md).
