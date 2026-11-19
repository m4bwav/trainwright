# Evaluation against the base

A checkpoint is picked by comparing it with the base model on held-out inputs, never by loss and never by the final step alone. Scores go into the recipe with `tw.py record <recipe> --score name=value --pick <checkpoint>`.

## Image and video LoRAs

1. **Held-out sheet**: 6-12 prompts in `eval.sheet` that are not training captions, fixed seeds.
2. Render the sheet with the **base** and with **each saved checkpoint** (every 100 steps), in the real inference graph: the target model (base or turbo), the sampler and any companion LoRA loaded. Trainer samples skip companion LoRAs and mislead.
3. **Strength-0 control**: the same graph with the LoRA at weight 0. If strength 0 already looks right, the prompt is doing the work, not the LoRA. Then sweep strength (0, 0.6, 0.8, 1.0, 1.2).
4. Lay out a contact sheet: rows = checkpoints, columns = seeds.
5. **Blind ranking** with artwright-judge: pairs in both orders, ties when they disagree, batch rank for many checkpoints. Trust a vision judge's yes and check its no.
6. The owner picks by eye from the top few. Expect the best step early; a later step that looks overcooked confirms the peak.

## Voices

- Render the same held-out lines (not in the training set) with the zero-shot clone, the base and each checkpoint.
- A person listens, blind: shuffled names, A/B pairs, picks recorded on a decision page (askwright). Automated speaker similarity can screen out wrecks but does not pick the winner.
- Listen for drift over long lines, mispronounced names and breath artefacts.

## LLMs

- **lm-evaluation-harness** (EleutherAI): run the same tasks on base and fine-tune (`lm_eval --model hf --model_args pretrained=<path>,peft=<adapter> --tasks <tasks>`) to catch lost general skill.
- A **held-out prompt sheet** from the target task, answered by base and fine-tune, compared blind by a person or a judge model with the order swapped.
- After GGUF quantization, re-run a few prompts: quantization can undo a small fine-tune.

## Record

Every eval names the base, the checkpoint, the seeds and the sheet so a rerun can repeat it. `tw.py diff <a> <b>` compares two recipes' configs and scores.
