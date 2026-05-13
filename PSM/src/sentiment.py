from __future__ import annotations

import json
from typing import Any

import pandas as pd

from src.paths import CONFIG_DIR


FALLBACK_WORDS = {
    "positive": ["支持", "认可", "满意", "理解", "及时", "负责", "清晰", "改善", "期待", "有用"],
    "negative": ["失望", "质疑", "担心", "愤怒", "离谱", "敷衍", "糟糕", "不满", "欺骗", "风险"],
}


def load_sentiment_words() -> dict[str, list[str]]:
    path = CONFIG_DIR / "sentiment_words.json"
    if not path.exists():
        return FALLBACK_WORDS
    return json.loads(path.read_text(encoding="utf-8"))


def _count_terms(text: str, terms: list[str]) -> int:
    return sum(text.count(term) for term in terms)


def analyze_sentiment(text: Any) -> dict[str, Any]:
    value = "" if pd.isna(text) else str(text)
    words = load_sentiment_words()
    positive_count = _count_terms(value, words.get("positive", []))
    negative_count = _count_terms(value, words.get("negative", []))
    score = (positive_count - negative_count) / (positive_count + negative_count + 1)
    if score >= 0.2:
        label = "positive"
    elif score <= -0.2:
        label = "negative"
    else:
        label = "neutral"
    return {
        "sentiment_label": label,
        "sentiment_score": round(float(score), 4),
        "positive_hits": positive_count,
        "negative_hits": negative_count,
    }


def batch_analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    result = df.copy()
    rows = [analyze_sentiment(text) for text in result[source_col].fillna("").astype(str)]
    sentiment_df = pd.DataFrame(rows)
    for column in sentiment_df.columns:
        result[column] = sentiment_df[column]
    return result


def sentiment_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if "sentiment_label" not in df.columns:
        return pd.DataFrame(columns=["sentiment_label", "count", "ratio"])
    counts = df["sentiment_label"].value_counts().rename_axis("sentiment_label").reset_index(name="count")
    total = counts["count"].sum()
    counts["ratio"] = (counts["count"] / total * 100).round(2) if total else 0
    return counts


def sentiment_over_time(df: pd.DataFrame) -> pd.DataFrame:
    if "publish_time" not in df.columns or "sentiment_label" not in df.columns:
        return pd.DataFrame()
    timed = df.dropna(subset=["publish_time"]).copy()
    if timed.empty:
        return pd.DataFrame()
    timed["date"] = pd.to_datetime(timed["publish_time"]).dt.date
    return timed.groupby(["date", "sentiment_label"]).size().reset_index(name="count")

