# trainwright prior art and overlap (2026-11-19)

Research for the planned trainwright plugin: repeatable local training (datasets, image/video LoRAs, voice and small-LLM fine-tunes, eval vs base, quantize, deploy) with each run kept as a rerunnable recipe record. Hardware: RTX 5060 Ti 16 GB (Windows), LAN Mac for inference.
Marks: [web] = checked by search this session; [k] = from model knowledge (cutoff mid-2026), verify before relying on it.

## 1. Existing agent skills, plugins and MCP servers

| Project | What it does | Licence | How trainwright differs |
|---|---|---|---|
| huggingface/skills `hf-llm-trainer`, now `hugging-face-model-trainer` [web] | Claude Code plugin: TRL SFT/DPO/GRPO on **HF Jobs** cloud GPUs, GPU sizing, cost estimator, GGUF converter, pushes to Hub. Needs HF token with Jobs write. | Apache-2.0 [k] | Cloud and paid, LLM only, no image/video/voice, no local 16 GB tuning, no recipe record with consent or eval-vs-base gate. Closest competitor for the LLM lane. |
| Unsloth MCP servers (OtotaO/unsloth-mcp-server, scientiacapital fork, LM Studio port with RunPod tools) [web] | MCP tools: load model, prepare dataset, LoRA/QLoRA, generate, export. | community, mostly MIT/Apache [k] | Thin wrappers over one trainer; no dataset provenance, no eval, no recipe, LLM only. |
| SkillsMP `unsloth-finetuning` and similar community skills [web] | Prose guidance for Unsloth load, LoRA config, export. | varies | Same gap: one stack, no records. |
| Third-party mirrors (tessl.io, skills.sh, mcpservers.org) of the HF skill [web] | Copies; one Tessl scan rated a copy high risk. | as upstream | Not distinct. |
| Anthropic skills repo [k] | No training skill. | | |
| Kohya/ai-toolkit/OneTrainer GUIs [k] | Trainers with UIs; not agent skills. | Apache/MIT/AGPL (OneTrainer AGPL-3.0) | trainwright drives them, does not replace them. |

No found project covers multi-modal local training plus a provenance-and-eval recipe record. Sources: https://huggingface.co/blog/hf-skills-training , https://github.com/huggingface/skills , https://huggingface.co/docs/hub/agents-skills , https://glama.ai/mcp/servers/@OtotaO/unsloth-mcp-server , https://skillsmp.com/skills/scientiacapital-unsloth-mcp-server-claude-skills-unsloth-finetuning-skill-md

## 2. Name collision: "trainwright"
Web search [web]: only "Trainwright Performance", a UK rugby-brothers fitness coaching business (trainwrightperfromance.carrd.co). No GitHub software project, PyPI or npm package surfaced [web search only; run `pip index versions trainwright`, `npm view trainwright` and a GitHub repo search before release]. Verdict: free in software; low risk, different field.

## 3. Stack state and 16 GB fit

Blackwell (sm_120) on Windows [k]: needs CUDA 12.8+ and PyTorch 2.7+ cu128 wheels (cu128/cu129/cu130 nightly or stable); older cu121/cu124 builds fail with "no kernel image is available". xformers, bitsandbytes (>=0.45) and flash-attention need Blackwell-built wheels; flash-attn on Windows is often unavailable, use SDPA. Triton on Windows via `triton-windows`. brandwright-train references/setup.md already records the "no kernel image" fix.

| Stack | Role | 16 GB fit [k unless noted] |
|---|---|---|
| kohya sd-scripts | SD1.5/SDXL/Flux.1 LoRA | SDXL LoRA yes; Flux.1 LoRA yes with fp8 base + block swap/gradient checkpointing |
| ostris ai-toolkit | Flux, Z-Image, Qwen-Image, FLUX.2 klein, Wan 2.x LoRA | Z-Image / klein 4B yes (brandwright already uses); Flux.1 yes with quantize; Wan 2.2 5B / 14B LoRA tight: low res, few frames, layer offload |
| diffusers training scripts | reference DreamBooth/LoRA scripts | fine for SDXL; Flux needs 8-bit/quantized base |
| musubi-tuner (kohya-ss) | HunyuanVideo, Wan 2.1/2.2, FramePack, Qwen-Image LoRA | best bet for Wan video LoRA on 16 GB: fp8 + block swap, image-only or short clips |
| OneTrainer | GUI/CLI multi-model trainer (AGPL-3.0) | SDXL/Flux yes with offloading |
| Unsloth | QLoRA LLM, fast, Windows supported | 4-bit QLoRA up to ~14B (tight), 7-8B comfortable |
| Axolotl | YAML LLM fine-tunes | Linux/WSL first; 7-8B QLoRA fits |
| TRL | SFT/DPO/GRPO library (what HF skill uses) | 7-8B with PEFT + 4-bit |
| VoxCPM fine-tune [web] | `scripts/train_voxcpm_finetune.py` + YAML, JSONL manifest, `voxcpm validate` (2.0.3) | official estimates at batch 16: VoxCPM1.5 (750M) LoRA ~12 GB fits; VoxCPM2 (2B) LoRA ~20 GB, needs smaller batch / grad accumulation to fit 16 GB |
| llama.cpp `convert_hf_to_gguf.py` + `llama-quantize` | GGUF Q4_K_M/Q5_K_M/Q8_0, LoRA to GGUF adapter | CPU/RAM bound, fine |
| Ollama Modelfile `FROM ./x.gguf` / `ADAPTER` + `ollama create` | deploy to Mac/PC Ollama | fine |
| AWQ (AutoAWQ archived 2025; llm-compressor successor) | GPU quant for vLLM | 7-8B fits; low value for Ollama-based setup, GGUF is the main path |
| lm-evaluation-harness (EleutherAI) | eval base vs fine-tune on tasks | fine with HF or GGUF/llama.cpp backends |

VoxCPM sources: https://voxcpm.readthedocs.io/en/latest/finetuning/finetune.html , https://github.com/OpenBMB/VoxCPM/releases

## 4. Neighbour ownership (installed SKILL.md descriptions)

- brandwright 0.1.6: brandwright-capture builds a brand-site LoRA dataset (crawl, mask PII, tile, caption); brandwright-train trains brand and residual sub-site LoRAs with ai-toolkit (Z-Image, Qwen-Image-2512, FLUX.2 klein 4B), base choice by licence and 16 GB, Blackwell fixes; mockup generates through ComfyUI. Owns brand LoRAs end to end.
- comfyui-gen (~/.claude/skills): generation of images/video/music on the two ComfyUI hosts, using LoRAs, dataset captions via image_extras.py, Krea 2 licence rule; notes a PC GPU busy with training is not free. Owns inference, not training.
- voicewright 0.1.9: voice design, candidates, voice bible, lines, cast drift checks; VoxCPM2/VoxMel cloning. Owns voices as zero-shot clones; no fine-tuning.
- labwright 0.3.0: read-only server pool (up/idle/busy, model locations, download placement, disk floor). Owns where jobs and files go.
- local-delegate: offloads mechanical text to Ollama. Owns using local LLMs, not making them.
- artwright 0.7.8 (artwright-judge): blind pairwise and batch ranking of images, brief fit checks. Owns image judging; trainwright calls it for image-LoRA eval vs base.

## Verdict
trainwright owns only: the training run as a reproducible record (recipe: base + hash, licence, dataset manifest with sources and consent, config, seed, steps, eval vs base, output path) plus the generic trainers it drives that no neighbour covers: non-brand image and video LoRAs (character/style/Wan via ai-toolkit or musubi-tuner), VoxCPM voice fine-tunes, small LLM QLoRA (Unsloth/TRL), eval-vs-base gates (calling artwright-judge, voicewright checks, lm-eval-harness), and GGUF quantize + Ollama import. It defers brand LoRAs to brandwright, inference to comfyui-gen/voicewright/local-delegate, and host/disk choice to labwright.
