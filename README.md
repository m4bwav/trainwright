# trainwright

A Claude Code plugin for training your own models on a local GPU and keeping each run as a recipe you can rerun: image and video LoRAs (ai-toolkit, musubi-tuner, kohya), voice fine-tunes (VoxCPM), small LLM fine-tunes (Unsloth, TRL QLoRA), checkpoint picks against the base model, GGUF quantize and Ollama import.

Every run is one JSON recipe: base model and its hash, licence, dataset manifest (file hashes, sources, consent), config, seed, steps, eval scores against the base and the output files. Gates run before training: licence pass-through, consent for a real face or voice, dataset hashes, a fresh output folder, disk and GPU.

## Install

```
claude plugin marketplace add m4bwav/trainwright
claude plugin install trainwright@trainwright
```

## Quick start

Ask "train a style LoRA on this folder", "fine-tune a small LLM on my notes", "which checkpoint is best" or "redo that training run exactly". The skill drives `tw.py`:

```
python skills/trainwright/scripts/tw.py new image-lora my-style
python skills/trainwright/scripts/tw.py hash datasets/my-style --manifest --source "own photos"
python skills/trainwright/scripts/tw.py check my-style.json
python skills/trainwright/scripts/tw.py config my-style.json --trainer ai-toolkit
python skills/trainwright/scripts/tw.py run my-style.json my-style.yaml --dry
```

Python 3.9+, standard library only; trainers run as subprocesses.

## Verbs

| verb | does |
|---|---|
| `new <kind> <name>` | recipe skeleton (image-lora, video-lora, voice, llm) |
| `hash <path> [--manifest]` | sha256 of a base or a dataset manifest |
| `check <recipe>` | gates: licence, consent, hashes, strength-0 sheet, same-name output, disk, GPU |
| `config <recipe> [--trainer T]` | trainer config (ai-toolkit proven; others mapped, dry-run first) |
| `run <recipe> <config> [--dry]` | runs the trainer and logs it into the recipe |
| `record <recipe>` | scores, pick and output files |
| `rerun <recipe> <new-name>` | same recipe under a new run name |
| `diff <a> <b>` | compare two runs |
| `leak --root <repo>` | scan public files for private terms, IPs and media |

## Privacy

Datasets, voice clips and trained weights never go in this repository. Private facts (trainer install paths, hosts, disk floor, recipes, leak terms) live in a folder named by `TRAINWRIGHT_HOME` (default `~/.trainwright`); `tw.py leak` fails on any term from its `leak-terms.txt`, any IP address or any media file in tracked files.

## Licence

MIT
