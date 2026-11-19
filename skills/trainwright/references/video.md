# Video LoRA

Wan 2.x, HunyuanVideo and similar. No first-hand run backs this page yet: every setting here is unverified until a smoke run records it in LEARNINGS.md.

## Trainer choice

| Trainer | Models | 16 GB fit (unverified) |
|---|---|---|
| musubi-tuner (kohya-ss) | Wan 2.1/2.2, HunyuanVideo, FramePack | best bet: fp8 base + `--blocks_to_swap`, image-only or short clips |
| ai-toolkit (`tw.py config` writes `num_frames`) | Wan 2.x | 5B fits; 14B tight: low resolution, few frames, layer offload |

Before training, check whether a downloaded LoRA already does it; most video work so far needed none.

## Starting settings

- Start with **images only** (a character or style learned from stills), then add short clips (17-33 frames at 480p or lower).
- rank 16-32, lr 1e-4 to 2e-4, batch 1, `save_every: 100`, steps 500-2,000, seed fixed.
- Cache latents and text-encoder outputs first (musubi `cache_latents.py`, `cache_text_encoder_outputs.py`); training without caches will not fit.

## Mapping for musubi-tuner (unproven; dry run first)

`tw.py config --trainer musubi-tuner` writes neutral JSON. Map it to `wan_train_network.py` (or `hv_train_network.py`) flags:

| recipe `config` | musubi flag |
|---|---|
| rank / alpha | `--network_dim` / `--network_alpha` (`--network_module networks.lora_wan`) |
| lr | `--learning_rate` |
| steps | `--max_train_steps` |
| save_every | `--save_every_n_steps` |
| seed | `--seed` |
| quant fp8 | `--fp8_base` (and `--fp8_scaled` where offered) |
| low_vram | `--blocks_to_swap 20-36`, `--gradient_checkpointing` |
| frames / resolution | dataset toml: `target_frames`, `resolution` |
| base / dataset | `--dit`, `--vae`, `--t5` paths / `--dataset_config` toml |

Add `--mixed_precision bf16 --sdpa --timestep_sampling shift --output_name <run name>`. Task flag (`--task t2v-14B` and similar) must match the base.

## Pitfalls

- Same-name resume and early peak apply as for images ([image.md](image.md)).
- Block swap trades GPU memory for system RAM and speed; watch RAM, not only VRAM.
- Judge in the real inference graph (sampler, step count, any speed LoRA loaded), never from trainer previews.
- Training holds the GPU for hours: keep the render queue empty and launch detached.
