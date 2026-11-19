# Handoff: trainwright

Updated 2026-11-19. Read [INDEX.md](INDEX.md) first.

## State
- Step E (fill the plugin) in progress. Written: SKILL.md, tw.py (new, hash, check, config, run, record, rerun, diff, leak), tests/test_tw.py, references (image, video, voice, llm, eval, ship, hardware), evergreen companions (evergreen.json tier fast 14 d, RESEARCH, CHANGELOG, LEARNINGS L-001..L-014, MAINTENANCE, TESTS, harvest.json), README, root CHANGELOG 0.1.0.
- Nothing committed yet; repo files staged only.
- Owner-specific harvest lives in the private sidecar (`$TRAINWRIGHT_HOME/notes/harvest.md`); `ai-docs/notes/harvest.md` is a public stub.
- `tw.py leak` needs `TRAINWRIGHT_HOME` set to the sidecar to load leak-terms.txt.

## Next
1. Skill-on eval runs and decoys (evals/evals.json); log in skills/trainwright/TESTS.md.
2. Prove non-ai-toolkit mappings (kohya, musubi-tuner, VoxCPM, Unsloth/TRL) with dry runs; record in LEARNINGS.
3. Name re-check (pip, npm, GitHub), banner, commit, public repo, release.
