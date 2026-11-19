# Voice fine-tune

Fine-tuning a TTS model on one speaker. Zero-shot cloning and using voices belong to voicewright; try a zero-shot clone first, and fine-tune only when it misses the voice.

## Consent first

A real person's voice needs `dataset.subject` and `consent` in the recipe (`self`, or `granted:YYYY-MM-DD <who>`). With consent recorded, go ahead. Without it, ask; never refuse outright and never guess. Lab audio stays out of public repos.

## Trainer choice

| Model | How | 16 GB fit |
|---|---|---|
| VoxCPM 1.5 (750M) | `scripts/train_voxcpm_finetune.py` + YAML, JSONL manifest, `voxcpm validate` | LoRA about 12 GB at batch 16: fits |
| VoxCPM2 (2B) | same script | LoRA about 20 GB at batch 16: drop batch to 4-8 with grad accumulation |

Figures are the project's own estimates (docs, 2.0.3); not yet measured here.

## Data

- 10-60 minutes of clean single-speaker audio, cut to 3-15 s clips, each with an exact transcript (JSONL: `audio`, `text`).
- A denoise pass made no audible difference on clean takes; skip it unless the source is noisy.
- Run `voxcpm validate` on the manifest before any training.

## Mapping for VoxCPM (unproven; dry run first)

`tw.py config --trainer voxcpm` writes neutral JSON. Copy into the trainer YAML:

| recipe `config` | VoxCPM YAML |
|---|---|
| lr | `learning_rate` |
| steps | `num_iters` (or `max_steps`) |
| batch / grad_accum | `batch_size` / `grad_accum_steps` |
| save_every | `save_interval` |
| rank / alpha | `lora.r` / `lora.alpha` |
| seed | `seed` |
| base / dataset | `pretrained_path` / `train_manifest` |

Key names vary by release; check the release's example YAML.

## Licences

Track the licence of the base **and** the data. Non-commercial training data (CC BY-NC) makes a non-commercial voice; some engines forbid using their output to train any commercial model. Keep a sellable project on a base and data that allow it.

## Pitfalls

- A voice designed from a prompt is not a stable identity: render one clean reference clip and clone or train from that frozen clip.
- Save often and judge checkpoints by ear, blind, against the zero-shot clone ([eval.md](eval.md)).
