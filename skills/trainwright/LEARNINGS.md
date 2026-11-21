# Learnings: trainwright

Lessons that shaped [SKILL.md](SKILL.md) and tw.py. Seeded 2026-11-19 from a harvest of one owner's training and generation notes; only the general lessons are here, owner-specific ones (hosts, datasets, speeds) live in the private sidecar (`TRAINWRIGHT_HOME`). Entry shape: `L-NNN code-name · date · source · lesson · fix`.

- L-001 `toolkit-resumes-same-name` · 2026-11-19 · LoRA training notes · ai-toolkit silently resumed an old run whose output folder had the same name. · New run name every time; `tw.py check` refuses a non-empty output; `rerun` takes a new name.
- L-002 `extend-with-new-name` · 2026-11-19 · environment notes · Updating a LoRA in place mixes runs. · `network.pretrained_lora_path` with a new job name.
- L-003 `loras-peak-early` · 2026-11-19 · LoRA training notes · 90 images, rank 32, lr 1e-4: best at step 250, collapsed from 500. · Save every 100, keep 20 saves, pick by eye; lower lr or rank before adding steps.
- L-004 `llm-encoder-draws-trigger` · 2026-11-19 · LoRA training notes · An LLM text encoder drew the trigger word as text; a nonsense trigger leaked more and carried less style. · Quote real visible text in prompts; avoid nonsense triggers on such bases.
- L-005 `comfy-maps-loaded-loras` · 2026-11-19 · LoRA training notes · Overwriting a LoRA a running ComfyUI had loaded failed on Windows (file mapped). · Ship picks under step-suffixed names.
- L-006 `samples-skip-companion-lora` · 2026-11-19 · LoRA training notes · Trainer samples unloaded the assistant LoRA and misled; samples also took a third of the run time. · Pick in the real inference graph; fewer samples.
- L-007 `base-loras-weak-on-turbo` · 2026-11-19 · mock-up notes · A LoRA trained on the base barely showed on its turbo variant. · Judge and train on the model that will be used.
- L-008 `strength-zero-control` · 2026-11-19 · generation notes · A strength sweep barely moved; strength 0 already looked right from the prompt. · Always include strength 0 against the base.
- L-009 `trainers-comparable` · 2026-11-19 · plugin notes · musubi-tuner and ai-toolkit gave comparable image LoRAs. · Either is fine; prove each config generator on the real trainer.
- L-010 `no-wrong-pictures` · 2026-11-19 · generation notes · Bad generated views polluted datasets. · Drop a view after two failed reseeds; rerun only the missing views.
- L-011 `clean-refs-first` · 2026-11-19 · generation notes · Small emblems in references were copied onto the subject. · Clean reference and training pictures before use.
- L-012 `frozen-voice-ref` · 2026-11-19 · voice research · A voice designed from a prompt drifted between renders. · Render one clean reference clip and clone or train from it.
- L-013 `licence-carries-through` · 2026-11-19 · voice research · Non-commercial training data and no-train output clauses carry into the model. · Record base and data licences; `check` gates sellable use.
- L-014 `launch-detached` · 2026-11-19 · generation notes · Long GPU jobs outlived a quiet session. · Launch detached, log to a file, keep the render queue empty.
- L-015 `same-seed-not-same-weights` · 2026-11-19 · proof run (SD1.5, ai-toolkit, 200 steps, seed 42, rerun from the same recipe) · The rerun's weights were not identical (cosine 0.96, final loss 0.010 against 0.023): GPU kernels and caption dropout are not deterministic. Rendered on a fixed sheet, both matched by eye. · Judge a rerun by its outputs on the held-out sheet, never by file hash; record the weight cosine as a drift figure.
- L-016 `comfy-lora-names-backslash` · 2026-11-19 · proof run · ComfyUI on Windows lists LoRAs in subfolders with a backslash (`sub\name.safetensors`); a forward slash returned HTTP 400. · Read the names from /object_info/LoraLoader rather than building them.
- L-017 `perplexity-needs-same-setup` · 2026-11-21 · Cohen 2025 ch. 4 · One model's perplexity fell 800 to 185 by window length alone. · Fix tokens, window, stride and tokenizer; `diff` refuses otherwise.
