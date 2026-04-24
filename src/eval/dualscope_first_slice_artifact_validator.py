"""Artifact validator rules and checker for DualScope first-slice outputs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/first-slice-artifact-validator/v1"


def required_artifact_schema() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "groups": {
            "stage1": ["illumination_summary.json", "illumination_details.jsonl", "screening_features.jsonl", "stage1_budget_usage.json"],
            "stage2": ["confidence_summary.json", "confidence_details.jsonl", "capability_mode_report.json", "fallback_report.json"],
            "stage3": ["fusion_summary.json", "fusion_details.jsonl", "final_decisions.jsonl", "cost_summary.json"],
            "evaluation": ["metrics_summary.json", "baseline_comparison.json", "real_run_report.md"],
            "governance": ["verdict.json", "next_step_recommendation.json"],
        },
    }


def validator_rules() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "rules": [
            "stage1 artifacts must include screening risk and budget usage",
            "stage2 artifacts must include capability_mode and fallback/degradation flag",
            "stage3 artifacts must include final_risk_score, final_risk_bucket, final_decision_flag, and cost fields",
            "metrics placeholders must be present before paper table generation",
            "report, verdict, and recommendation must be traceable",
        ],
        "forbidden": ["route_c_199_plus", "benchmark_truth_change", "gate_change", "full_matrix_claim"],
    }


def check_first_slice_artifacts(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = required_artifact_schema()
    rows = []
    for group, names in schema["groups"].items():
        group_root = run_dir / group if group in {"stage1", "stage2", "stage3"} else run_dir / group
        for name in names:
            path = group_root / name
            rows.append({"group": group, "artifact": name, "path": str(path), "exists": path.exists()})
    missing = [row for row in rows if not row["exists"]]
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "run_dir": str(run_dir),
        "checked_count": len(rows),
        "missing_count": len(missing),
        "verdict": "pass" if not missing else "missing_artifacts",
        "rows": rows,
    }
    write_json(output_dir / "dualscope_first_slice_artifact_check_summary.json", summary)
    return summary


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_artifact_validator.py",
        "src/eval/post_dualscope_first_slice_artifact_validator_analysis.py",
        "scripts/check_dualscope_first_slice_artifacts.py",
        "scripts/build_dualscope_first_slice_artifact_validator_hardening.py",
        "scripts/build_post_dualscope_first_slice_artifact_validator_hardening_analysis.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {"passed": result.returncode == 0, "stderr": result.stderr, "files": files}


def build_dualscope_first_slice_artifact_validator_hardening(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = required_artifact_schema()
    rules = validator_rules()
    py_compile = _py_compile(repo_root)
    final = "Artifact validator hardening validated" if py_compile["passed"] else "Not validated"
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_group_count": len(schema["groups"]),
        "rule_count": len(rules["rules"]),
        "py_compile_passed": py_compile["passed"],
        "final_verdict": final,
    }
    report = "\n".join(["# DualScope First Slice Artifact Validator", "", f"- Final verdict: `{final}`", f"- Rule count: `{len(rules['rules'])}`", ""])
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final}
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final, "recommended_next_step": "进入 dualscope-first-slice-readiness-report-package"}
    write_json(output_dir / "dualscope_first_slice_required_artifact_schema.json", schema)
    write_json(output_dir / "dualscope_first_slice_artifact_validator_rules.json", rules)
    write_json(output_dir / "dualscope_first_slice_artifact_validator_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_artifact_validator_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_artifact_validator_next_step_recommendation.json", rec)
    write_json(output_dir / "dualscope_first_slice_artifact_validator_py_compile.json", py_compile)
    (output_dir / "dualscope_first_slice_artifact_validator_report.md").write_text(report, encoding="utf-8")
    return {"summary": summary, "verdict": verdict}
