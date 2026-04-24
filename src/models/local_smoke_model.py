"""Utilities for creating a tiny local causal LM for smoke training."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import WordLevelTrainer
from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast

from src.models.training_dataset import validate_training_dataset


def _load_records(dataset_manifest: Path | None, dataset_path: Path | None) -> tuple[list[dict[str, Any]], str]:
    validation = validate_training_dataset(
        dataset_path=dataset_path,
        manifest_path=dataset_manifest,
        preview_count=2,
        seed=42,
    )
    if validation.summary_status == "FAIL":
        issues = "\n".join(f"{issue['level']} {issue['code']}: {issue['message']}" for issue in validation.issues)
        raise ValueError(f"Cannot create smoke model from invalid dataset.\n{issues}")

    resolved_path = Path(validation.dataset_path)
    records: list[dict[str, Any]] = []
    with resolved_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            records.append(json.loads(stripped))
    return records, str(resolved_path.resolve())


def _build_tokenizer(records: list[dict[str, Any]], vocab_size: int) -> PreTrainedTokenizerFast:
    tokenizer = Tokenizer(WordLevel(unk_token="<unk>"))
    tokenizer.pre_tokenizer = Whitespace()
    trainer = WordLevelTrainer(
        vocab_size=vocab_size,
        special_tokens=["<pad>", "<bos>", "<eos>", "<unk>"],
    )
    corpus = []
    for record in records:
        corpus.append(str(record["train_prompt"]))
        corpus.append(str(record["train_response"]))
    tokenizer.train_from_iterator(corpus, trainer=trainer)
    fast_tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        pad_token="<pad>",
        bos_token="<bos>",
        eos_token="<eos>",
        unk_token="<unk>",
    )
    return fast_tokenizer


def create_local_smoke_model(
    dataset_manifest: Path | None,
    dataset_path: Path | None,
    output_dir: Path,
    seed: int,
    vocab_size: int,
    n_layer: int,
    n_head: int,
    n_embd: int,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    records, resolved_dataset_path = _load_records(dataset_manifest, dataset_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = _build_tokenizer(records, vocab_size=vocab_size)
    config = GPT2Config(
        vocab_size=len(tokenizer),
        n_positions=256,
        n_ctx=256,
        n_embd=n_embd,
        n_layer=n_layer,
        n_head=n_head,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    model = GPT2LMHeadModel(config)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    summary = {
        "summary_status": "PASS",
        "model_dir": str(output_dir),
        "dataset_path": resolved_dataset_path,
        "seed": seed,
        "vocab_size": len(tokenizer),
        "config": {
            "n_layer": n_layer,
            "n_head": n_head,
            "n_embd": n_embd,
            "max_positions": 256,
        },
    }
    (output_dir / "smoke_model_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return summary
