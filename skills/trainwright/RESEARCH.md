# Research: trainwright

Findings that back [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons in [LEARNINGS.md](LEARNINGS.md); runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

Topic: local LoRA, voice and LLM fine-tuning tools and methods on a 16 GB GPU. Tier `fast` (trainers ship weekly).

## Current understanding

- No agent skill or MCP server found covers multi-kind local training with a provenance and eval-vs-base record. The closest is Hugging Face's model-trainer skill (TRL on paid HF Jobs, LLM only); Unsloth MCP servers and community skills wrap one trainer with no records.
- Image LoRAs on 16 GB: ai-toolkit with qfloat8 and `low_vram` is proven first-hand; kohya sd-scripts (SDXL, Flux.1 with fp8 + block swap) and musubi-tuner are mapped but unverified here.
- Video LoRAs: musubi-tuner with fp8 base and block swap is the likely fit for Wan 2.x on 16 GB (unverified).
- Voice: VoxCPM ships an official LoRA fine-tune script; its own estimates put VoxCPM1.5 LoRA at about 12 GB and VoxCPM2 at about 20 GB at batch 16.
- LLMs: Unsloth or TRL 4-bit QLoRA fits 7-8B comfortably (unverified); GGUF via llama.cpp then `ollama create` is the ship route.
- Blackwell needs CUDA 12.8+ torch wheels; SDPA over flash-attn on Windows (model knowledge, unverified; matches first-hand "no kernel image" fix).
- A bare model already knows licence pass-through, consent, strength-0 control, Blackwell wheels and recipe fields; it fails on same-name resume and early-peak checkpointing. Those two are the skill's core rules (baseline 2026-11-19).

## Open questions

- Real 16 GB fits and speeds for Wan 2.2 LoRA in musubi-tuner and ai-toolkit.
- VoxCPM2 LoRA at reduced batch on 16 GB: quality vs zero-shot clone.
- Does Unsloth's Windows install work on Blackwell without WSL?
- Which non-ai-toolkit config mappings survive a real dry run.

## Search plan

Subject: ai-toolkit, sd-scripts, musubi-tuner, unsloth, VoxCPM, llama.cpp release notes since `last_checked` (see `harvest.json`); `Wan 2.2 LoRA 16GB <year>`; `VoxCPM fine-tune VRAM`.
Tooling: `path:SKILL.md lora training` and `path:SKILL.md fine-tune` on GitHub; `registry.modelcontextprotocol.io/v0/servers?search=fine-tune`; huggingface/skills changes.
Practice: r/StableDiffusion, r/LocalLLaMA, r/unsloth, r/comfyui threads on settings and checkpoints, dated only.
Testing: `lm-evaluation-harness` releases; LoRA checkpoint selection methods; speaker-similarity metrics for TTS fine-tunes.

## Findings log

### R-20261119-3 · 2026-11-19 · Bare baseline decides which rules stay
- Summary: 7 cases bare; same-name resume and save-every-100/early peak failed, the rest passed. Magnitude 0.6 for the skill's scope.
- Track: testing
- Sources: ai-docs/notes/baseline.md

### R-20261119-2 · 2026-11-19 · Stack state and 16 GB fits
- Summary: trainer table above. VoxCPM figures checked on the web; other fits from model knowledge, marked unverified in references.
- Track: subject
- Sources: https://voxcpm.readthedocs.io/en/latest/finetuning/finetune.html , https://github.com/OpenBMB/VoxCPM/releases

### R-20261119-1 · 2026-11-19 · Prior art and name
- Summary: no multi-kind local training skill with records exists; HF model-trainer is cloud LLM only. Name "trainwright" free in software.
- Track: tooling
- Sources: https://huggingface.co/blog/hf-skills-training , https://github.com/huggingface/skills , https://glama.ai/mcp/servers/@OtotaO/unsloth-mcp-server
