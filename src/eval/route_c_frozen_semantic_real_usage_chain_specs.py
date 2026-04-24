"""Window specifications for route_c frozen-semantic real-usage chains (stages 159-198)."""

from __future__ import annotations

from typing import Any


REQUIRED_PROMPT_IDS = [
    "illumination_0000",
    "illumination_0001",
    "illumination_0002",
    "illumination_0003",
    "illumination_0004",
    "illumination_0005",
]


def _window(
    *,
    idx: int,
    rec_primary: str,
    norm_primary: str,
    rec_secondary: str,
    norm_secondary: str,
    tag: str,
) -> dict[str, Any]:
    return {
        "window_id": f"real_usage_window_{idx:02d}",
        "window_tag": f"ruw{idx:02d}",
        "entries": [
            {
                "path_kind": "recoverable",
                "anchor_prompt_id": rec_primary,
                "response_variant": "code_fence",
                "case_tail": f"{tag}_recoverable_code_fence",
                "note": f"recoverable code-fence wrapper from {rec_primary}",
            },
            {
                "path_kind": "normal",
                "anchor_prompt_id": norm_primary,
                "response_variant": "raw",
                "case_tail": f"{tag}_normal_primary",
                "note": f"real normal primary case from {norm_primary}",
            },
            {
                "path_kind": "nonrecoverable",
                "anchor_prompt_id": "illumination_0000",
                "response_variant": "raw",
                "case_tail": f"{tag}_nonrecoverable_anchor",
                "note": "real nonrecoverable anchor case from illumination_0000",
            },
            {
                "path_kind": "recoverable",
                "anchor_prompt_id": rec_secondary,
                "response_variant": "code_fence_lang_tag",
                "case_tail": f"{tag}_recoverable_lang_tag",
                "note": f"recoverable language-tag wrapper from {rec_secondary}",
            },
            {
                "path_kind": "normal",
                "anchor_prompt_id": norm_secondary,
                "response_variant": "raw",
                "case_tail": f"{tag}_normal_secondary",
                "note": f"real normal secondary case from {norm_secondary}",
            },
        ],
    }


BASE_WINDOWS = [
    _window(idx=1, rec_primary="illumination_0001", norm_primary="illumination_0001", rec_secondary="illumination_0002", norm_secondary="illumination_0002", tag="w01"),
    _window(idx=2, rec_primary="illumination_0003", norm_primary="illumination_0003", rec_secondary="illumination_0004", norm_secondary="illumination_0004", tag="w02"),
    _window(idx=3, rec_primary="illumination_0005", norm_primary="illumination_0005", rec_secondary="illumination_0001", norm_secondary="illumination_0001", tag="w03"),
    _window(idx=4, rec_primary="illumination_0002", norm_primary="illumination_0003", rec_secondary="illumination_0004", norm_secondary="illumination_0005", tag="w04"),
    _window(idx=5, rec_primary="illumination_0003", norm_primary="illumination_0002", rec_secondary="illumination_0005", norm_secondary="illumination_0004", tag="w05"),
    _window(idx=6, rec_primary="illumination_0004", norm_primary="illumination_0001", rec_secondary="illumination_0002", norm_secondary="illumination_0005", tag="w06"),
    _window(idx=7, rec_primary="illumination_0005", norm_primary="illumination_0003", rec_secondary="illumination_0001", norm_secondary="illumination_0002", tag="w07"),
    _window(idx=8, rec_primary="illumination_0002", norm_primary="illumination_0004", rec_secondary="illumination_0003", norm_secondary="illumination_0001", tag="w08"),
    _window(idx=9, rec_primary="illumination_0001", norm_primary="illumination_0005", rec_secondary="illumination_0004", norm_secondary="illumination_0003", tag="w09"),
    _window(idx=10, rec_primary="illumination_0003", norm_primary="illumination_0001", rec_secondary="illumination_0005", norm_secondary="illumination_0002", tag="w10"),
    _window(idx=11, rec_primary="illumination_0004", norm_primary="illumination_0002", rec_secondary="illumination_0001", norm_secondary="illumination_0005", tag="w11"),
    _window(idx=12, rec_primary="illumination_0005", norm_primary="illumination_0004", rec_secondary="illumination_0002", norm_secondary="illumination_0003", tag="w12"),
    _window(idx=13, rec_primary="illumination_0001", norm_primary="illumination_0002", rec_secondary="illumination_0003", norm_secondary="illumination_0004", tag="w13"),
    _window(idx=14, rec_primary="illumination_0002", norm_primary="illumination_0005", rec_secondary="illumination_0004", norm_secondary="illumination_0001", tag="w14"),
    _window(idx=15, rec_primary="illumination_0003", norm_primary="illumination_0004", rec_secondary="illumination_0005", norm_secondary="illumination_0002", tag="w15"),
    _window(idx=16, rec_primary="illumination_0004", norm_primary="illumination_0003", rec_secondary="illumination_0001", norm_secondary="illumination_0005", tag="w16"),
    _window(idx=17, rec_primary="illumination_0005", norm_primary="illumination_0001", rec_secondary="illumination_0003", norm_secondary="illumination_0002", tag="w17"),
    _window(idx=18, rec_primary="illumination_0002", norm_primary="illumination_0004", rec_secondary="illumination_0005", norm_secondary="illumination_0001", tag="w18"),
    _window(idx=19, rec_primary="illumination_0001", norm_primary="illumination_0003", rec_secondary="illumination_0004", norm_secondary="illumination_0005", tag="w19"),
    _window(idx=20, rec_primary="illumination_0003", norm_primary="illumination_0002", rec_secondary="illumination_0001", norm_secondary="illumination_0004", tag="w20"),
    _window(idx=21, rec_primary="illumination_0004", norm_primary="illumination_0005", rec_secondary="illumination_0002", norm_secondary="illumination_0001", tag="w21"),
    _window(idx=22, rec_primary="illumination_0005", norm_primary="illumination_0003", rec_secondary="illumination_0001", norm_secondary="illumination_0002", tag="w22"),
    _window(idx=23, rec_primary="illumination_0001", norm_primary="illumination_0004", rec_secondary="illumination_0003", norm_secondary="illumination_0005", tag="w23"),
    _window(idx=24, rec_primary="illumination_0002", norm_primary="illumination_0001", rec_secondary="illumination_0004", norm_secondary="illumination_0003", tag="w24"),
    _window(idx=25, rec_primary="illumination_0003", norm_primary="illumination_0005", rec_secondary="illumination_0002", norm_secondary="illumination_0004", tag="w25"),
    _window(idx=26, rec_primary="illumination_0004", norm_primary="illumination_0002", rec_secondary="illumination_0005", norm_secondary="illumination_0001", tag="w26"),
    _window(idx=27, rec_primary="illumination_0005", norm_primary="illumination_0001", rec_secondary="illumination_0003", norm_secondary="illumination_0004", tag="w27"),
    _window(idx=28, rec_primary="illumination_0001", norm_primary="illumination_0003", rec_secondary="illumination_0005", norm_secondary="illumination_0002", tag="w28"),
    _window(idx=29, rec_primary="illumination_0002", norm_primary="illumination_0004", rec_secondary="illumination_0001", norm_secondary="illumination_0005", tag="w29"),
    _window(idx=30, rec_primary="illumination_0003", norm_primary="illumination_0001", rec_secondary="illumination_0004", norm_secondary="illumination_0002", tag="w30"),
    _window(idx=31, rec_primary="illumination_0004", norm_primary="illumination_0005", rec_secondary="illumination_0002", norm_secondary="illumination_0003", tag="w31"),
    _window(idx=32, rec_primary="illumination_0005", norm_primary="illumination_0002", rec_secondary="illumination_0001", norm_secondary="illumination_0004", tag="w32"),
    _window(idx=33, rec_primary="illumination_0001", norm_primary="illumination_0005", rec_secondary="illumination_0003", norm_secondary="illumination_0002", tag="w33"),
    _window(idx=34, rec_primary="illumination_0002", norm_primary="illumination_0003", rec_secondary="illumination_0004", norm_secondary="illumination_0001", tag="w34"),
    _window(idx=35, rec_primary="illumination_0003", norm_primary="illumination_0004", rec_secondary="illumination_0005", norm_secondary="illumination_0002", tag="w35"),
    _window(idx=36, rec_primary="illumination_0004", norm_primary="illumination_0005", rec_secondary="illumination_0001", norm_secondary="illumination_0003", tag="w36"),
    _window(idx=37, rec_primary="illumination_0005", norm_primary="illumination_0002", rec_secondary="illumination_0003", norm_secondary="illumination_0004", tag="w37"),
    _window(idx=38, rec_primary="illumination_0001", norm_primary="illumination_0004", rec_secondary="illumination_0002", norm_secondary="illumination_0005", tag="w38"),
    _window(idx=39, rec_primary="illumination_0002", norm_primary="illumination_0005", rec_secondary="illumination_0003", norm_secondary="illumination_0001", tag="w39"),
    _window(idx=40, rec_primary="illumination_0003", norm_primary="illumination_0001", rec_secondary="illumination_0004", norm_secondary="illumination_0005", tag="w40"),
    _window(idx=41, rec_primary="illumination_0004", norm_primary="illumination_0002", rec_secondary="illumination_0005", norm_secondary="illumination_0003", tag="w41"),
    _window(idx=42, rec_primary="illumination_0005", norm_primary="illumination_0003", rec_secondary="illumination_0001", norm_secondary="illumination_0004", tag="w42"),
    _window(idx=43, rec_primary="illumination_0001", norm_primary="illumination_0002", rec_secondary="illumination_0005", norm_secondary="illumination_0004", tag="w43"),
    _window(idx=44, rec_primary="illumination_0002", norm_primary="illumination_0004", rec_secondary="illumination_0001", norm_secondary="illumination_0003", tag="w44"),
]


def windows_for_159() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:5]


def windows_for_160() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:6]


def windows_for_161() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:7]


def windows_for_162() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:8]


def windows_for_163() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:9]


def windows_for_164() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:10]


def windows_for_165() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:11]


def windows_for_166() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:12]


def windows_for_167() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:13]


def windows_for_168() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:14]


def windows_for_169() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:15]


def windows_for_170() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:16]


def windows_for_171() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:17]


def windows_for_172() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:18]


def windows_for_173() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:19]


def windows_for_174() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:20]


def windows_for_175() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:21]


def windows_for_176() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:22]


def windows_for_177() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:23]


def windows_for_178() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:24]


def windows_for_179() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:25]


def windows_for_180() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:26]


def windows_for_181() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:27]


def windows_for_182() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:28]


def windows_for_183() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:29]


def windows_for_184() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:30]


def windows_for_185() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:31]


def windows_for_186() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:32]


def windows_for_187() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:33]


def windows_for_188() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:34]


def windows_for_189() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:35]


def windows_for_190() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:36]


def windows_for_191() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:37]


def windows_for_192() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:38]


def windows_for_193() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:39]


def windows_for_194() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:40]


def windows_for_195() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:41]


def windows_for_196() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:42]


def windows_for_197() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:43]


def windows_for_198() -> list[dict[str, Any]]:
    return BASE_WINDOWS[:44]
