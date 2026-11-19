# Ship

Put the picked checkpoint where it will be used, with its recipe beside it.

## LoRAs (image, video)

- Copy the pick into the generator's `models/loras` folder under a step-suffixed name: `<run>-s<step>.safetensors`. Never overwrite a LoRA a running ComfyUI has loaded (Windows locks memory-mapped files).
- Copy the recipe JSON next to it (`<run>-s<step>.recipe.json`) so anyone can see the base, data, licence and scores.
- Record the shipped file name in the recipe: `tw.py record <recipe> --pick <step> --files <path>`.

## LLMs to GGUF and Ollama (unverified until a first run)

1. Merge the adapter into a 16-bit base: Unsloth `model.save_pretrained_merged(dir, tokenizer, save_method="merged_16bit")`, or PEFT `merge_and_unload()` on a bf16 load.
2. Convert: `python llama.cpp/convert_hf_to_gguf.py <merged-dir> --outfile <name>-f16.gguf --outtype f16`.
3. Quantize: `llama-quantize <name>-f16.gguf <name>-Q4_K_M.gguf Q4_K_M` (Q5_K_M or Q8_0 for more quality).
4. Modelfile:
   ```
   FROM ./<name>-Q4_K_M.gguf
   TEMPLATE """<the base's chat template>"""
   PARAMETER temperature 0.7
   ```
   Or keep the base and ship only the adapter: convert with `convert_lora_to_gguf.py`, then `FROM <base>` plus `ADAPTER ./<adapter>.gguf`.
5. `ollama create <name> -f Modelfile`, then `ollama run <name>` on two held-out prompts.
6. Unsloth can do steps 1-3 in one call (`save_pretrained_gguf`); check the output with step 5 anyway.

On Windows, call Ollama at `127.0.0.1`, not `localhost`: `localhost` may resolve to IPv6 first while Ollama listens on IPv4.

AWQ and other GPU quantizations matter only for vLLM-style serving; GGUF is the route for Ollama.

## Voices

Ship the checkpoint plus one rendered reference clip and the recipe into the voice tool's model folder; voicewright uses it from there.

## Licence label

Copy the recipe's licence verdict into the shipped folder's name or notes when it is non-commercial, so it never lands in a sellable project by accident.
