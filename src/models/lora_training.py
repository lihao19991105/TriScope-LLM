"""Minimal LoRA finetuning path for TriScope-LLM."""

from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
import yaml
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.models.training_dataset import (
    load_jsonl,
    validate_training_dataset,
)


SUPPORTED_DTYPE_MAP: dict[str, torch.dtype] = {
    "float32": torch.float32,
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
}


@dataclass
class ModelProfile:
    profile_name: str
    model_id: str
    backend_type: str
    dtype: str
    max_length: int
    device: str
    device_map: str | None


@dataclass
class TrainingProfile:
    profile_name: str
    model_profile: str
    train_split: str
    prompt_template: str
    response_template: str
    joiner: str
    append_eos_token: bool
    response_loss_only: bool
    lora_r: int
    lora_alpha: int
    lora_dropout: float
    lora_bias: str
    lora_target_modules: list[str] | str
    per_device_train_batch_size: int
    gradient_accumulation_steps: int
    learning_rate: float
    warmup_ratio: float
    num_train_epochs: float
    max_steps: int
    logging_steps: int
    save_steps: int
    save_total_limit: int
    weight_decay: float
    output_root: str
    gradient_checkpointing: bool
    remove_unused_columns: bool
    bf16: bool
    fp16: bool


@dataclass
class TokenizedExample:
    sample_id: str
    split: str
    is_poisoned: bool
    text: str
    prompt_text: str
    response_text: str
    input_ids: list[int]
    attention_mask: list[int]
    labels: list[int]


@dataclass
class TrainingPlan:
    summary_status: str
    dry_run: bool
    model_profile: dict[str, Any]
    training_profile: dict[str, Any]
    dataset_path: str
    manifest_path: str | None
    num_records: int
    num_selected_records: int
    num_poisoned_selected: int
    train_split: str
    tokenizer_name: str
    max_length: int
    resolved_dtype: str
    resolved_target_modules: list[str]
    device_summary: dict[str, Any]
    output_paths: dict[str, str]
    issues: list[str]


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_yaml_profile(config_path: Path, profile_name: str) -> dict[str, Any]:
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or profile_name not in payload:
        raise ValueError(f"Profile `{profile_name}` not found in `{config_path}`.")
    profile = payload[profile_name]
    if not isinstance(profile, dict):
        raise ValueError(f"Profile `{profile_name}` in `{config_path}` must be a mapping.")
    return profile


def load_model_profile(config_path: Path, profile_name: str) -> ModelProfile:
    profile = load_yaml_profile(config_path=config_path, profile_name=profile_name)
    required_fields = ["model_id", "backend_type", "dtype", "max_length", "device"]
    missing = [field for field in required_fields if field not in profile]
    if missing:
        raise ValueError(
            f"Model profile `{profile_name}` is missing required fields: {', '.join(missing)}."
        )
    return ModelProfile(
        profile_name=profile_name,
        model_id=str(profile["model_id"]),
        backend_type=str(profile["backend_type"]),
        dtype=str(profile["dtype"]),
        max_length=int(profile["max_length"]),
        device=str(profile["device"]),
        device_map=str(profile["device_map"]) if profile.get("device_map") is not None else None,
    )


def load_training_profile(config_path: Path, profile_name: str) -> TrainingProfile:
    profile = load_yaml_profile(config_path=config_path, profile_name=profile_name)
    formatting = profile.get("formatting", {})
    lora = profile.get("lora", {})
    training = profile.get("training", {})
    runtime = profile.get("runtime", {})
    return TrainingProfile(
        profile_name=profile_name,
        model_profile=str(profile.get("model_profile", "reference")),
        train_split=str(profile.get("train_split", "train")),
        prompt_template=str(formatting.get("prompt_template", "{train_prompt}")),
        response_template=str(formatting.get("response_template", "{train_response}")),
        joiner=str(formatting.get("joiner", "\n\n")),
        append_eos_token=bool(formatting.get("append_eos_token", True)),
        response_loss_only=bool(formatting.get("response_loss_only", True)),
        lora_r=int(lora.get("r", 16)),
        lora_alpha=int(lora.get("alpha", 32)),
        lora_dropout=float(lora.get("dropout", 0.05)),
        lora_bias=str(lora.get("bias", "none")),
        lora_target_modules=lora.get("target_modules", "auto"),
        per_device_train_batch_size=int(training.get("per_device_train_batch_size", 1)),
        gradient_accumulation_steps=int(training.get("gradient_accumulation_steps", 4)),
        learning_rate=float(training.get("learning_rate", 2.0e-4)),
        warmup_ratio=float(training.get("warmup_ratio", 0.03)),
        num_train_epochs=float(training.get("num_train_epochs", 1.0)),
        max_steps=int(training.get("max_steps", -1)),
        logging_steps=int(training.get("logging_steps", 1)),
        save_steps=int(training.get("save_steps", 50)),
        save_total_limit=int(training.get("save_total_limit", 1)),
        weight_decay=float(training.get("weight_decay", 0.0)),
        output_root=str(runtime.get("output_root", "outputs/train_runs")),
        gradient_checkpointing=bool(runtime.get("gradient_checkpointing", True)),
        remove_unused_columns=bool(runtime.get("remove_unused_columns", False)),
        bf16=bool(runtime.get("bf16", True)),
        fp16=bool(runtime.get("fp16", False)),
    )


def resolve_dtype(dtype_name: str) -> torch.dtype:
    if dtype_name not in SUPPORTED_DTYPE_MAP:
        supported = ", ".join(sorted(SUPPORTED_DTYPE_MAP))
        raise ValueError(f"Unsupported dtype `{dtype_name}`. Supported values: {supported}.")
    return SUPPORTED_DTYPE_MAP[dtype_name]


def resolve_dataset_records(
    dataset_manifest: Path | None,
    dataset_path: Path | None,
    preview_count: int,
    seed: int,
) -> tuple[list[dict[str, Any]], Path, Path | None, list[str]]:
    validation = validate_training_dataset(
        dataset_path=dataset_path,
        manifest_path=dataset_manifest,
        preview_count=preview_count,
        seed=seed,
    )
    issues = [f"{issue['level']} {issue['code']}: {issue['message']}" for issue in validation.issues]
    if validation.summary_status == "FAIL":
        raise ValueError("Training dataset validation failed:\n" + "\n".join(issues))

    resolved_manifest = dataset_manifest.resolve() if dataset_manifest is not None else None
    resolved_dataset_path = Path(validation.dataset_path).resolve()
    records = load_jsonl(resolved_dataset_path)
    return records, resolved_dataset_path, resolved_manifest, issues


def filter_records_for_split(
    records: list[dict[str, Any]],
    split_name: str,
    max_train_samples: int | None,
) -> list[dict[str, Any]]:
    selected = [record for record in records if record.get("split") == split_name]
    if max_train_samples is not None:
        selected = selected[:max_train_samples]
    if not selected:
        raise ValueError(f"No records available for split `{split_name}`.")
    return selected


def format_training_pair(record: dict[str, Any], profile: TrainingProfile) -> tuple[str, str, str]:
    try:
        prompt_text = profile.prompt_template.format(**record)
        response_text = profile.response_template.format(**record)
    except KeyError as exc:
        raise ValueError(f"Training template references missing field `{exc.args[0]}`.") from exc

    full_text = f"{prompt_text}{profile.joiner}{response_text}"
    return prompt_text, response_text, full_text


def tokenize_records(
    records: list[dict[str, Any]],
    tokenizer: Any,
    model_profile: ModelProfile,
    training_profile: TrainingProfile,
) -> list[TokenizedExample]:
    tokenized: list[TokenizedExample] = []
    for record in records:
        prompt_text, response_text, full_text = format_training_pair(record, training_profile)
        if training_profile.append_eos_token and tokenizer.eos_token and not full_text.endswith(tokenizer.eos_token):
            full_text = f"{full_text}{tokenizer.eos_token}"

        encoded = tokenizer(
            full_text,
            truncation=True,
            max_length=model_profile.max_length,
            add_special_tokens=True,
        )
        labels = list(encoded["input_ids"])
        if training_profile.response_loss_only:
            prompt_encoded = tokenizer(
                f"{prompt_text}{training_profile.joiner}",
                truncation=True,
                max_length=model_profile.max_length,
                add_special_tokens=True,
            )
            prompt_token_count = min(len(prompt_encoded["input_ids"]), len(labels))
            labels[:prompt_token_count] = [-100] * prompt_token_count

        tokenized.append(
            TokenizedExample(
                sample_id=str(record["sample_id"]),
                split=str(record["split"]),
                is_poisoned=bool(record["is_poisoned"]),
                text=full_text,
                prompt_text=prompt_text,
                response_text=response_text,
                input_ids=list(encoded["input_ids"]),
                attention_mask=list(encoded["attention_mask"]),
                labels=labels,
            )
        )
    return tokenized


def infer_lora_target_modules(model: Any) -> list[str]:
    linear_leaf_names = sorted(
        {
            name.split(".")[-1]
            for name, module in model.named_modules()
            if isinstance(module, torch.nn.Linear)
        }
    )
    candidate_sets = [
        ["q_proj", "k_proj", "v_proj", "o_proj"],
        ["q_proj", "v_proj"],
        ["c_attn", "c_proj"],
        ["query_key_value"],
        ["Wqkv"],
    ]
    for candidate_set in candidate_sets:
        resolved = [name for name in candidate_set if name in linear_leaf_names]
        if resolved:
            return resolved
    return linear_leaf_names[:8]


def resolve_target_modules(config_value: list[str] | str, model: Any) -> list[str]:
    if config_value == "auto":
        return infer_lora_target_modules(model)
    if isinstance(config_value, list) and all(isinstance(item, str) for item in config_value):
        return config_value
    raise ValueError("LoRA `target_modules` must be `auto` or a list of module names.")


def build_device_summary() -> dict[str, Any]:
    return {
        "cuda_compiled_version": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "device_names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        if torch.cuda.is_available()
        else [],
    }


def ensure_output_paths(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    return {
        "config_snapshot": output_dir / "config_snapshot.json",
        "training_plan": output_dir / "training_plan.json",
        "run_summary": output_dir / "run_summary.json",
        "dataset_preview": output_dir / "dataset_preview.jsonl",
        "training_log": output_dir / "training.log",
        "adapter_dir": output_dir / "adapter_model",
        "checkpoint_dir": output_dir / "checkpoints" / "checkpoint-final",
        "metrics": output_dir / "train_metrics.json",
        "step_log": output_dir / "step_log.json",
        "reload_preview": output_dir / "reload_preview.jsonl",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_preview(path: Path, examples: list[TokenizedExample], preview_count: int = 3) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for example in examples[:preview_count]:
            handle.write(
                json.dumps(
                    {
                        "sample_id": example.sample_id,
                        "split": example.split,
                        "is_poisoned": example.is_poisoned,
                        "prompt_text": example.prompt_text,
                        "response_text": example.response_text,
                        "sequence_length": len(example.input_ids),
                    },
                    ensure_ascii=True,
                )
                + "\n"
            )


def write_dry_run_preview(
    path: Path,
    records: list[dict[str, Any]],
    training_profile: TrainingProfile,
    preview_count: int = 3,
) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records[:preview_count]:
            prompt_text, response_text, full_text = format_training_pair(record, training_profile)
            handle.write(
                json.dumps(
                    {
                        "sample_id": str(record["sample_id"]),
                        "split": str(record["split"]),
                        "is_poisoned": bool(record["is_poisoned"]),
                        "prompt_text": prompt_text,
                        "response_text": response_text,
                        "formatted_text_chars": len(full_text),
                    },
                    ensure_ascii=True,
                )
                + "\n"
            )


class SupervisedCollator:
    def __init__(self, tokenizer: Any) -> None:
        self.tokenizer = tokenizer

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, torch.Tensor]:
        input_tensors = [torch.tensor(feature["input_ids"], dtype=torch.long) for feature in features]
        mask_tensors = [torch.tensor(feature["attention_mask"], dtype=torch.long) for feature in features]
        label_tensors = [torch.tensor(feature["labels"], dtype=torch.long) for feature in features]
        return {
            "input_ids": torch.nn.utils.rnn.pad_sequence(
                input_tensors,
                batch_first=True,
                padding_value=self.tokenizer.pad_token_id,
            ),
            "attention_mask": torch.nn.utils.rnn.pad_sequence(
                mask_tensors,
                batch_first=True,
                padding_value=0,
            ),
            "labels": torch.nn.utils.rnn.pad_sequence(
                label_tensors,
                batch_first=True,
                padding_value=-100,
            ),
        }


def write_log(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def ensure_runtime_ready(model_profile: ModelProfile, dry_run: bool) -> None:
    if dry_run:
        return
    if model_profile.device.startswith("cuda") and not torch.cuda.is_available():
        raise ValueError(
            "CUDA device was requested by the model profile, but torch.cuda.is_available() is False. "
            "If you are running from the default workspace sandbox, launch the training command outside the sandbox "
            "so the process can access /dev/nvidia*."
        )


def load_tokenizer_for_training(model_id: str) -> Any:
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    except Exception as exc:
        raise ValueError(
            f"Failed to load tokenizer from `{model_id}`. "
            "Provide a valid local model path or a reachable HuggingFace model ID."
        ) from exc
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_model_for_training(model_profile: ModelProfile) -> Any:
    try:
        return AutoModelForCausalLM.from_pretrained(
            model_profile.model_id,
            torch_dtype=resolve_dtype(model_profile.dtype),
        )
    except Exception as exc:
        raise ValueError(
            f"Failed to load causal LM weights from `{model_profile.model_id}`. "
            "For smoke training, prefer a prepared local model path or a reachable small HuggingFace model."
        ) from exc


def build_reload_preview(
    model_profile: ModelProfile,
    adapter_dir: Path,
    tokenizer: Any,
    selected_records: list[dict[str, Any]],
    training_profile: TrainingProfile,
    preview_count: int,
) -> list[dict[str, Any]]:
    base_model = load_model_for_training(model_profile)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    base_model.to(device)
    reloaded_model = PeftModel.from_pretrained(base_model, str(adapter_dir))
    reloaded_model.eval()

    rows: list[dict[str, Any]] = []
    for record in selected_records[:preview_count]:
        prompt_text, _, _ = format_training_pair(record, training_profile)
        encoded = tokenizer(prompt_text, return_tensors="pt", truncation=True, max_length=model_profile.max_length)
        encoded = {key: value.to(device) for key, value in encoded.items()}
        with torch.no_grad():
            generated = reloaded_model.generate(
                **encoded,
                max_new_tokens=24,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        decoded = tokenizer.decode(generated[0], skip_special_tokens=True)
        rows.append(
            {
                "sample_id": str(record["sample_id"]),
                "is_poisoned": bool(record["is_poisoned"]),
                "prompt_text": prompt_text,
                "generated_text": decoded,
            }
        )
    return rows


def build_training_batches(
    examples: list[TokenizedExample],
    tokenizer: Any,
    batch_size: int,
) -> list[dict[str, torch.Tensor]]:
    collator = SupervisedCollator(tokenizer)
    batches: list[dict[str, torch.Tensor]] = []
    for start_index in range(0, len(examples), batch_size):
        chunk = examples[start_index : start_index + batch_size]
        batches.append(
            collator(
                [
                    {
                        "input_ids": example.input_ids,
                        "attention_mask": example.attention_mask,
                        "labels": example.labels,
                    }
                    for example in chunk
                ]
            )
        )
    return batches


def run_minimal_training_loop(
    model: Any,
    batches: list[dict[str, torch.Tensor]],
    training_profile: TrainingProfile,
    device: str,
    save_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    optimizer = torch.optim.AdamW(
        params=[parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=training_profile.learning_rate,
        weight_decay=training_profile.weight_decay,
    )
    model.to(device)
    model.train()
    global_step = 0
    optimizer.zero_grad()
    accumulated_loss = 0.0
    step_log: list[dict[str, Any]] = []
    start_time = time.time()
    target_steps = training_profile.max_steps if training_profile.max_steps > 0 else len(batches)
    max_epochs = max(1, int(round(training_profile.num_train_epochs)))

    for _ in range(max_epochs):
        for batch in batches:
            global_step += 1
            batch = {key: value.to(device) for key, value in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss / training_profile.gradient_accumulation_steps
            loss.backward()
            accumulated_loss += float(outputs.loss.detach().cpu().item())

            if (
                global_step % training_profile.gradient_accumulation_steps == 0
                or global_step >= target_steps
            ):
                optimizer.step()
                optimizer.zero_grad()

            if global_step % training_profile.logging_steps == 0 or global_step == target_steps:
                step_log.append(
                    {
                        "step": global_step,
                        "loss": float(outputs.loss.detach().cpu().item()),
                    }
                )

            if global_step >= target_steps:
                model.save_pretrained(save_dir)
                train_runtime = time.time() - start_time
                metrics = {
                    "global_step": global_step,
                    "train_loss": accumulated_loss / global_step,
                    "train_runtime": train_runtime,
                    "train_samples": len(batches),
                    "train_steps": target_steps,
                }
                return metrics, step_log

    model.save_pretrained(save_dir)
    train_runtime = time.time() - start_time
    metrics = {
        "global_step": global_step,
        "train_loss": (accumulated_loss / global_step) if global_step else 0.0,
        "train_runtime": train_runtime,
        "train_samples": len(batches),
        "train_steps": global_step,
    }
    return metrics, step_log


def run_lora_finetuning(
    dataset_manifest: Path | None,
    dataset_path: Path | None,
    training_config_path: Path,
    training_profile_name: str,
    model_config_path: Path,
    model_profile_name: str | None,
    output_dir: Path,
    seed: int,
    preview_count: int,
    max_train_samples: int | None,
    dry_run: bool,
) -> TrainingPlan:
    set_seed(seed)
    training_profile = load_training_profile(training_config_path, training_profile_name)
    resolved_model_profile_name = model_profile_name or training_profile.model_profile
    model_profile = load_model_profile(model_config_path, resolved_model_profile_name)
    ensure_runtime_ready(model_profile=model_profile, dry_run=dry_run)
    records, resolved_dataset_path, resolved_manifest_path, issues = resolve_dataset_records(
        dataset_manifest=dataset_manifest,
        dataset_path=dataset_path,
        preview_count=preview_count,
        seed=seed,
    )
    selected_records = filter_records_for_split(
        records=records,
        split_name=training_profile.train_split,
        max_train_samples=max_train_samples,
    )

    output_paths = ensure_output_paths(output_dir)

    config_snapshot = {
        "seed": seed,
        "dataset_manifest": str(dataset_manifest) if dataset_manifest else None,
        "dataset_path": str(resolved_dataset_path),
        "training_config_path": str(training_config_path),
        "training_profile": asdict(training_profile),
        "model_config_path": str(model_config_path),
        "model_profile": asdict(model_profile),
        "max_train_samples": max_train_samples,
        "dry_run": dry_run,
    }
    write_json(output_paths["config_snapshot"], config_snapshot)

    resolved_target_modules: list[str] = []
    train_metrics: dict[str, Any] | None = None
    step_log: list[dict[str, Any]] = []
    reload_preview_rows: list[dict[str, Any]] = []

    if dry_run:
        write_dry_run_preview(
            output_paths["dataset_preview"],
            records=selected_records,
            training_profile=training_profile,
            preview_count=preview_count,
        )
        resolved_target_modules = (
            ["auto-resolved-at-train-time"]
            if training_profile.lora_target_modules == "auto"
            else list(training_profile.lora_target_modules)
        )
    else:
        tokenizer = load_tokenizer_for_training(model_profile.model_id)

        tokenized_examples = tokenize_records(
            records=selected_records,
            tokenizer=tokenizer,
            model_profile=model_profile,
            training_profile=training_profile,
        )
        write_preview(output_paths["dataset_preview"], tokenized_examples, preview_count=preview_count)

        model = load_model_for_training(model_profile)
        if training_profile.gradient_checkpointing:
            model.gradient_checkpointing_enable()
            model.config.use_cache = False

        resolved_target_modules = resolve_target_modules(training_profile.lora_target_modules, model)
        lora_config = LoraConfig(
            r=training_profile.lora_r,
            lora_alpha=training_profile.lora_alpha,
            lora_dropout=training_profile.lora_dropout,
            bias=training_profile.lora_bias,
            task_type="CAUSAL_LM",
            target_modules=resolved_target_modules,
        )
        model = get_peft_model(model, lora_config)
        output_paths["checkpoint_dir"].mkdir(parents=True, exist_ok=True)
        train_batches = build_training_batches(
            examples=tokenized_examples,
            tokenizer=tokenizer,
            batch_size=training_profile.per_device_train_batch_size,
        )
        train_metrics, step_log = run_minimal_training_loop(
            model=model,
            batches=train_batches,
            training_profile=training_profile,
            device="cuda" if torch.cuda.is_available() else "cpu",
            save_dir=output_paths["checkpoint_dir"],
        )
        model.save_pretrained(str(output_paths["adapter_dir"]))
        tokenizer.save_pretrained(str(output_paths["adapter_dir"]))
        tokenizer.save_pretrained(str(output_paths["checkpoint_dir"]))
        write_json(output_paths["metrics"], train_metrics)
        write_json(output_paths["step_log"], {"log_history": step_log})
        reload_preview_rows = build_reload_preview(
            model_profile=model_profile,
            adapter_dir=output_paths["adapter_dir"],
            tokenizer=tokenizer,
            selected_records=selected_records,
            training_profile=training_profile,
            preview_count=preview_count,
        )
        write_jsonl(output_paths["reload_preview"], reload_preview_rows)

    plan = TrainingPlan(
        summary_status="PASS",
        dry_run=dry_run,
        model_profile=asdict(model_profile),
        training_profile=asdict(training_profile),
        dataset_path=str(resolved_dataset_path),
        manifest_path=str(resolved_manifest_path) if resolved_manifest_path else None,
        num_records=len(records),
        num_selected_records=len(selected_records),
        num_poisoned_selected=sum(1 for record in selected_records if record.get("is_poisoned") is True),
        train_split=training_profile.train_split,
        tokenizer_name=model_profile.model_id,
        max_length=model_profile.max_length,
        resolved_dtype=model_profile.dtype,
        resolved_target_modules=resolved_target_modules,
        device_summary=build_device_summary(),
        output_paths={name: str(path) for name, path in output_paths.items()},
        issues=issues,
    )
    write_json(output_paths["training_plan"], asdict(plan))
    run_summary = {
        "summary_status": plan.summary_status,
        "dry_run": plan.dry_run,
        "dataset_path": plan.dataset_path,
        "manifest_path": plan.manifest_path,
        "model_id": model_profile.model_id,
        "train_split": plan.train_split,
        "num_selected_records": plan.num_selected_records,
        "num_poisoned_selected": plan.num_poisoned_selected,
        "resolved_target_modules": plan.resolved_target_modules,
        "device_summary": plan.device_summary,
        "train_metrics": train_metrics,
        "step_log_entries": len(step_log),
        "reload_preview_count": len(reload_preview_rows),
        "output_paths": plan.output_paths,
        "issues": plan.issues,
    }
    write_json(output_paths["run_summary"], run_summary)

    log_lines = [
        "TriScope-LLM LoRA finetuning run",
        f"summary_status={plan.summary_status}",
        f"dry_run={plan.dry_run}",
        f"dataset_path={plan.dataset_path}",
        f"manifest_path={plan.manifest_path}",
        f"model_id={model_profile.model_id}",
        f"train_split={plan.train_split}",
        f"num_records={plan.num_records}",
        f"num_selected_records={plan.num_selected_records}",
        f"num_poisoned_selected={plan.num_poisoned_selected}",
        f"device_summary={json.dumps(plan.device_summary, ensure_ascii=True)}",
        f"resolved_target_modules={','.join(plan.resolved_target_modules)}",
        f"run_summary={output_paths['run_summary']}",
    ]
    if train_metrics is not None:
        log_lines.append(f"train_metrics={json.dumps(train_metrics, ensure_ascii=True)}")
    for issue in issues:
        log_lines.append(issue)
    write_log(output_paths["training_log"], log_lines)
    return plan
