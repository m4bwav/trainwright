# AGENTS.md: trainwright

Agent plugin (one skill): repeatable local model training kept as rerunnable recipe records.

- Layout: `.claude-plugin/plugin.json`; `skills/trainwright/` (SKILL.md, references/, scripts/tw.py, evals/, evergreen files); `tests/`.
- Before committing: `python -m unittest discover -s tests` with `TRAINWRIGHT_HOME` pointing at the private sidecar. The leak test fails when no term list is found.
- No dataset, model weight, face, voice, host address or owner path in a tracked file, ai-docs/ included. Those live in `TRAINWRIGHT_HOME`.
- Python edits keep LF line endings; write Python with a file tool, not a Bash heredoc.
- State and handoff: [ai-docs/HANDOFF.md](ai-docs/HANDOFF.md), log [ai-docs/log.md](ai-docs/log.md).
