from __future__ import annotations

import json
from typing import Any

import pandas as pd

from src.paths import CONFIG_DIR


DEFAULT_WEIGHTS = {
    "negative_ratio": 20,
    "heat_growth": 15,
    "topic_concentration": 15,
    "opposition_ratio": 15,
    "uncertainty_index": 15,
    "extreme_expression_ratio": 10,
    "interaction_amplification": 10,
}

EXTREME_TERMS = ["必须", "绝不", "太离谱", "无法接受", "抵制", "愤怒", "曝光", "严查", "道歉", "追责"]

METRIC_NAMES = {
    "negative_ratio": "负面情绪占比",
    "heat_growth": "热度增长速度",
    "topic_concentration": "争议主题集中度",
    "opposition_ratio": "反对立场占比",
    "uncertainty_index": "不确定信息指数",
    "extreme_expression_ratio": "极端表达比例",
    "interaction_amplification": "互动放大系数",
}


def load_default_weights() -> dict[str, int]:
    path = CONFIG_DIR / "risk_weights.json"
    if not path.exists():
        return DEFAULT_WEIGHTS
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio(series: pd.Series, value: Any) -> float:
    if series.empty:
        return 0.0
    return float((series == value).mean() * 100)


def calculate_negative_ratio(df: pd.DataFrame) -> float:
    if "sentiment_label" not in df.columns:
        return 0.0
    return round(_ratio(df["sentiment_label"], "negative"), 2)


def calculate_opposition_ratio(df: pd.DataFrame) -> float:
    if "stance_label" not in df.columns:
        return 0.0
    return round(_ratio(df["stance_label"], "oppose"), 2)


def calculate_uncertainty_index(df: pd.DataFrame) -> float:
    if "uncertainty_flag" not in df.columns or df.empty:
        return 0.0
    return round(float(df["uncertainty_flag"].fillna(False).mean() * 100), 2)


def calculate_topic_concentration(df: pd.DataFrame) -> float:
    if "cluster" not in df.columns or df.empty:
        return 0.0
    return round(float(df["cluster"].value_counts(normalize=True).max() * 100), 2)


def calculate_heat_growth(df: pd.DataFrame) -> float:
    if "publish_time" not in df.columns:
        return 0.0
    timed = df.dropna(subset=["publish_time"]).copy()
    if timed.empty:
        return 0.0
    timed["date"] = pd.to_datetime(timed["publish_time"]).dt.date
    counts = timed.groupby("date").size().sort_index()
    if len(counts) < 2:
        return 0.0
    growth = counts.pct_change().replace([float("inf"), -float("inf")], 0).fillna(0).max()
    return round(float(min(max(growth * 60, 0), 100)), 2)


def calculate_extreme_expression_ratio(df: pd.DataFrame) -> float:
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    if source_col not in df.columns or df.empty:
        return 0.0
    flags = df[source_col].fillna("").astype(str).apply(lambda text: any(term in text for term in EXTREME_TERMS))
    return round(float(flags.mean() * 100), 2)


def calculate_interaction_amplification(df: pd.DataFrame) -> float:
    cols = [col for col in ["like_count", "comment_count", "repost_count"] if col in df.columns]
    if not cols or df.empty:
        return 0.0
    interactions = df[cols].sum(axis=1)
    if interactions.max() <= 0:
        return 0.0
    top_share = interactions.sort_values(ascending=False).head(max(1, len(df) // 10)).sum() / interactions.sum()
    return round(float(min(top_share * 100, 100)), 2)


def calculate_risk_score(df: pd.DataFrame, weights: dict[str, int] | None = None) -> dict[str, Any]:
    weights = weights or load_default_weights()
    metrics = {
        "negative_ratio": calculate_negative_ratio(df),
        "heat_growth": calculate_heat_growth(df),
        "topic_concentration": calculate_topic_concentration(df),
        "opposition_ratio": calculate_opposition_ratio(df),
        "uncertainty_index": calculate_uncertainty_index(df),
        "extreme_expression_ratio": calculate_extreme_expression_ratio(df),
        "interaction_amplification": calculate_interaction_amplification(df),
    }
    weight_sum = sum(weights.values()) or 1
    score = sum(metrics[key] * weights.get(key, 0) for key in metrics) / weight_sum
    score = round(float(score), 2)
    if score <= 30:
        level = "低风险"
    elif score <= 60:
        level = "中风险"
    elif score <= 80:
        level = "较高风险"
    else:
        level = "高风险"

    ranked = sorted(metrics.items(), key=lambda item: item[1] * weights.get(item[0], 0), reverse=True)
    reasons = [f"{METRIC_NAMES[key]}较高（{value:.2f}）" for key, value in ranked[:3] if value > 0]
    return {"score": score, "level": level, "metrics": metrics, "weights": weights, "reasons": reasons}

