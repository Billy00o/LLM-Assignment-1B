import os
from contextlib import nullcontext
from functools import partial
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "runtime" / "cache" / "official"
MODEL_ID = "google/gemma-2b-it"
MODEL_REVISION = "96988410cbdaeb8d5093d1ebdc5a8fb563e02bad"
CHECKPOINT = CACHE / "models--google--gemma-2b-it" / "snapshots" / MODEL_REVISION
WEIGHT_SHARDS = {
    "model-00001-of-00002.safetensors": (4945242264, "561656f892a2a1ca0837ca529c5ce820a72b40f4f563b1cd0a1acc0b3899c30c"),
    "model-00002-of-00002.safetensors": (67121608, "20fe2ee66bf1361241a6c522091a5e0328fc6c1703f93734889fa381fcf8760c"),
}
CHECKPOINT_FILES = ("config.json", "generation_config.json", "model.safetensors.index.json",
                    "special_tokens_map.json", "tokenizer_config.json", "tokenizer.json", "tokenizer.model")
MODES = {
    "general": "Answer the student's question clearly and concisely.",
    "explain": "Explain this topic simply, then give one short example.",
    "quiz": "Write one practice question about this topic. Do not give its answer yet.",
}


def check_checkpoint():
    incomplete = [name for name in CHECKPOINT_FILES if not (CHECKPOINT / name).is_file()]
    for name, (size, _) in WEIGHT_SHARDS.items():
        shard = CHECKPOINT / name
        if not shard.is_file() or shard.stat().st_size != size:
            incomplete.append(name)
    if incomplete:
        raise FileNotFoundError("Gemma checkpoint incomplete: " + ", ".join(incomplete)
                                + ". Run python preflight.py --download.")


def load_model():
    check_checkpoint()
    import torch
    from safetensors import safe_open
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(min(8, os.cpu_count() or 1))
    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT, local_files_only=True)
    reader = (patch("transformers.modeling_utils.safe_open", partial(safe_open, backend="pread"))
              if os.name == "nt" else nullcontext())
    print("Loading Google's Gemma 2B IT on CPU (BF16)...", flush=True)
    with reader:
        model = AutoModelForCausalLM.from_pretrained(CHECKPOINT, dtype=torch.bfloat16,
                                                    local_files_only=True)
    model.eval()
    return model, tokenizer


def build_messages(prompt, history=None, mode="general"):
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Enter a non-empty question.")
    if mode not in MODES:
        raise ValueError("Unknown study mode.")
    messages = [dict(item) for item in (history or [])]
    if len(messages) % 2 or any(m.get("role") != ("user" if i % 2 == 0 else "assistant")
                               or not isinstance(m.get("content"), str)
                               for i, m in enumerate(messages)):
        raise ValueError("History must contain complete user/assistant turns.")
    messages.append({"role": "user", "content": MODES[mode] + "\n\n" + prompt.strip()})
    return messages


def get_response(prompt, model, tokenizer, max_length=128, *, history=None, mode="general"):
    import torch

    if not isinstance(max_length, int) or not 1 <= max_length <= 1024:
        raise ValueError("Output limit must be 1..1024 tokens.")
    messages = build_messages(prompt, history, mode)
    inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                           return_dict=True, return_tensors="pt")
    prompt_length = inputs["input_ids"].shape[-1]
    if prompt_length + max_length > model.config.max_position_embeddings:
        raise ValueError("Conversation is too long. Use /reset or shorten your question.")
    with torch.inference_mode():
        output = model.generate(**inputs, do_sample=False, max_new_tokens=max_length)
    reply = tokenizer.decode(output[0, prompt_length:], skip_special_tokens=True).strip()
    if not reply:
        raise RuntimeError("Model returned an empty response.")
    return reply
