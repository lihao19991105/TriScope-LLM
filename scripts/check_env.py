#!/usr/bin/env python3
"""Bootstrap environment check for TriScope-LLM."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    metadata: dict[str, Any]


DEPENDENCY_SPECS: list[tuple[str, str]] = [
    ("transformers", "transformers"),
    ("peft", "peft"),
    ("accelerate", "accelerate"),
    ("datasets", "datasets"),
    ("sklearn", "scikit-learn"),
    ("pandas", "pandas"),
    ("matplotlib", "matplotlib"),
    ("yaml", "PyYAML"),
    ("tqdm", "tqdm"),
]

EXPECTED_CONFIGS = ["models.yaml", "attacks.yaml", "detection.yaml"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check the local environment for the TriScope-LLM bootstrap stage.",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path("configs"),
        help="Directory containing the bootstrap YAML configuration files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/check_env"),
        help="Directory where environment check artifacts will be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed recorded in the output metadata for reproducibility.",
    )
    return parser


def import_version(module_name: str) -> str | None:
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None

    version = getattr(module, "__version__", None)
    if version is None and module_name == "yaml":
        version = getattr(module, "version", None)
    return str(version) if version is not None else "unknown"


def check_python_version() -> CheckResult:
    version_info = sys.version_info
    meets_requirement = version_info >= (3, 10)
    status = "PASS" if meets_requirement else "FAIL"
    detail = (
        f"Python {platform.python_version()} detected; "
        f"{'meets' if meets_requirement else 'does not meet'} the >= 3.10 requirement."
    )
    return CheckResult(
        name="python",
        status=status,
        detail=detail,
        metadata={
            "version": platform.python_version(),
            "executable": sys.executable,
            "required_minimum": "3.10",
        },
    )


def check_dependency(module_name: str, package_name: str) -> CheckResult:
    version = import_version(module_name)
    if version is None:
        return CheckResult(
            name=package_name,
            status="FAIL",
            detail=f"Missing dependency: import `{module_name}` failed.",
            metadata={"module_name": module_name},
        )

    return CheckResult(
        name=package_name,
        status="PASS",
        detail=f"Dependency available via `{module_name}` (version: {version}).",
        metadata={"module_name": module_name, "version": version},
    )


def check_configs(config_dir: Path) -> CheckResult:
    missing = [name for name in EXPECTED_CONFIGS if not (config_dir / name).is_file()]
    if missing:
        return CheckResult(
            name="configs",
            status="WARN",
            detail=(
                f"Config directory found at `{config_dir}`, but some expected files are missing: "
                + ", ".join(missing)
            ),
            metadata={"config_dir": str(config_dir), "missing_files": missing},
        )

    return CheckResult(
        name="configs",
        status="PASS",
        detail=f"All expected bootstrap config files are present in `{config_dir}`.",
        metadata={"config_dir": str(config_dir), "files": EXPECTED_CONFIGS},
    )


def check_torch_and_cuda() -> list[CheckResult]:
    try:
        torch = importlib.import_module("torch")
    except Exception as exc:
        return [
            CheckResult(
                name="torch",
                status="FAIL",
                detail=f"PyTorch is not available: {exc}",
                metadata={},
            ),
            CheckResult(
                name="cuda",
                status="WARN",
                detail="CUDA checks skipped because PyTorch is not installed.",
                metadata={},
            ),
        ]

    results: list[CheckResult] = [
        CheckResult(
            name="torch",
            status="PASS",
            detail=f"PyTorch available (version: {torch.__version__}).",
            metadata={
                "torch_version": torch.__version__,
                "cuda_version": getattr(torch.version, "cuda", None),
            },
        )
    ]

    cuda_available = bool(torch.cuda.is_available())
    gpu_count = int(torch.cuda.device_count()) if cuda_available else 0

    if cuda_available:
        gpu_names = [torch.cuda.get_device_name(i) for i in range(gpu_count)]
        results.append(
            CheckResult(
                name="cuda",
                status="PASS",
                detail=(
                    f"CUDA is available (torch CUDA: {torch.version.cuda}); "
                    f"detected {gpu_count} GPU(s)."
                ),
                metadata={
                    "cuda_version": torch.version.cuda,
                    "gpu_count": gpu_count,
                    "gpu_names": gpu_names,
                },
            )
        )
    else:
        results.append(
            CheckResult(
                name="cuda",
                status="WARN",
                detail="CUDA is not available. GPU-backed runs will not be possible in this environment.",
                metadata={
                    "cuda_version": getattr(torch.version, "cuda", None),
                    "gpu_count": 0,
                    "gpu_names": [],
                },
            )
        )

    return results


def summarize(results: list[CheckResult]) -> str:
    has_fail = any(result.status == "FAIL" for result in results)
    has_warn = any(result.status == "WARN" for result in results)
    if has_fail:
        return "FAIL"
    if has_warn:
        return "WARN"
    return "PASS"


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def write_json_report(
    output_dir: Path,
    config_dir: Path,
    seed: int,
    summary_status: str,
    results: list[CheckResult],
) -> Path:
    report_path = output_dir / "environment_report.json"
    payload = {
        "summary_status": summary_status,
        "seed": seed,
        "python_executable": sys.executable,
        "config_dir": str(config_dir),
        "results": [asdict(result) for result in results],
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return report_path


def print_report(summary_status: str, results: list[CheckResult], report_path: Path) -> None:
    print("TriScope-LLM Environment Check")
    print("=" * 31)
    for result in results:
        print(f"[{result.status}] {result.name}: {result.detail}")

    torch_result = next((result for result in results if result.name == "torch"), None)
    cuda_result = next((result for result in results if result.name == "cuda"), None)
    if torch_result and torch_result.status == "PASS":
        print("")
        print("Torch Summary")
        print("-" * 13)
        print(f"torch version: {torch_result.metadata.get('torch_version', 'unknown')}")
        print(f"CUDA version: {torch_result.metadata.get('cuda_version', 'unknown')}")
        if cuda_result:
            print(f"GPU count: {cuda_result.metadata.get('gpu_count', 0)}")
            gpu_names = cuda_result.metadata.get("gpu_names", [])
            for index, name in enumerate(gpu_names):
                print(f"GPU {index}: {name}")

    print("")
    print(f"Overall status: {summary_status}")
    if summary_status == "PASS":
        print("Environment looks ready for the bootstrap stage.")
    elif summary_status == "WARN":
        print("Environment is partially ready, but some optional or hardware-dependent checks need attention.")
    else:
        print("Environment is not ready for the bootstrap stage. Please address the failing checks above.")
    print(f"Structured report: {report_path}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    results: list[CheckResult] = [check_python_version(), check_configs(args.config_dir)]
    results.extend(check_torch_and_cuda())
    results.extend(
        check_dependency(module_name=module_name, package_name=package_name)
        for module_name, package_name in DEPENDENCY_SPECS
    )

    summary_status = summarize(results)
    ensure_output_dir(args.output_dir)
    report_path = write_json_report(
        output_dir=args.output_dir,
        config_dir=args.config_dir,
        seed=args.seed,
        summary_status=summary_status,
        results=results,
    )
    print_report(summary_status=summary_status, results=results, report_path=report_path)

    return 0 if summary_status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
