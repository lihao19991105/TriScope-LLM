"""Post-analysis for DualScope first-slice clean / poisoned labels."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_label_common import (
    SCHEMA_VERSION,
    read_json,
    read_jsonl,
    validate_labeled_rows,
    write_json,
    write_markdown,
)


REQUIRED_ARTIFACTS = [
    "dualscope_first_slice_label_schema.json",
    "dualscope_first_slice_trigger_contract.json",
    "dualscope_first_slice_target_contract.json",
    "dualscope_first_slice_clean_poisoned_pair_manifest.json",
    "dualscope_first_slice_detection_label_contract.json",
    "dualscope_first_slice_asr_label_contract.json",
    "dualscope_first_slice_utility_label_contract.json",
    "dualscope_first_slice_metric_readiness_summary.json",
    "dualscope_first_slice_clean_poisoned_labeled_slice_summary.json",
    "dualscope_first_slice_clean_poisoned_labeled_slice_details.jsonl",
    "dualscope_first_slice_clean_poisoned_labeled_slice_report.md",
]


def post_clean_poisoned_labeled_slice_analysis(
    label_file: Path,
    build_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    missing_artifacts = [name for name in REQUIRED_ARTIFACTS if not (build_dir / name).exists()]
    summary = read_json(build_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_summary.json")
    manifest = read_json(build_dir / "dualscope_first_slice_clean_poisoned_pair_manifest.json")
    metric_readiness = read_json(build_dir / "dualscope_first_slice_metric_readiness_summary.json")
    rows = read_jsonl(label_file) if label_file.exists() else []
    schema_check = validate_labeled_rows(rows, source_count=manifest.get("source_example_count"))
    labels_ready = (
        not missing_artifacts
        and label_file.exists()
        and summary.get("final_verdict") == "Clean-poisoned labeled slice plan validated"
        and schema_check["summary_status"] == "PASS"
        and metric_readiness.get("labels_ready") is True
        and metric_readiness.get("performance_ready") is False
    )
    if labels_ready:
        verdict = "Clean-poisoned labeled slice plan validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-labels"
    elif rows and schema_check["schema_valid"]:
        verdict = "Partially validated"
        recommendation = "dualscope-first-slice-label-materialization-repair"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-first-slice-label-contract-closure"
    analysis_summary: dict[str, Any] = {
        "summary_status": "PASS" if verdict != "Not validated" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "missing_artifacts": missing_artifacts,
        "label_file": str(label_file),
        "label_file_exists": label_file.exists(),
        "row_count": len(rows),
        "seed": manifest.get("seed"),
        "schema_check": schema_check,
        "labels_ready": labels_ready,
        "performance_ready": False,
        "performance_metrics_reported": False,
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_analysis_summary.json", analysis_summary)
    write_json(
        output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_verdict.json",
        {"summary_status": analysis_summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict},
    )
    write_json(
        output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_next_step_recommendation.json",
        {
            "summary_status": analysis_summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": verdict,
            "recommended_next_step": recommendation,
        },
    )
    write_markdown(
        output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_analysis_report.md",
        "DualScope First-Slice Labeled Slice Analysis",
        [
            f"- Label file exists: `{label_file.exists()}`",
            f"- Row count: `{len(rows)}`",
            f"- Missing artifacts: `{len(missing_artifacts)}`",
            f"- Schema valid: `{schema_check['schema_valid']}`",
            f"- Pairing valid: `{schema_check['pairing_valid']}`",
            f"- Labels ready: `{labels_ready}`",
            "- Performance ready: `false` until real Stage 3 outputs and model responses are aligned.",
            f"- Verdict: `{verdict}`",
            f"- Recommendation: `{recommendation}`",
        ],
    )
    return analysis_summary
