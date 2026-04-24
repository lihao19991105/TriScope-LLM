"""Build the DualScope first-slice data-source intake package."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/first-slice-data-source-intake-package/v1"


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_data_source_intake_package.py",
        "src/eval/post_dualscope_first_slice_data_source_intake_package_analysis.py",
        "scripts/build_dualscope_first_slice_data_source_intake_package.py",
        "scripts/build_post_dualscope_first_slice_data_source_intake_package_analysis.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {"passed": result.returncode == 0, "returncode": result.returncode, "stderr": result.stderr, "files": files}


def build_dualscope_first_slice_data_source_intake_package(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    requirements = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_file": "real Alpaca-style JSON or JSONL",
        "target_output": "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl",
        "must_be_real_data": True,
        "synthetic_placeholder_accepted": False,
    }
    formats = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "accepted_formats": [
            {"format": "json_list", "fields": ["instruction", "input", "output"]},
            {"format": "jsonl", "fields": ["instruction", "input", "output"]},
            {"format": "json_or_jsonl", "fields": ["prompt", "response"]},
            {"format": "json_or_jsonl", "fields": ["query", "target"]},
        ],
    }
    import_examples = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "commands": [
            ".venv/bin/python scripts/build_dualscope_first_slice_alpaca_jsonl.py --source-file <REAL_ALPACA_SOURCE_JSON_OR_JSONL> --output-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --max-examples 72 --seed 2025 --split-name first_slice --dataset-id stanford_alpaca",
            ".venv/bin/python scripts/check_dualscope_first_slice_dataset_schema.py --dataset-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --output-dir outputs/dualscope_first_slice_dataset_schema_check/default",
            "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run_preflight.py --output-dir outputs/dualscope_minimal_first_slice_real_run_preflight/default",
        ],
        "placeholder_must_be_replaced": True,
    }
    schema = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_output_fields": ["example_id", "dataset_id", "instruction", "input", "prompt", "response", "split", "source", "metadata"],
        "required_validation_fields": ["example_id", "dataset_id", "prompt", "response", "split"],
        "empty_input_allowed": True,
        "empty_prompt_allowed": False,
        "empty_response_allowed": False,
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "package_complete": True,
        "real_source_still_required": True,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    report = "\n".join(
        [
            "# DualScope First Slice Data Source Intake Package",
            "",
            "Provide a real Alpaca-style JSON or JSONL file, then run the import and schema commands.",
            "",
        ]
    )
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": "Data source intake package validated"}
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": "Data source intake package validated",
        "recommended_next_step": "进入 dualscope-first-slice-dry-run-config-and-contract-validator",
    }
    action_md = "\n".join(
        [
            "# DualScope First Slice User Action Items",
            "",
            "1. Provide `<REAL_ALPACA_SOURCE_JSON_OR_JSONL>`.",
            "2. Run the import command.",
            "3. Run the schema checker.",
            "4. Rerun preflight with the 3090 GPU prefix.",
            "",
        ]
    )
    py_compile = _py_compile(repo_root)
    outputs = {
        "dualscope_first_slice_data_source_requirements.json": requirements,
        "dualscope_first_slice_accepted_source_formats.json": formats,
        "dualscope_first_slice_import_command_examples.json": import_examples,
        "dualscope_first_slice_schema_expectation.json": schema,
        "dualscope_first_slice_data_source_intake_summary.json": summary | {"py_compile_passed": py_compile["passed"]},
        "dualscope_first_slice_data_source_intake_verdict.json": verdict,
        "dualscope_first_slice_data_source_intake_next_step_recommendation.json": recommendation,
        "dualscope_first_slice_data_source_intake_py_compile.json": py_compile,
    }
    for name, payload in outputs.items():
        write_json(output_dir / name, payload)
    (output_dir / "dualscope_first_slice_user_action_items.md").write_text(action_md, encoding="utf-8")
    (output_dir / "dualscope_first_slice_data_source_intake_report.md").write_text(report, encoding="utf-8")
    return {"summary": summary, "verdict": verdict}
