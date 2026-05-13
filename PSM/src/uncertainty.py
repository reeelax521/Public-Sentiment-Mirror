from __future__ import annotations

from typing import Any

import pandas as pd

from src.paths import CONFIG_DIR


FALLBACK_TERMS = ["网传", "听说", "据说", "爆料", "求证", "未证实", "真的假的", "等官方回应", "消息源"]


def load_uncertainty_terms() -> list[str]:
    path = CONFIG_DIR / "uncertainty_words.txt"
    if not path.exists():
        return FALLBACK_TERMS
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def detect_uncertainty(text: Any) -> dict[str, Any]:
    value = "" if pd.isna(text) else str(text)
    terms = [term for term in load_uncertainty_terms() if term in value]
    return {
        "uncertainty_flag": bool(terms),
        "uncertainty_terms": "、".join(terms),
        "uncertainty_score": min(len(terms) / 3, 1.0),
    }


def batch_detect_uncertainty(df: pd.DataFrame) -> pd.DataFrame:
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    result = df.copy()
    rows = [detect_uncertainty(text) for text in result[source_col].fillna("").astype(str)]
    uncertainty_df = pd.DataFrame(rows)
    for column in uncertainty_df.columns:
        result[column] = uncertainty_df[column]
    return result


def uncertainty_summary(df: pd.DataFrame) -> dict[str, Any]:
    if "uncertainty_flag" not in df.columns or df.empty:
        return {"count": 0, "ratio": 0, "terms": [], "examples": []}
    flagged = df[df["uncertainty_flag"] == True]
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    terms: list[str] = []
    for value in flagged["uncertainty_terms"].fillna(""):
        terms.extend([term for term in str(value).split("、") if term])
    common_terms = pd.Series(terms).value_counts().head(8).index.tolist() if terms else []
    return {
        "count": int(len(flagged)),
        "ratio": round(len(flagged) / len(df) * 100, 2) if len(df) else 0,
        "terms": common_terms,
        "examples": flagged[source_col].head(5).tolist(),
    }

