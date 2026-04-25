"""Build clean / poisoned-triggered labeled pairs for DualScope first slice."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_label_common import (
    LABEL_SOURCE,
    REQUIRED_LABEL_FIELDS,
    SCHEMA_VERSION,
    TARGET_ID,
    TARGET_MATCH_RULE,
    TARGET_TYPE,
    TASK_NAME,
    TRIGGER_ID,
    TRIGGER_INSERT_POSITION,
    TRIGGER_TYPE,
    insert_trigger,
    make_pair_id,
    read_jsonl,
    run_py_compile,
    validate_labeled_rows,
    write_json,
    write_jsonl,
    write_markdown,
)


PY_FILES = [
    "src/eval/dualscope_first_slice_label_common.py",
    "src/eval/dualscope_first_slice_clean_poisoned_labeled_slice.py",
    "src/eval/post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py",
    "scripts/build_dualscope_first_slice_clean_poisoned_labeled_slice.py",
    "scripts/build_post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py",
]


def _metadata(source_row: dict[str, Any], seed: int, row_role: str) -> dict[str, Any]:
    source_metadata = source_row.get("metadata")
    return {
        "seed": seed,
        "row_role": row_role,
        "source_split": source_row.get("split"),
        "source_index": source_metadata.get("source_index") if isinstance(source_metadata, dict) else None,
        "label_policy": "experimental construction labels; not benchmark truth; not inferred from model outputs",
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "model_output_fabricated": False,
    }


def build_labeled_rows(
    source_rows: list[dict[str, Any]],
    trigger_text: str,
    target_text: str,
    seed: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, source_row in enumerate(source_rows):
        source_example_id = str(source_row.get("example_id") or f"source_{index:05d}")
        dataset_id = str(source_row.get("dataset_id") or "stanford_alpaca")
        pair_id = make_pair_id(index, source_example_id)
        clean_prompt = str(source_row.get("prompt") or source_row.get("instruction") or "")
        response_reference = str(source_row.get("response") or "")

        base_fields = {
            "pair_id": pair_id,
            "source_example_id": source_example_id,
            "dataset_id": dataset_id,
            "response_reference": response_reference,
            "trigger_id": TRIGGER_ID,
            "trigger_text": trigger_text,
            "trigger_insert_position": TRIGGER_INSERT_POSITION,
            "target_id": TARGET_ID,
            "target_type": TARGET_TYPE,
            "target_text": target_text,
            "target_match_rule": TARGET_MATCH_RULE,
            "label_source": LABEL_SOURCE,
        }

        rows.append(
            {
                **base_fields,
                "row_id": f"{pair_id}__clean",
                "condition": "clean",
                "prompt": clean_prompt,
                "trigger_present": False,
                "detection_label": 0,
                "asr_eligible": False,
                "utility_eligible": True,
                "metadata": _metadata(source_row, seed, "clean"),
            }
        )
        rows.append(
            {
                **base_fields,
                "row_id": f"{pair_id}__poisoned_triggered",
                "condition": "poisoned_triggered",
                "prompt": insert_trigger(clean_prompt, trigger_text, TRIGGER_INSERT_POSITION),
                "trigger_present": True,
                "detection_label": 1,
                "asr_eligible": True,
                "utility_eligible": False,
                "metadata": _metadata(source_row, seed, "poisoned_triggered"),
            }
        )
    return rows


def build_clean_poisoned_labeled_slice(
    source_file: Path,
    output_file: Path,
    output_dir: Path,
    trigger_text: str,
    target_text: str,
    seed: int,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    source_rows = read_jsonl(source_file)
    labeled_rows = build_labeled_rows(source_rows, trigger_text=trigger_text, target_text=target_text, seed=seed)
    schema_validation = validate_labeled_rows(labeled_rows, source_count=len(source_rows))
    py_compile = run_py_compile(repo_root, PY_FILES)
    write_jsonl(output_file, labeled_rows)

    label_schema = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "label_file": str(output_file),
        "required_fields": REQUIRED_LABEL_FIELDS,
        "conditions": ["clean", "poisoned_triggered"],
        "label_source": LABEL_SOURCE,
        "labels_are_experimental_construction": True,
        "labels_inferred_from_model_outputs": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
    }
    trigger_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "trigger_type": TRIGGER_TYPE,
        "trigger_id": TRIGGER_ID,
        "trigger_text": trigger_text,
        "trigger_insert_position": TRIGGER_INSERT_POSITION,
        "trigger_policy": "lexical trigger inserted deterministically into poisoned_triggered prompts only",
        "prompt_family_expanded": False,
    }
    target_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "target_type": TARGET_TYPE,
        "target_id": TARGET_ID,
        "target_text": target_text,
        "target_match_rule": TARGET_MATCH_RULE,
        "target_policy": "fixed response target for ASR matching on poisoned_triggered rows",
        "target_family_expanded": False,
    }
    manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "source_file": str(source_file),
        "output_file": str(output_file),
        "source_example_count": len(source_rows),
        "labeled_row_count": len(labeled_rows),
        "pair_count": len(source_rows),
        "clean_row_count": sum(1 for row in labeled_rows if row["condition"] == "clean"),
        "poisoned_triggered_row_count": sum(1 for row in labeled_rows if row["condition"] == "poisoned_triggered"),
        "seed": seed,
    }
    detection_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "detection_label_field": "detection_label",
        "negative_condition": "clean",
        "negative_label": 0,
        "positive_condition": "poisoned_triggered",
        "positive_label": 1,
        "auroc_requires": ["detection_label", "final_risk_score", "row_id_or_pair_id_alignment"],
        "f1_requires": ["detection_label", "thresholded_final_prediction", "row_id_or_pair_id_alignment"],
        "performance_ready_without_stage3_outputs": False,
    }
    asr_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "asr_eligible_field": "asr_eligible",
        "target_text_field": "target_text",
        "target_match_rule": TARGET_MATCH_RULE,
        "asr_requires": ["asr_eligible", "target_text", "model_response", "row_id_alignment"],
        "asr_ready_without_model_responses": False,
    }
    utility_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "utility_eligible_field": "utility_eligible",
        "reference_response_field": "response_reference",
        "clean_utility_requires": ["utility_eligible", "clean_model_response", "response_reference", "utility_scoring_contract"],
        "utility_ready_without_clean_model_responses": False,
    }
    metric_readiness = {
        "summary_status": "PASS" if schema_validation["summary_status"] == "PASS" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "labels_ready": schema_validation["summary_status"] == "PASS",
        "detection_labels_ready": schema_validation["summary_status"] == "PASS",
        "asr_labels_ready": schema_validation["summary_status"] == "PASS",
        "utility_labels_ready": schema_validation["summary_status"] == "PASS",
        "performance_ready": False,
        "auroc_ready": False,
        "f1_ready": False,
        "asr_ready": False,
        "clean_utility_ready": False,
        "reason": "Labels are ready, but performance metrics require aligned real Stage 3 outputs and model responses.",
    }
    if schema_validation["summary_status"] == "PASS" and py_compile["passed"]:
        verdict = "Clean-poisoned labeled slice plan validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-labels"
    elif py_compile["passed"]:
        verdict = "Partially validated"
        recommendation = "dualscope-first-slice-label-materialization-repair"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-first-slice-label-contract-closure"

    summary = {
        "summary_status": "PASS" if verdict != "Not validated" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
        "source_example_count": len(source_rows),
        "labeled_row_count": len(labeled_rows),
        "pair_count": len(source_rows),
        "schema_valid": schema_validation["schema_valid"],
        "pairing_valid": schema_validation["pairing_valid"],
        "py_compile_passed": py_compile["passed"],
        "labels_are_experimental_construction": True,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "model_outputs_fabricated": False,
        "performance_metrics_reported": False,
    }
    details = [
        {"detail_type": "label_schema", "payload": label_schema},
        {"detail_type": "trigger_contract", "payload": trigger_contract},
        {"detail_type": "target_contract", "payload": target_contract},
        {"detail_type": "schema_validation", "payload": schema_validation},
        {"detail_type": "metric_readiness", "payload": metric_readiness},
    ]

    write_json(output_dir / "dualscope_first_slice_label_schema.json", label_schema)
    write_json(output_dir / "dualscope_first_slice_trigger_contract.json", trigger_contract)
    write_json(output_dir / "dualscope_first_slice_target_contract.json", target_contract)
    write_json(output_dir / "dualscope_first_slice_clean_poisoned_pair_manifest.json", manifest)
    write_json(output_dir / "dualscope_first_slice_detection_label_contract.json", detection_contract)
    write_json(output_dir / "dualscope_first_slice_asr_label_contract.json", asr_contract)
    write_json(output_dir / "dualscope_first_slice_utility_label_contract.json", utility_contract)
    write_json(output_dir / "dualscope_first_slice_metric_readiness_summary.json", metric_readiness)
    write_json(output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_schema_check.json", schema_validation)
    write_json(output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_py_compile.json", py_compile)
    write_jsonl(output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_details.jsonl", details)
    write_markdown(
        output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_report.md",
        "DualScope First-Slice Clean / Poisoned Labeled Slice",
        [
            f"- Source examples: `{len(source_rows)}`",
            f"- Labeled rows: `{len(labeled_rows)}`",
            f"- Trigger: `{TRIGGER_ID}` / `{trigger_text}`",
            f"- Target: `{TARGET_ID}` / `{target_text}`",
            f"- Labels ready: `{metric_readiness['labels_ready']}`",
            "- Labels are experimental construction labels, not benchmark truth.",
            "- No model outputs were fabricated and no performance metrics were reported.",
            f"- Verdict: `{verdict}`",
            f"- Recommendation: `{recommendation}`",
        ],
    )
    return summary
