# Small LLM fine-tune

QLoRA on a 16 GB GPU. Using local models belongs to local-delegate; cloud training on HF Jobs is the Hugging Face model-trainer skill. Smoke-proven 2026-11-27: Unsloth QLoRA of Qwen2.5-0.5B-Instruct, 20 steps in 30 s, learned the trigger format (L-020).

## Trainer choice

| Trainer | Notes | 16 GB fit (unverified) |
|---|---|---|
| Unsloth | fastest, Windows supported, exports GGUF | 7-8B 4-bit QLoRA comfortable; up to about 14B tight |
| TRL (`SFTTrainer`) + PEFT + bitsandbytes | plain Hugging Face stack, SFT/DPO/GRPO | 7-8B with 4-bit |
| Axolotl | YAML-driven; Linux or WSL first | 7-8B QLoRA |

Prefer an ungated base (Qwen, Mistral, Gemma, Phi family) and read its licence; a gated or restrictive base licence carries to the fine-tune.

## Starting settings

rank 16, alpha 16-32, lr 2e-4, batch 2 with grad accumulation 4-8, max sequence 2,048, 1-3 epochs, `save_every: 100`, seed fixed, 4-bit base (`quant: nf4`). A few hundred to a few thousand clean examples beat many noisy ones.

## Mapping (Unsloth smoke-proven; TRL and Axolotl unproven)

`tw.py config --trainer unsloth|trl` writes neutral JSON. Map it:

| recipe `config` | Unsloth / TRL |
|---|---|
| rank / alpha | `get_peft_model(r=, lora_alpha=)` / `LoraConfig(r=, lora_alpha=)` |
| lr | `SFTConfig(learning_rate=)` |
| steps | `max_steps` (or `num_train_epochs`) |
| batch / grad_accum | `per_device_train_batch_size` / `gradient_accumulation_steps` |
| save_every | `save_steps` with `save_strategy="steps"` |
| seed | `seed` |
| quant nf4 | `load_in_4bit=True` (Unsloth) / `BitsAndBytesConfig(load_in_4bit=True)` |
| base / dataset | `model_name` / `load_dataset("json", data_files=...)` |

For Axolotl the same keys sit in its YAML: `lora_r`, `lora_alpha`, `learning_rate`, `max_steps`, `micro_batch_size`, `gradient_accumulation_steps`, `save_steps`, `seed`, `load_in_4bit`.

## Pitfalls

- Use the base's own chat template for training and inference; a mismatch looks like a broken fine-tune.
- Batched padding needs the attention mask, padded positions left out of the loss, and a pad token (GPT-style tokenizers often have none); without the mask losses are quietly wrong.
- Call `model.eval()` before scoring: dropout left on gives noisy, unrepeatable numbers.
- Hold out 5-10 % of examples and evaluate base vs fine-tune on them ([eval.md](eval.md)); a falling loss alone proves nothing.
- Same-name output folders resume from the last checkpoint in most trainers: use a new run name.
- Merge the adapter into a 16-bit copy of the base before GGUF conversion, not into the 4-bit one ([ship.md](ship.md)).
