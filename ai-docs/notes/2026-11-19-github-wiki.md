# GitHub wiki (2026-11-19)

Pages for trainwright 0.1.0, written with wikiwright: Home, Getting-Started, Commands, Recipe-Format, Gates, Known-Issues, FAQ, Versions-and-Upgrading, Development, _Sidebar, _Footer.

- Status: written and checked (check, outputs, snippets all exit 0; `tw.py leak` 0 hits). NOT pushed yet: the wiki repository did not exist (preflight `no-wiki-repo`); the owner must save a first page at https://github.com/m4bwav/trainwright/wiki/_new, then clone `trainwright.wiki.git` next to this repo, copy the pages over the placeholder, commit, push, and run `wikiwright.py live m4bwav/trainwright <wiki dir>`.
- Draft pages: ../trainwright.wiki-draft (sibling of the clone) (outside the repo; copy into the wiki clone).
- Verification: `2026-11-19-wiki-verify.py` runs every example in a temp folder with a throwaway TRAINWRIGHT_HOME (stand-in base file, two-image dataset); output saved as `2026-11-19-wiki-verify.out.txt` (temp folder masked as `<tmp>`). Training itself not run. Unit tests: 13 passed.
- Update procedure: rerun the verify script, `wikiwright.py diffout` against the saved output, fix the pages that differ; the footer and Versions-and-Upgrading name the version.

## Facts the README lacks

- `new` writes `<name>.recipe.json`; `config` writes `<name>.recipe.yaml`.
- `hash --manifest` includes caption .txt and .jsonl files.
- `check --shallow` skips dataset hashes, GPU probe and disk floor.
- The GPU warning fires on memory over 6000 MB even at 0 % load.

## Inaccuracies and bugs found

1. Bug: `config --trainer <anything but ai-toolkit>` without `--out` overwrites the recipe JSON with the trainer settings (`with_suffix(".json")` on `<name>.recipe.<trainer>`). Documented on Known-Issues; fix in tw.py `cmd_config`.
2. README quick start uses `my-style.json` / `my-style.yaml`; the real names are `my-style.recipe.json` / `my-style.recipe.yaml`.
