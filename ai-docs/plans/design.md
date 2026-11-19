# trainwright design (one page)

Sources: [harvest](../notes/harvest.md), [prior art](../notes/prior-art.md), continue prompt sections 5 and 6.

## Name
Keep **trainwright** (small ruling, 2026-11-19): no software project uses it; the one hit is a UK fitness coach. Re-check pip, npm and GitHub at release.

## What it holds (nobody else does)
1. **The recipe record**: one JSON per run. Fields: kind (image-lora, video-lora, voice, llm), trainer and version, base model with sha256 and licence, dataset manifest (file hashes, sources, consent, licence), config, seed, steps, checkpoints kept, eval scores against the base, output path, host, wall time. Rerunnable: `tw.py rerun` rebuilds the trainer config from it.
2. **Gates before a run**: licence pass-through (non-commercial data makes a non-commercial model; Krea 2 banned from sellable projects; avoid Meta-gated bases), consent for any real face or voice, disk floor and GPU idle through labwright, a dry run of a few steps first.
3. **Config generators** for each trainer: ai-toolkit (Z-Image, Flux, Wan), musubi-tuner (Wan), VoxCPM LoRA, Unsloth or TRL QLoRA. Each one is proven on the real trainer before it is trusted.
4. **Evaluation against the base**: a held-out prompt sheet rendered with the base and with each checkpoint, plus a strength-0 control, ranked by artwright-judge. Voices go to voicewright checks; LLMs to lm-eval-harness or a held-out prompt sheet. Pick by eye early: style LoRAs peak early.
5. **Ship**: GGUF convert and quantize, then `ollama create` from a Modelfile; LoRAs copied into the ComfyUI loras folder with the record beside them.

## What stays with the neighbours
brandwright: brand LoRAs (it may call trainwright later, never the reverse). comfyui-gen: inference. voicewright: voice use and zero-shot clones. labwright: hosts, model locations, disk floor. local-delegate: using local LLMs. artwright-judge: ranking images.

## Shape
One hub skill (`skills/trainwright/SKILL.md`). There are no siblings until a kind's reference outgrows a load. References are loaded on demand, one per kind (image, video, voice, llm, ship, eval), plus hardware and licences. The script `scripts/tw.py` uses only the standard library and calls trainers as subprocesses. Verbs:
`new <kind>` (writes a recipe skeleton), `check <recipe>` (licence, consent, manifest hashes, disk and GPU gates), `config <recipe> --trainer T` (writes the trainer config), `run <recipe> [--dry]`, `record <recipe>` (fills scores and outputs), `rerun <recipe>`, `diff <a> <b>` (compares two runs), `leak` (public-file scan).

## Sidecar (`TRAINWRIGHT_HOME`, a folder in the everlast vault)
Hosts and trainer install paths, measured speeds, the owner's datasets and their consent notes, per-project licence rulings and voice references. No dataset ever goes in the repository. `tw.py leak` fails the build on any sidecar term, IP address or media file in a public file (the pattern is brandwright check_public plus the everkeep overlay).

## Proof for each rule (step D decides which survive)
A rule enters only if a bare case fails without it, or if it is a fact the model cannot know.
- ai-toolkit silently resumes a run with the same name. Case: ask the model to retrain an existing name.
- Strength-0 control in every sweep. Case: "is my LoRA working?"
- Licence pass-through. Case: fine-tune on CC BY-NC data for a sellable game.
- Consent gate. Case: train a voice from a relative's clips.
- Early peak and save every 100 steps. Case: "train 2,000 steps on 90 images".
- Blackwell needs cu128 or newer. Case: "no kernel image" error.
- The Mac cannot train, and training holds the GPU. These are facts about the owner's setup, so they go in the sidecar.
