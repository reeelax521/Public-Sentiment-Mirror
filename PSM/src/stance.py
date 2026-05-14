from __future__ import annotations

import json
from typing import Any

import pandas as pd

from src.paths import CONFIG_DIR


FALLBACK_WORDS = {
    "support": ["支持", "赞成", "认可", "理解", "合理", "做得好", "及时", "负责"],
    "oppose": ["反对", "质疑", "不满", "抵制", "失望", "离谱", "敷衍", "不接受"],
    "neutral": ["观望", "等待", "看看", "中立", "不好说", "需要更多信息"],
}


def load_stance_words() -> dict[str, list[str]]:
    path = CONFIG_DIR / "stance_words.json"
    if not path.exists():
        return FALLBACK_WORDS
    return json.loads(path.read_text(encoding="utf-8"))


def _hits(text: str, terms: list[str]) -> int:
    return sum(text.count(term) for term in terms)


def detect_stance(text: Any, target: str = "") -> dict[str, Any]:
    value = "" if pd.isna(text) else str(text)
    target = target.strip()
    words = load_stance_words()
    support = _hits(value, words.get("support", []))
    oppose = _hits(value, words.get("oppose", []))
    neutral = _hits(value, words.get("neutral", []))

    if target and target not in value and support + oppose + neutral == 0:
        label = "irrelevant"
        score = 0.0
    elif support > oppose and support >= neutral:
        label = "support"
        score = support / (support + oppose + neutral + 1)
    elif oppose > support and oppose >= neutral:
        label = "oppose"
        score = oppose / (support + oppose + neutral + 1)
    else:
        label = "neutral"
        score = neutral / (support + oppose + neutral + 1)
    return {
        "target_entity": target,
        "stance_label": label,
        "stance_score": round(float(score), 4),
        "stance_support_hits": support,
        "stance_oppose_hits": oppose,
    }


def batch_detect_stance(df: pd.DataFrame, target: str = "") -> pd.DataFrame:
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    result = df.copy()
    rows = [detect_stance(text, target) for text in result[source_col].fillna("").astype(str)]
    stance_df = pd.DataFrame(rows)
    for column in stance_df.columns:
        result[column] = stance_df[column]
    return result


def stance_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if "stance_label" not in df.columns:
        return pd.DataFrame(columns=["stance_label", "count", "ratio"])
    counts = df["stance_label"].value_counts().rename_axis("stance_label").reset_index(name="count")
    total = counts["count"].sum()
    counts["ratio"] = (counts["count"] / total * 100).round(2) if total else 0
    return counts

