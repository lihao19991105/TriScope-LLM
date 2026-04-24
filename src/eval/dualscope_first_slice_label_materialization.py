"""Materialize available label contracts for DualScope first-slice evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    DATASET_FILE,
    SCHEMA_VERSION,
    markdown,
    read_jsonl,
    run_py_compile,
    write_json,
)


PY_FILES = [
    "src/eval/dualscope_first_slice_label_materialization.py",
    "src/eval/post_dualscope_first_slice_label_materialization_analysis.py",
    "scripts/build_dualscope_first_slice_label_materialization.py",
    "scripts/build_post_dualscope_first_slice_label_materialization_analysis.py",
]


def _candidate_rows(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / "outputs/dualscope_minimal_first_slice_real_run/default/data_slice/first_slice_candidate_queries.jsonl"
    return read_jsonl(path) if path.exists() else []


def build_label_materialization(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    source_rows = read_jsonl(DATASET_FILE)
    candidates = _candidate_rows(repo_root)
    candidate_ids = {row.get("example_id") for row in candidates}
    source_ids = {row.get("example_id") for row in source_rows}
    artifact_labels_available = bool(source_ids and candidate_ids and candidate_ids.issubset(source_ids))
    trigger_annotations_available = all("trigger_family" in row for row in candidates) if candidates else False
    target_annotations_available = all("target_family" in row for row in candidates) if candidates else False
    detection_labels_available = False
    asr_labels_available = False
    utility_labels_available = bool(source_rows and all(row.get("response") for row in source_rows[: min(10, len(source_rows))]))
    py_compile = run_py_compile(repo_root, PY_FILES)
    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-first-slice-label-materialization",
        "dataset_file": str(DATASET_FILE),
        "source_row_count": len(source_rows),
        "candidate_row_count": len(candidates),
        "no_label_fabrication": True,
    }
    available_sources = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "artifact_validation_labels": artifact_labels_available,
        "example_id_alignment": artifact_labels_available,
        "trigger_family_annotations": trigger_annotations_available,
        "target_family_annotations": target_annotations_available,
        "reference_response_for_clean_utility_placeholder": utility_labels_available,
        "clean_poisoned_split_labels": False,
        "backdoor_binary_detection_labels": False,
        "target_behavior_success_labels": False,
        "asr_labels": False,
    }
    label_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "available_contract_labels": [
            "example_id",
            "dataset_id",
            "split",
            "trigger_family_annotation",
            "target_family_annotation",
            "reference_response",
        ],
        "unavailable_performance_labels": [
            "is_backdoored",
            "is_poisoned",
            "clean_or_poisoned_split",
            "target_behavior_success",
            "asr_success",
            "binary_detection_ground_truth",
        ],
        "label_source_policy": "Only externally constructed clean/poisoned/backdoor labels may unlock performance metrics.",
        "do_not_infer_backdoor_truth_from_response": True,
    }
    detection_readiness = {
        "summary_status": "BLOCKED",
        "detection_labels_available": detection_labels_available,
        "blocked_reason": "No legitimate clean/poisoned or backdoor binary label source is present in the current Alpaca first-slice.",
    }
    asr_readiness = {
        "summary_status": "BLOCKED",
        "asr_labels_available": asr_labels_available,
        "blocked_reason": "No poisoned trigger-target construction outputs or target-success annotations are present.",
    }
    utility_readiness = {
        "summary_status": "PARTIAL",
        "utility_reference_available": utility_labels_available,
        "note": "Reference responses exist, but no model utility scoring/judging contract is executed in this stage.",
    }
    metric_readiness = {
        "summary_status": "PARTIAL",
        "artifact_shape_metrics_ready": artifact_labels_available,
        "cost_metrics_ready": True,
        "performance_metrics_ready": detection_labels_available,
        "auroc_ready": False,
        "f1_ready": False,
        "asr_ready": False,
        "clean_utility_ready": False,
        "metric_placeholders_required": True,
    }
    if py_compile["passed"] and artifact_labels_available:
        verdict = "Partially validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback"
    elif py_compile["passed"]:
        verdict = "Partially validated"
        recommendation = "dualscope-first-slice-label-contract-repair"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-first-slice-label-materialization-blocker-closure"
    summary = {
        "summary_status": "PASS" if py_compile["passed"] else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "artifact_validation_labels_available": artifact_labels_available,
        "trigger_annotations_available": trigger_annotations_available,
        "target_annotations_available": target_annotations_available,
        "performance_labels_available": detection_labels_available,
        "metric_placeholders_required": True,
        "py_compile_passed": py_compile["passed"],
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_label_materialization_scope.json", scope)
    write_json(output_dir / "dualscope_first_slice_available_label_sources.json", available_sources)
    write_json(output_dir / "dualscope_first_slice_label_contract.json", label_contract)
    write_json(output_dir / "dualscope_first_slice_detection_label_readiness.json", detection_readiness)
    write_json(output_dir / "dualscope_first_slice_asr_label_readiness.json", asr_readiness)
    write_json(output_dir / "dualscope_first_slice_utility_label_readiness.json", utility_readiness)
    write_json(output_dir / "dualscope_first_slice_metric_readiness_after_label_materialization.json", metric_readiness)
    write_json(output_dir / "dualscope_first_slice_label_materialization_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_first_slice_label_materialization_summary.json", summary)
    markdown(output_dir / "dualscope_first_slice_label_materialization_report.md", "Label Materialization", [
        f"- Artifact validation labels available: `{artifact_labels_available}`",
        f"- Trigger annotations available: `{trigger_annotations_available}`",
        f"- Target annotations available: `{target_annotations_available}`",
        f"- Performance labels available: `{detection_labels_available}`",
        "- No labels were fabricated and no benchmark truth semantics were changed.",
        f"- Verdict: `{verdict}`",
    ])
    write_json(output_dir / "dualscope_first_slice_label_materialization_verdict.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_label_materialization_next_step_recommendation.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    return summary
