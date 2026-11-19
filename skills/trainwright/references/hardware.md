# Hardware and environment

Facts for a single 16 GB NVIDIA GPU on Windows or Linux. Host names, install paths and measured speeds belong in `TRAINWRIGHT_HOME` (`setup.md`, `hosts.json`), never here.

## Blackwell (RTX 50 series, sm_120)

- Needs CUDA 12.8 or newer and PyTorch 2.7+ built for it: `pip install torch --index-url https://download.pytorch.org/whl/cu128` (cu129/cu130 also work). Older cu121/cu124 wheels fail with `no kernel image is available for execution on the device`.
- Check: `python -c "import torch;print(torch.__version__, torch.version.cuda, torch.cuda.get_arch_list())"` must list `sm_120`.
- Attention: use PyTorch **SDPA** (`--sdpa`, the default in most trainers). flash-attn often has no Windows or Blackwell wheel; do not install it unless a prebuilt wheel exists.
- xformers and bitsandbytes need Blackwell-built releases (bitsandbytes 0.45 or newer).
- Triton on Windows: `pip install triton-windows`; needed for torch.compile and some fused kernels.

## Memory levers on 16 GB (in order)

1. Quantize the frozen base: qfloat8 or fp8 for diffusion bases, 4-bit nf4 for LLMs.
2. Gradient checkpointing.
3. Batch 1 with gradient accumulation.
4. Cache latents and text-encoder outputs.
5. Block swap or layer offload (costs RAM and speed).
6. Lower resolution or frame count.

## Running

- Training holds the GPU for hours. Find an idle host first (labwright `lw.py status`), queue behind a busy one, never stop another job, and keep render queues empty during a run.
- Launch long runs detached and log to a file; a session may see no output for hours.
- Smoke run first: a few steps on a copy of the recipe (`tw.py run <recipe> <config> --dry`, then `--steps 5`).
- Disk: checkpoints every 100 steps add up (a 6B-base LoRA save is tens to hundreds of MB); check the free-space floor before a run (`tw.py check`).
- Apple Silicon: inference yes; training mid-size diffusion bases ran out of MPS memory. Train on the NVIDIA host.
