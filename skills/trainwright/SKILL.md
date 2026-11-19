---
name: trainwright
description: "Train your own models on a local GPU and keep each run as a recipe you can rerun: image and video LoRAs (ai-toolkit, musubi-tuner, kohya; Z-Image, Flux, SDXL, Wan), voice fine-tunes (VoxCPM), small LLM fine-tunes (Unsloth, TRL QLoRA), checkpoint picks against the base model, GGUF quantize and Ollama import. tw.py checks licence, consent, dataset hashes, disk and GPU before a run, writes trainer configs, records scores and diffs reruns. Use on 'train a LoRA', 'fine-tune a model on my data', 'make a voice model', 'fine-tune a small LLM', 'which checkpoint is best', 'redo that training run exactly', 'quantize to GGUF for Ollama'. Also 'refresh trainwright'. Not for brand LoRAs (brandwright), generating images or video (comfyui-gen), using a voice (voicewright) or picking a host (labwright)."
---

# trainwright

Every training run is a **recipe**: one JSON with the base model and its hash, licence, dataset manifest (file hashes, sources, consent), config, seed, steps, eval scores against the base and the output files. A run without one cannot be repeated or trusted.

Script: `scripts/tw.py` (Python 3.9+, standard library). Every verb prints JSON; exit 2 means a gate refused and lists why. Private facts (trainer installs, disk floor, hosts, leak terms) come from `TRAINWRIGHT_HOME` (default `~/.trainwright`); read its `setup.md` first when it exists.

```
tw.py new <image-lora|video-lora|voice|llm> <name>     recipe skeleton
tw.py hash <folder> --manifest --source "<where from>"  dataset items with sha256
tw.py hash <base.safetensors>                           base hash
tw.py check <recipe>                                    gates: licence, consent, hashes, strength-0, same-name output, disk, GPU
tw.py config <recipe> [--trainer ai-toolkit]            trainer config (ai-toolkit proven; others mapped, dry-run first)
tw.py run <recipe> <config> [--dry]                     runs the trainer from hosts.json, logs it into the recipe
tw.py record <recipe> --score k=v --pick step_N --files <out>
tw.py rerun <recipe> <new-name>    tw.py diff <a> <b>    tw.py leak --root <repo>
```

## The loop

1. **Host first.** Ask labwright (`lw.py status`) which GPU is idle. Training holds the GPU for hours: queue behind a busy one, never stop another job. Runs over an hour need the owner's go-ahead with an estimate; a few-step smoke run is a test.
2. **Recipe**: `new`, fill `base` (name, path, arch, licence) and `dataset` (`hash --manifest`), set `use` (personal, sellable, public-release). For a person's face or voice set `dataset.subject` and `consent` (`self`, `granted:YYYY-MM-DD <who>`); with consent recorded, go ahead; without it, ask, never refuse outright and never guess.
3. `check` until clean. `config`, then a smoke run of a few steps on a copy with `steps` small, then the real run.
4. **Pick the checkpoint**, then `record`.
5. **Ship**: LoRAs into the generator's loras folder with the recipe beside them; LLMs to GGUF and `ollama create` ([ship](references/ship.md)).

## Rules that change outcomes

- **A new run name every time.** ai-toolkit, and most trainers, *resume* a run whose output folder already exists instead of starting over or overwriting: the "new" LoRA silently continues the old one. To retrain, use `tw.py rerun <recipe> <new-name>`; to extend a LoRA on purpose, start a new name from it (`pretrained_lora_path`). `check` refuses a non-empty output folder.
- **Save every 100 steps and pick early.** Style and subject LoRAs often peak in the first few hundred steps and then overcook (90 images, rank 32, lr 1e-4: best at 250, collapsed by 500). Keep every checkpoint, render the held-out sheet at each, and lower lr or rank before adding steps. Never keep only the last step.
- Judge where the model will be used: a LoRA trained on a base model can barely show on its turbo variant, and trainer samples skip any companion LoRA.

Per kind, read only the one you need: [image LoRA](references/image.md), [video LoRA](references/video.md), [voice](references/voice.md), [LLM](references/llm.md), [eval](references/eval.md), [ship](references/ship.md), [hardware](references/hardware.md).

## Step 0: freshness (every use, one read)

Read `evergreen.json` here. If today is on or after `next_due` or `contradiction` is set, say so in one line, do the task, then refresh (`evergreen-refresh`). Due `volatile_claims` are re-checked before relying on them.

## Maintenance

Evergreen unit (topic: local LoRA, voice and LLM fine-tuning tools and methods; tier `fast`). Files: `evergreen.json`, [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evals/evals.json`, `harvest.json`. Lessons go in LEARNINGS.md as they happen; owner-specific ones go in `TRAINWRIGHT_HOME`.
