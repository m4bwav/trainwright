# Image LoRA

Character, style, object and UI LoRAs on a 16 GB GPU. Brand LoRAs belong to brandwright.

## Trainer choice

| Base | Trainer | 16 GB fit |
|---|---|---|
| Z-Image, FLUX.2 klein 4B, Qwen-Image | ai-toolkit (`tw.py config` proven) | yes with qfloat8 model and text encoder, `low_vram` |
| Flux.1 dev | ai-toolkit or kohya sd-scripts `flux_train_network.py` | yes with fp8 base, gradient checkpointing, block swap (unverified) |
| SDXL, SD 1.5 | kohya sd-scripts `sdxl_train_network.py` | yes (unverified) |
| any of the above | musubi-tuner (Qwen-Image), OneTrainer (AGPL-3.0) | musubi gave LoRAs comparable to ai-toolkit; OneTrainer untested |

Use a third-party LoRA when one already does the job; train only when none does.

## Starting settings (ai-toolkit, 16 GB)

`config`: rank 16-32, alpha = rank, lr 1e-4, batch 1, resolution 768-1024, `quant: qfloat8`, `low_vram: true`, `save_every: 100`, steps about 5 per image (400-1,500), seed fixed. Keep 20+ saves; never only the last.

## Mapping for kohya sd-scripts (unproven; dry run first)

`tw.py config --trainer kohya` writes neutral JSON. Map it to flags:

| recipe `config` | kohya flag |
|---|---|
| rank / alpha | `--network_dim` / `--network_alpha` (`--network_module networks.lora`) |
| lr | `--learning_rate` |
| steps | `--max_train_steps` |
| save_every | `--save_every_n_steps` |
| batch | `--train_batch_size` |
| grad_accum | `--gradient_accumulation_steps` |
| resolution | `--resolution W,H` |
| seed | `--seed` |
| quant fp8 | `--fp8_base` (Flux), plus `--blocks_to_swap N` when short of memory |
| base / dataset | `--pretrained_model_name_or_path` / `--dataset_config` toml |

Always add `--gradient_checkpointing --mixed_precision bf16 --sdpa --save_model_as safetensors --output_name <run name>`.

## Datasets

- Never train on a wrong picture. Drop a generated view after two failed reseeds; rerun only the missing views so dropped ones are not refilled.
- Clean reference pictures first: small emblems and logos get learned and copied.
- Synthetic datasets from a strong generator work for characters.
- Captions from a local vision model are fine; read a sample before training.
- For a canon look the generator keeps getting wrong, edit the canon picture instead of re-prompting, and show one face test before any batch.

## Pitfalls

- **Same name resumes.** ai-toolkit continues an existing output folder instead of starting over. `tw.py check` refuses a non-empty output; use `rerun <recipe> <new-name>`. To extend a LoRA on purpose use `network.pretrained_lora_path` with a new name.
- **Early peak.** 90 images, rank 32, lr 1e-4: best at step 250, collapsed by 500. Lower lr or rank before adding steps.
- **Trigger words on LLM text encoders** (Z-Image): the encoder reads the trigger as text and may draw it. A nonsense token leaked more and carried less style; quote real visible text in the prompt instead.
- **Trainer samples mislead** when the run uses an assistant or companion LoRA: samples unload it. Pick by rendering in the real graph. Fewer samples also save time (they took a third of one run).
- **Base vs turbo.** A LoRA trained on the base barely shows on its distilled turbo variant. Train on turbo only when turbo is the target.
- **Windows file locks.** A running ComfyUI memory-maps loaded LoRAs; copy picks under step-suffixed names (`<name>-s<step>.safetensors`) instead of overwriting.
