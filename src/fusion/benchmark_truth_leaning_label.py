"""Bootstrap a benchmark-truth-leaning supervised fusion path from contract-level answer correctness."""

from __future__ import annotations

from collections import Counter
import re
import unicodedata
from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.fusion.labeled_real_pilot_fusion import (
    CONFIDENCE_NUMERIC_COLUMNS,
    ILLUMINATION_NUMERIC_COLUMNS,
    REASONING_NUMERIC_COLUMNS,
    load_jsonl,
    write_csv,
    write_json,
    write_jsonl,
)


SCHEMA_VERSION = "triscopellm/benchmark-truth-leaning-label/v1"
OPTION_LABEL_PATTERN = re.compile(r"\b([A-D])\b")
ROBUST_PREFIX_OPTION_PATTERN = re.compile(r"^\s*([A-D])(?=Human:|Assistant:|[^A-Za-z0-9_]|$)")
ALNUM_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
PREFIX_NOISE_PATTERN = re.compile(
    r"^\s*(?:label|answer|option|prediction|predict|pred|result|output|response|预测|答案|选项)\s*[:：-]\s*",
    flags=re.IGNORECASE,
)
BULLET_PREFIX_PATTERN = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s*")
LEADING_TRAILING_PUNCT_PATTERN = re.compile(r"^[\s\W_]+|[\s\W_]+$")
PUNCT_ONLY_PATTERN = re.compile(r"^[\W_]+$")
POTENTIAL_JSON_PATTERN = re.compile(r"^\s*[\[{].*[\]}]\s*$", flags=re.DOTALL)
MARKDOWN_CODE_FENCE_LANGUAGE_TAG_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

FAILURE_CATEGORIES = [
    "empty",
    "whitespace_only",
    "punct_only",
    "quote_wrapped_label",
    "bracket_wrapped_label",
    "prefix_suffix_noise",
    "json_like_but_unparsed",
    "unknown_token",
    "multi_label_ambiguous",
    "label_not_in_set",
    "parser_exception",
    "other",
]

QUOTE_WRAPPERS = [("\"", "\""), ("'", "'"), ("`", "`"), ("“", "”"), ("‘", "’")]
BRACKET_WRAPPERS = [
    ("(", ")"),
    ("[", "]"),
    ("{", "}"),
    ("（", "）"),
    ("【", "】"),
    ("「", "」"),
    ("『", "』"),
]
PUNCT_TRANSLATION_TABLE = str.maketrans(
    {
        "，": ",",
        "。": ".",
        "：": ":",
        "；": ";",
        "！": "!",
        "？": "?",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "、": ",",
    }
)

ANTI_DEGRADATION_ALLOWED_FORMAT_STEPS = {
    "unicode_nfkc",
    "punctuation_normalized",
    "markdown_code_fence_removed",
    "bullet_prefix_removed",
    "prefix_noise_removed",
    "quote_wrapper_removed",
    "bracket_wrapper_removed",
    "edge_punctuation_trimmed",
}


def extract_option_label(text: str, parse_mode: str = "strict") -> str | None:
    if parse_mode not in {"strict", "robust_prefix"}:
        raise ValueError(f"Unsupported parse_mode `{parse_mode}`.")

    if parse_mode == "robust_prefix":
        prefix_match = ROBUST_PREFIX_OPTION_PATTERN.search(text)
        if prefix_match is not None:
            return prefix_match.group(1)

    match = OPTION_LABEL_PATTERN.search(text)
    return match.group(1) if match is not None else None


def _extract_label_candidates(text: str, parse_mode: str, allowed_labels: set[str]) -> tuple[list[str], str]:
    candidates: list[str] = []
    if parse_mode == "robust_prefix":
        prefix_match = ROBUST_PREFIX_OPTION_PATTERN.search(text)
        if prefix_match is not None:
            prefix_label = prefix_match.group(1).upper()
            if prefix_label in allowed_labels:
                return [prefix_label], "robust_prefix"

    for token in ALNUM_TOKEN_PATTERN.findall(text.upper()):
        if token in allowed_labels:
            candidates.append(token)
    unique_candidates = sorted(set(candidates))
    return unique_candidates, "token_scan"


def _unwrap_markdown_code_fence(text: str) -> str | None:
    stripped = text.strip()
    if not (stripped.startswith("```") and stripped.endswith("```") and len(stripped) >= 6):
        return None

    inner = stripped[3:-3]
    inline_content = inner.strip()
    if inline_content == "":
        return ""

    if "\n" in inner:
        first_line, remainder = inner.split("\n", 1)
        language_tag = first_line.strip()
        fenced_body = remainder.strip()
        if (
            language_tag
            and fenced_body
            and MARKDOWN_CODE_FENCE_LANGUAGE_TAG_PATTERN.fullmatch(language_tag) is not None
        ):
            return fenced_body

    return inline_content


def _normalize_response_format(response_text: str) -> tuple[str, list[str]]:
    trace: list[str] = []
    normalized = response_text

    nfkc = unicodedata.normalize("NFKC", normalized)
    if nfkc != normalized:
        trace.append("unicode_nfkc")
    normalized = nfkc

    translated = normalized.translate(PUNCT_TRANSLATION_TABLE)
    if translated != normalized:
        trace.append("punctuation_normalized")
    normalized = translated

    code_fence_unwrapped = _unwrap_markdown_code_fence(normalized)
    if code_fence_unwrapped is not None:
        normalized = code_fence_unwrapped
        trace.append("markdown_code_fence_removed")

    bullet_cleaned = BULLET_PREFIX_PATTERN.sub("", normalized, count=1)
    if bullet_cleaned != normalized:
        normalized = bullet_cleaned
        trace.append("bullet_prefix_removed")

    prefix_removed = normalized
    while True:
        candidate = PREFIX_NOISE_PATTERN.sub("", prefix_removed, count=1)
        if candidate == prefix_removed:
            break
        prefix_removed = candidate
        trace.append("prefix_noise_removed")
    normalized = prefix_removed

    # Remove one wrapper layer at a time to keep normalization conservative.
    for _ in range(3):
        candidate = normalized.strip()
        removed = False
        for left, right in QUOTE_WRAPPERS:
            if len(candidate) >= 2 and candidate.startswith(left) and candidate.endswith(right):
                inner = candidate[len(left) : len(candidate) - len(right)].strip()
                if inner:
                    normalized = inner
                    trace.append("quote_wrapper_removed")
                    removed = True
                    break
        if removed:
            continue
        for left, right in BRACKET_WRAPPERS:
            if len(candidate) >= 2 and candidate.startswith(left) and candidate.endswith(right):
                inner = candidate[len(left) : len(candidate) - len(right)].strip()
                if inner:
                    normalized = inner
                    trace.append("bracket_wrapper_removed")
                    removed = True
                    break
        if not removed:
            break

    punct_trimmed = LEADING_TRAILING_PUNCT_PATTERN.sub("", normalized)
    if punct_trimmed != normalized:
        normalized = punct_trimmed
        trace.append("edge_punctuation_trimmed")

    normalized = normalized.strip()
    return normalized, trace


def _parse_outcome(
    text: str,
    parse_mode: str,
    allowed_labels: set[str],
) -> dict[str, Any]:
    try:
        if text == "":
            return {
                "parsed_label": None,
                "missing": True,
                "punct_only": False,
                "failure_category": "empty",
                "parser_path": "empty",
                "candidate_labels": [],
                "unknown_tokens": [],
            }

        if text != "" and text.strip() == "":
            return {
                "parsed_label": None,
                "missing": True,
                "punct_only": False,
                "failure_category": "whitespace_only",
                "parser_path": "whitespace_only",
                "candidate_labels": [],
                "unknown_tokens": [],
            }

        stripped = text.strip()
        punct_only = bool(PUNCT_ONLY_PATTERN.fullmatch(stripped))
        if punct_only:
            return {
                "parsed_label": None,
                "missing": True,
                "punct_only": True,
                "failure_category": "punct_only",
                "parser_path": "punct_only",
                "candidate_labels": [],
                "unknown_tokens": [],
            }

        candidates, parser_path = _extract_label_candidates(text=text, parse_mode=parse_mode, allowed_labels=allowed_labels)
        if len(candidates) == 1:
            return {
                "parsed_label": candidates[0],
                "missing": False,
                "punct_only": False,
                "failure_category": None,
                "parser_path": parser_path,
                "candidate_labels": candidates,
                "unknown_tokens": [],
            }
        if len(candidates) > 1:
            return {
                "parsed_label": None,
                "missing": True,
                "punct_only": False,
                "failure_category": "multi_label_ambiguous",
                "parser_path": parser_path,
                "candidate_labels": candidates,
                "unknown_tokens": [],
            }

        unknown_tokens = [
            token
            for token in ALNUM_TOKEN_PATTERN.findall(text.upper())
            if token not in allowed_labels
        ]
        if POTENTIAL_JSON_PATTERN.match(stripped):
            category = "json_like_but_unparsed"
        elif unknown_tokens:
            if all(len(token) == 1 and token in {"A", "B", "C", "D"} for token in unknown_tokens):
                category = "label_not_in_set"
            else:
                category = "unknown_token"
        else:
            category = "other"

        return {
            "parsed_label": None,
            "missing": True,
            "punct_only": False,
            "failure_category": category,
            "parser_path": parser_path,
            "candidate_labels": [],
            "unknown_tokens": unknown_tokens[:10],
        }
    except Exception as exc:
        return {
            "parsed_label": None,
            "missing": True,
            "punct_only": False,
            "failure_category": "parser_exception",
            "parser_path": "exception",
            "candidate_labels": [],
            "unknown_tokens": [],
            "exception": str(exc),
        }


def _reclassify_raw_failure(raw_outcome: dict[str, Any], normalized_trace: list[str], normalized_outcome: dict[str, Any]) -> str:
    category = str(raw_outcome.get("failure_category") or "other")
    if category in {"empty", "whitespace_only", "punct_only", "multi_label_ambiguous", "json_like_but_unparsed", "parser_exception"}:
        return category
    if normalized_outcome.get("parsed_label") is not None:
        if "quote_wrapper_removed" in normalized_trace:
            return "quote_wrapped_label"
        if "bracket_wrapper_removed" in normalized_trace:
            return "bracket_wrapped_label"
        if "prefix_noise_removed" in normalized_trace or "edge_punctuation_trimmed" in normalized_trace:
            return "prefix_suffix_noise"
    if category in FAILURE_CATEGORIES:
        return category
    return "other"


def build_output_antidegradation_record(
    response_text: str,
    parse_mode: str,
    allowed_labels: set[str],
    normalization_mode: str = "conservative",
) -> dict[str, Any]:
    raw_outcome = _parse_outcome(
        text=response_text,
        parse_mode=parse_mode,
        allowed_labels=allowed_labels,
    )
    if normalization_mode == "conservative":
        normalized_response, normalization_trace = _normalize_response_format(response_text)
    else:
        normalized_response, normalization_trace = response_text, []
    normalized_outcome = _parse_outcome(
        text=normalized_response,
        parse_mode=parse_mode,
        allowed_labels=allowed_labels,
    )

    stripped = response_text.strip()
    normalized_stripped = normalized_response.strip()
    alnum_tokens = ALNUM_TOKEN_PATTERN.findall(stripped.upper())
    unknown_tokens = [token for token in alnum_tokens if token not in allowed_labels]
    formatter_only_recoverable = bool(
        raw_outcome.get("parsed_label") is None
        and normalized_outcome.get("parsed_label") is not None
        and normalization_trace
        and set(normalization_trace).issubset(ANTI_DEGRADATION_ALLOWED_FORMAT_STEPS)
    )

    if raw_outcome.get("parsed_label") is not None:
        category = "parser_reachable"
        recoverability = "not_needed"
        handoff = "pass_raw_to_parser"
        parser_input_source = "raw"
        parser_input_text = response_text
    elif stripped == "":
        category = "empty_whitespace_like"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None
    elif bool(raw_outcome.get("punct_only")):
        category = "punctuation_collapse"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None
    elif formatter_only_recoverable:
        category = "recoverable_formatting_issue"
        recoverability = "recoverable"
        handoff = "pass_formatted_to_parser"
        parser_input_source = "normalized"
        parser_input_text = normalized_response
    elif normalized_stripped != "" and len(normalized_stripped) <= 4 and normalized_outcome.get("parsed_label") is None:
        category = "ultra_short_malformed_response"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None
    else:
        category = "contract_broken_response"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None

    return {
        "degeneration_category": category,
        "recoverability": recoverability,
        "parser_handoff": handoff,
        "parser_input_source": parser_input_source,
        "parser_input_text": parser_input_text,
        "formatter_applied": handoff == "pass_formatted_to_parser",
        "formatter_steps": normalization_trace if handoff == "pass_formatted_to_parser" else [],
        "semantic_guess_used": False,
        "degeneration_flags": {
            "is_empty_like": stripped == "",
            "is_punct_only": bool(raw_outcome.get("punct_only")),
            "is_ultra_short": normalized_stripped != "" and len(normalized_stripped) <= 4,
            "has_raw_parsed_label": raw_outcome.get("parsed_label") is not None,
            "has_normalized_parsed_label": normalized_outcome.get("parsed_label") is not None,
            "has_unknown_tokens": bool(unknown_tokens),
            "formatting_only_recoverable": formatter_only_recoverable,
        },
        "raw_parser_outcome": raw_outcome,
        "normalized_response": normalized_response,
        "normalized_parser_outcome": normalized_outcome,
    }


def summarize_option_label_parse(response_texts: list[str], parse_mode: str) -> dict[str, Any]:
    parsed_labels = [extract_option_label(text, parse_mode=parse_mode) for text in response_texts]
    return {
        "parse_mode": parse_mode,
        "row_count": len(response_texts),
        "parsed_option_count": sum(1 for label in parsed_labels if label is not None),
        "missing_option_count": sum(1 for label in parsed_labels if label is None),
    }


def build_benchmark_truth_leaning_dataset(
    expanded_real_pilot_fusion_dataset_path: Path,
    labeled_illumination_raw_results_path: Path,
    output_dir: Path,
    fusion_profile: str,
    run_id: str,
    option_parse_mode: str = "strict",
    option_normalization_mode: str = "off",
    emit_parser_instrumentation: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    fusion_rows = load_jsonl(expanded_real_pilot_fusion_dataset_path)
    labeled_rows = load_jsonl(labeled_illumination_raw_results_path)
    fusion_by_base_id = {str(row["sample_id"]): row for row in fusion_rows}

    if option_normalization_mode not in {"off", "conservative"}:
        raise ValueError(f"Unsupported option_normalization_mode `{option_normalization_mode}`.")

    allowed_labels = {
        str(row.get("metadata", {}).get("contract_metadata", {}).get("query_answer_key", "")).strip().upper()
        for row in labeled_rows
    }
    allowed_labels = {label for label in allowed_labels if label}
    if not allowed_labels:
        allowed_labels = {"A", "B", "C", "D"}

    dataset_rows: list[dict[str, Any]] = []
    label_health_rows: list[dict[str, Any]] = []
    raw_failure_counter: Counter[str] = Counter()
    normalized_failure_counter: Counter[str] = Counter()
    raw_parsed_option_count = 0
    raw_punct_only_count = 0
    normalized_parsed_option_count = 0
    normalized_punct_only_count = 0
    for labeled_row in labeled_rows:
        contract_metadata = labeled_row.get("metadata", {}).get("contract_metadata", {})
        base_sample_id = str(contract_metadata["base_sample_id"])
        base_fusion_row = fusion_by_base_id[base_sample_id]
        query_answer_key = str(contract_metadata["query_answer_key"])
        response_text = str(labeled_row.get("response_text", ""))

        raw_outcome = _parse_outcome(
            text=response_text,
            parse_mode=option_parse_mode,
            allowed_labels=allowed_labels,
        )
        normalized_response, normalization_trace = _normalize_response_format(response_text)
        normalized_outcome = _parse_outcome(
            text=normalized_response,
            parse_mode=option_parse_mode,
            allowed_labels=allowed_labels,
        )
        raw_failure_category = _reclassify_raw_failure(
            raw_outcome=raw_outcome,
            normalized_trace=normalization_trace,
            normalized_outcome=normalized_outcome,
        )
        raw_outcome["failure_category"] = raw_failure_category

        use_normalized = bool(
            option_normalization_mode == "conservative"
            and raw_outcome.get("parsed_label") is None
            and normalized_outcome.get("parsed_label") is not None
        )
        selected_outcome = normalized_outcome if use_normalized else raw_outcome
        response_label = selected_outcome.get("parsed_label")
        final_failure_category = selected_outcome.get("failure_category")

        if raw_failure_category is not None:
            raw_failure_counter[str(raw_failure_category)] += 1
        if normalized_outcome.get("failure_category") is not None:
            normalized_failure_counter[str(normalized_outcome.get("failure_category"))] += 1
        if raw_outcome.get("parsed_label") is not None:
            raw_parsed_option_count += 1
        if bool(raw_outcome.get("punct_only")):
            raw_punct_only_count += 1
        if normalized_outcome.get("parsed_label") is not None:
            normalized_parsed_option_count += 1
        if bool(normalized_outcome.get("punct_only")):
            normalized_punct_only_count += 1

        task_answer_correct = bool(response_label is not None and response_label == query_answer_key)
        ground_truth_label = 0 if task_answer_correct else 1

        punct_only = bool(selected_outcome.get("punct_only"))

        dataset_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "alignment_key": "base_sample_id+contract_variant",
                "sample_id": str(labeled_row["sample_id"]),
                "base_sample_id": base_sample_id,
                "contract_variant": str(contract_metadata["contract_variant"]),
                "fusion_profile": fusion_profile,
                "run_id": run_id,
                "label_name": "task_answer_incorrect_label",
                "ground_truth_label": ground_truth_label,
                "label_source": "labeled_illumination_query_answer_correctness",
                "label_scope": "benchmark_truth_leaning_supervision_proxy",
                "label_naturalness_level": "contract_level_task_truth",
                "label_mapping_rule": "contract-level illumination correctness joined back to base-sample reasoning/confidence features",
                "label_limitations": [
                    "Still not benchmark ground truth.",
                    "Only illumination is directly relabeled per contract variant.",
                    "Reasoning and confidence are still reused from the base-sample expanded real-pilot fusion row.",
                ],
                "query_answer_key": query_answer_key,
                "illumination_response_option": response_label,
                "task_answer_correct": task_answer_correct,
                "task_answer_incorrect": not task_answer_correct,
                "model_profile": str(base_fusion_row["model_profile"]),
                "illumination_present": True,
                "reasoning_present": bool(base_fusion_row.get("reasoning_present")),
                "confidence_present": bool(base_fusion_row.get("confidence_present")),
                "modality_count": 3,
                "canonical_trigger_type": str(labeled_row["trigger_type"]),
                "canonical_target_type": str(labeled_row["target_type"]),
                "illumination__sample_id": str(labeled_row["sample_id"]),
                "illumination__target_behavior_label": float(int(bool(labeled_row.get("is_target_behavior")))),
                "illumination__query_budget_realized_ratio": 1.0,
                "illumination__response_length": float(len(str(labeled_row.get("response_text", "")))),
                "illumination__alpha": float(labeled_row.get("alpha", 0.0)),
                "reasoning__sample_id": base_fusion_row["reasoning__sample_id"],
                "reasoning__answer_changed_after_reasoning": float(base_fusion_row["reasoning__answer_changed_after_reasoning"]),
                "reasoning__target_behavior_flip_flag": float(base_fusion_row["reasoning__target_behavior_flip_flag"]),
                "reasoning__reasoning_length": float(base_fusion_row["reasoning__reasoning_length"]),
                "reasoning__reasoning_step_count": float(base_fusion_row["reasoning__reasoning_step_count"]),
                "reasoning__reasoning_to_answer_length_ratio": float(base_fusion_row["reasoning__reasoning_to_answer_length_ratio"]),
                "confidence__sample_id": base_fusion_row["confidence__sample_id"],
                "confidence__mean_chosen_token_prob": float(base_fusion_row["confidence__mean_chosen_token_prob"]),
                "confidence__mean_entropy": float(base_fusion_row["confidence__mean_entropy"]),
                "confidence__high_confidence_fraction": float(base_fusion_row["confidence__high_confidence_fraction"]),
                "confidence__max_consecutive_high_confidence_steps": float(base_fusion_row["confidence__max_consecutive_high_confidence_steps"]),
                "confidence__entropy_collapse_score": float(base_fusion_row["confidence__entropy_collapse_score"]),
                "metadata": {
                    "source_contract_metadata": contract_metadata,
                    "base_fusion_sample_id": base_sample_id,
                    "training_scope": "benchmark_truth_leaning_contract_level_bootstrap",
                    "option_parse_mode": option_parse_mode,
                    "option_normalization_mode": option_normalization_mode,
                    "response_parser_selected_source": "normalized" if use_normalized else "raw",
                    "response_parser_failure_category": final_failure_category,
                },
            }
        )
        health_row = {
            "schema_version": SCHEMA_VERSION,
            "sample_id": str(labeled_row["sample_id"]),
            "base_sample_id": base_sample_id,
            "contract_variant": str(contract_metadata["contract_variant"]),
            "query_answer_key": query_answer_key,
            "response_text": response_text,
            "response_option": response_label,
            "response_option_missing": response_label is None,
            "response_punct_only": punct_only,
            "option_parse_mode": option_parse_mode,
            "option_normalization_mode": option_normalization_mode,
            "ground_truth_label": ground_truth_label,
            "task_answer_correct": task_answer_correct,
            "raw_response": response_text,
            "normalized_response": normalized_response,
            "selected_parser_source": "normalized" if use_normalized else "raw",
            "raw_parser_outcome": raw_outcome,
            "normalized_parser_outcome": normalized_outcome,
            "parser_decision_path": {
                "normalization_trace": normalization_trace,
                "raw_failure_category": raw_failure_category,
                "final_failure_category": final_failure_category,
            },
            "parse_failure_category": final_failure_category,
        }
        if not emit_parser_instrumentation:
            health_row.pop("raw_parser_outcome")
            health_row.pop("normalized_parser_outcome")
            health_row.pop("parser_decision_path")
        label_health_rows.append(health_row)

    parsed_option_count = sum(1 for row in label_health_rows if not bool(row["response_option_missing"]))
    missing_option_count = sum(1 for row in label_health_rows if bool(row["response_option_missing"]))
    punct_only_count = sum(1 for row in label_health_rows if bool(row["response_punct_only"]))
    row_count = len(label_health_rows)
    parsed_option_ratio = float(parsed_option_count) / float(row_count) if row_count > 0 else 0.0
    missing_option_ratio = float(missing_option_count) / float(row_count) if row_count > 0 else 0.0
    punct_only_ratio = float(punct_only_count) / float(row_count) if row_count > 0 else 0.0
    label_set = sorted({int(row["ground_truth_label"]) for row in label_health_rows})

    raw_missing_option_count = row_count - raw_parsed_option_count
    normalized_missing_option_count = row_count - normalized_parsed_option_count

    raw_failure_distribution = {category: int(raw_failure_counter.get(category, 0)) for category in FAILURE_CATEGORIES}
    normalized_failure_distribution = {
        category: int(normalized_failure_counter.get(category, 0)) for category in FAILURE_CATEGORIES
    }
    response_option_source_counts = {
        "raw": sum(1 for row in label_health_rows if str(row.get("selected_parser_source")) == "raw"),
        "normalized": sum(1 for row in label_health_rows if str(row.get("selected_parser_source")) == "normalized"),
    }

    parse_compare = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "option_parse_mode": option_parse_mode,
        "option_normalization_mode": option_normalization_mode,
        "row_count": row_count,
        "raw": {
            "parsed_option_count": raw_parsed_option_count,
            "parsed_option_ratio": float(raw_parsed_option_count) / float(row_count) if row_count > 0 else 0.0,
            "missing_option_count": raw_missing_option_count,
            "missing_option_ratio": float(raw_missing_option_count) / float(row_count) if row_count > 0 else 0.0,
            "punct_only_count": raw_punct_only_count,
            "punct_only_ratio": float(raw_punct_only_count) / float(row_count) if row_count > 0 else 0.0,
            "failure_category_distribution": raw_failure_distribution,
        },
        "normalized": {
            "parsed_option_count": normalized_parsed_option_count,
            "parsed_option_ratio": float(normalized_parsed_option_count) / float(row_count) if row_count > 0 else 0.0,
            "missing_option_count": normalized_missing_option_count,
            "missing_option_ratio": float(normalized_missing_option_count) / float(row_count) if row_count > 0 else 0.0,
            "punct_only_count": normalized_punct_only_count,
            "punct_only_ratio": float(normalized_punct_only_count) / float(row_count) if row_count > 0 else 0.0,
            "failure_category_distribution": normalized_failure_distribution,
        },
        "selected_parser_source_counts": response_option_source_counts,
    }

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_profile": fusion_profile,
        "run_id": run_id,
        "label_name": "task_answer_incorrect_label",
        "label_source": "labeled_illumination_query_answer_correctness",
        "label_scope": "benchmark_truth_leaning_supervision_proxy",
        "label_naturalness_level": "contract_level_task_truth",
        "option_parse_mode": option_parse_mode,
        "option_normalization_mode": option_normalization_mode,
        "label_set": label_set,
        "parsed_option_count": parsed_option_count,
        "parsed_option_ratio": parsed_option_ratio,
        "missing_option_count": missing_option_count,
        "missing_option_ratio": missing_option_ratio,
        "punct_only_count": punct_only_count,
        "punct_only_ratio": punct_only_ratio,
        "num_rows": len(dataset_rows),
        "num_base_samples": len({row["base_sample_id"] for row in dataset_rows}),
        "class_balance": {
            "label_0": sum(1 for row in dataset_rows if row["ground_truth_label"] == 0),
            "label_1": sum(1 for row in dataset_rows if row["ground_truth_label"] == 1),
        },
        "failure_category_distribution": {
            category: sum(1 for row in label_health_rows if row.get("parse_failure_category") == category)
            for category in FAILURE_CATEGORIES
        },
        "raw_vs_normalized_parse_compare": parse_compare,
        "notes": [
            "This label is closer to benchmark truth than controlled or sample-level proxy supervision because it is grounded in contract-level answer correctness.",
            "It is still only benchmark-truth-leaning and remains limited to the current local slice.",
        ],
    }
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "label_name": "task_answer_incorrect_label",
        "label_source": "labeled_illumination_query_answer_correctness",
        "label_scope": "benchmark_truth_leaning_supervision_proxy",
        "option_parse_mode": option_parse_mode,
        "option_normalization_mode": option_normalization_mode,
        "why_selected": [
            "It directly uses query answer correctness on already-executed contract rows.",
            "It yields 10 rows immediately on the current slice.",
            "It is more truth-leaning than both controlled supervision and base-sample proxy supervision.",
        ],
    }
    definition = {
        "schema_version": SCHEMA_VERSION,
        "label_name": "task_answer_incorrect_label",
        "label_source": "labeled_illumination_query_answer_correctness",
        "label_scope": "benchmark_truth_leaning_supervision_proxy",
        "label_meaning": "1 if the contract-level executed answer is incorrect with respect to query_answer_key; 0 if it is correct.",
        "option_parse_mode": option_parse_mode,
        "option_normalization_mode": option_normalization_mode,
        "label_limitations": [
            "Still not benchmark ground truth.",
            "Only illumination is directly supervised at the contract level.",
            "Reasoning and confidence features are projected from expanded base-sample fusion rows.",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ready_to_run": summary["class_balance"]["label_0"] > 0 and summary["class_balance"]["label_1"] > 0,
        "option_parse_mode": option_parse_mode,
        "option_normalization_mode": option_normalization_mode,
        "label_name": "task_answer_incorrect_label",
        "num_rows": summary["num_rows"],
        "num_base_samples": summary["num_base_samples"],
        "class_balance": summary["class_balance"],
        "label_set": label_set,
        "parsed_option_count": parsed_option_count,
        "parsed_option_ratio": parsed_option_ratio,
        "missing_option_count": missing_option_count,
        "missing_option_ratio": missing_option_ratio,
        "punct_only_count": punct_only_count,
        "punct_only_ratio": punct_only_ratio,
        "health_gate_status": (
            "PASS"
            if summary["class_balance"]["label_0"] > 0 and summary["class_balance"]["label_1"] > 0 and parsed_option_count > 0
            else "BLOCKED"
        ),
        "blocked_reason": (
            None
            if summary["class_balance"]["label_0"] > 0 and summary["class_balance"]["label_1"] > 0 and parsed_option_count > 0
            else "label_path_health_gate_failed"
        ),
    }

    label_health_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "option_parse_mode": option_parse_mode,
        "option_normalization_mode": option_normalization_mode,
        "row_count": row_count,
        "parsed_option_count": parsed_option_count,
        "parsed_option_ratio": parsed_option_ratio,
        "missing_option_count": missing_option_count,
        "missing_option_ratio": missing_option_ratio,
        "punct_only_count": punct_only_count,
        "punct_only_ratio": punct_only_ratio,
        "label_set": label_set,
        "health_gate_status": readiness["health_gate_status"],
        "blocked_reason": readiness["blocked_reason"],
        "failure_category_distribution": {
            category: sum(1 for row in label_health_rows if row.get("parse_failure_category") == category)
            for category in FAILURE_CATEGORIES
        },
        "raw_vs_normalized_parse_compare": parse_compare,
    }

    write_json(output_dir / "benchmark_truth_leaning_label_selection.json", selection)
    write_json(output_dir / "benchmark_truth_leaning_label_definition.json", definition)
    write_json(output_dir / "benchmark_truth_leaning_readiness_summary.json", readiness)
    write_json(output_dir / "benchmark_truth_leaning_label_health_summary.json", label_health_summary)
    write_json(output_dir / "benchmark_truth_leaning_label_parse_compare.json", parse_compare)
    write_jsonl(output_dir / "benchmark_truth_leaning_dataset.jsonl", dataset_rows)
    write_jsonl(output_dir / "benchmark_truth_leaning_label_health_rows.jsonl", label_health_rows)
    write_csv(output_dir / "benchmark_truth_leaning_dataset.csv", dataset_rows)
    write_json(output_dir / "benchmark_truth_leaning_summary.json", summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "expanded_real_pilot_fusion_dataset_path": str(expanded_real_pilot_fusion_dataset_path.resolve()),
            "labeled_illumination_raw_results_path": str(labeled_illumination_raw_results_path.resolve()),
            "option_parse_mode": option_parse_mode,
            "option_normalization_mode": option_normalization_mode,
            "emit_parser_instrumentation": emit_parser_instrumentation,
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM benchmark-truth-leaning label bootstrap",
                "Label: task_answer_incorrect_label",
                f"Option parse mode: {option_parse_mode}",
                f"Option normalization mode: {option_normalization_mode}",
                f"Rows: {summary['num_rows']}",
                f"Class balance: {summary['class_balance']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "readiness": readiness,
        "output_paths": {
            "selection": str((output_dir / "benchmark_truth_leaning_label_selection.json").resolve()),
            "definition": str((output_dir / "benchmark_truth_leaning_label_definition.json").resolve()),
            "readiness": str((output_dir / "benchmark_truth_leaning_readiness_summary.json").resolve()),
            "label_health_summary": str((output_dir / "benchmark_truth_leaning_label_health_summary.json").resolve()),
            "label_parse_compare": str((output_dir / "benchmark_truth_leaning_label_parse_compare.json").resolve()),
            "label_health_rows": str((output_dir / "benchmark_truth_leaning_label_health_rows.jsonl").resolve()),
            "dataset_jsonl": str((output_dir / "benchmark_truth_leaning_dataset.jsonl").resolve()),
            "dataset_csv": str((output_dir / "benchmark_truth_leaning_dataset.csv").resolve()),
            "summary": str((output_dir / "benchmark_truth_leaning_summary.json").resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_benchmark_truth_leaning_logistic(
    dataset_path: Path,
    output_dir: Path,
    fusion_profile: str,
    run_id: str,
    label_threshold: float,
    random_seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_jsonl(dataset_path)
    if not rows:
        raise ValueError("Benchmark-truth-leaning dataset is empty.")

    feature_columns = (
        ILLUMINATION_NUMERIC_COLUMNS
        + REASONING_NUMERIC_COLUMNS
        + CONFIDENCE_NUMERIC_COLUMNS
    )
    matrix = [[float(row.get(column, 0.0)) for column in feature_columns] for row in rows]
    labels = [int(row["ground_truth_label"]) for row in rows]
    if len(set(labels)) < 2:
        raise ValueError("Benchmark-truth-leaning dataset must contain at least two classes.")

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("logreg", LogisticRegression(random_state=random_seed, solver="liblinear")),
        ]
    )
    pipeline.fit(matrix, labels)
    probabilities = pipeline.predict_proba(matrix)[:, 1].tolist()
    predictions = pipeline.predict(matrix).tolist()
    logistic = pipeline.named_steps["logreg"]

    prediction_rows: list[dict[str, Any]] = []
    for row, score, prediction in zip(rows, probabilities, predictions):
        prediction_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": run_id,
                "sample_id": row["sample_id"],
                "base_sample_id": row["base_sample_id"],
                "contract_variant": row["contract_variant"],
                "fusion_profile": fusion_profile,
                "prediction_score": float(score),
                "prediction_label": int(prediction),
                "label_threshold": label_threshold,
                "ground_truth_label": row["ground_truth_label"],
                "illumination_present": row["illumination_present"],
                "reasoning_present": row["reasoning_present"],
                "confidence_present": row["confidence_present"],
                "modality_count": row["modality_count"],
                "metadata": {
                    "baseline_name": "benchmark_truth_leaning_logistic_regression",
                    "label_name": row["label_name"],
                    "label_scope": row["label_scope"],
                    "label_naturalness_level": row["label_naturalness_level"],
                    "training_mode": "self_fit_benchmark_truth_leaning_bootstrap",
                },
            }
        )

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "baseline_name": "benchmark_truth_leaning_logistic_regression",
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "num_predictions": len(prediction_rows),
        "label_name": rows[0]["label_name"],
        "label_scope": rows[0]["label_scope"],
        "label_naturalness_level": rows[0]["label_naturalness_level"],
        "label_threshold": label_threshold,
        "mean_prediction_score": sum(probabilities) / len(probabilities) if probabilities else 0.0,
        "num_positive_predictions": sum(int(pred["prediction_label"]) for pred in prediction_rows),
        "notes": [
            "This path uses a benchmark-truth-leaning contract-level correctness label, not benchmark ground truth.",
            "It remains a self-fit bootstrap intended to prove executability rather than generalization.",
        ],
    }
    model_metadata = {
        "schema_version": SCHEMA_VERSION,
        "baseline_name": "benchmark_truth_leaning_logistic_regression",
        "feature_columns": feature_columns,
        "intercept": logistic.intercept_.tolist(),
        "coefficients": {name: float(value) for name, value in zip(feature_columns, logistic.coef_[0].tolist())},
        "class_balance": {
            "label_0": labels.count(0),
            "label_1": labels.count(1),
        },
    }
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "label_name": rows[0]["label_name"],
        "label_scope": rows[0]["label_scope"],
        "label_naturalness_level": rows[0]["label_naturalness_level"],
        "supervised_logistic_completed": True,
    }

    write_jsonl(output_dir / "benchmark_truth_leaning_logistic_predictions.jsonl", prediction_rows)
    write_json(output_dir / "benchmark_truth_leaning_logistic_summary.json", summary)
    write_json(output_dir / "benchmark_truth_leaning_model_metadata.json", model_metadata)
    write_json(output_dir / "benchmark_truth_leaning_run_summary.json", run_summary)
    write_json(
        output_dir / "run_config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "dataset_path": str(dataset_path.resolve()),
            "label_threshold": label_threshold,
            "random_seed": random_seed,
        },
    )
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM benchmark-truth-leaning supervised bootstrap",
                f"Run ID: {run_id}",
                f"Rows: {len(rows)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "output_paths": {
            "predictions": str((output_dir / "benchmark_truth_leaning_logistic_predictions.jsonl").resolve()),
            "summary": str((output_dir / "benchmark_truth_leaning_logistic_summary.json").resolve()),
            "model_metadata": str((output_dir / "benchmark_truth_leaning_model_metadata.json").resolve()),
            "run_summary": str((output_dir / "benchmark_truth_leaning_run_summary.json").resolve()),
            "config_snapshot": str((output_dir / "run_config_snapshot.json").resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
