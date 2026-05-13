from __future__ import annotations

import pandas as pd


def overview_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    interaction_cols = [col for col in ["like_count", "comment_count", "repost_count"] if col in df.columns]
    total_interactions = int(df[interaction_cols].sum(axis=1).sum()) if interaction_cols else 0
    return {
        "text_count": int(len(df)),
        "platform_count": int(df["platform"].nunique()) if "platform" in df.columns else 0,
        "total_interactions": total_interactions,
        "average_length": round(float(df["clean_content"].str.len().mean()), 2)
        if "clean_content" in df.columns and not df.empty
        else 0,
    }


def aggregate_by_time(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    if "publish_time" not in df.columns:
        return pd.DataFrame()
    timed = df.dropna(subset=["publish_time"]).copy()
    if timed.empty:
        return pd.DataFrame()
    timed["publish_time"] = pd.to_datetime(timed["publish_time"])
    grouped = timed.set_index("publish_time").resample(freq).size().reset_index(name="count")
    return grouped


def detect_peak_period(time_series: pd.DataFrame) -> str:
    if time_series.empty or "count" not in time_series.columns:
        return "无有效时间峰值"
    row = time_series.loc[time_series["count"].idxmax()]
    return str(pd.to_datetime(row["publish_time"]).date())


def estimate_lifecycle_stage(time_series: pd.DataFrame) -> str:
    if time_series.empty or len(time_series) < 3:
        return "样本时间不足，暂不判断"
    counts = time_series["count"].tolist()
    peak_idx = counts.index(max(counts))
    if peak_idx == len(counts) - 1:
        return "升温期"
    if peak_idx <= 1 and counts[-1] < max(counts) * 0.5:
        return "回落期"
    if counts[-1] <= max(counts) * 0.3:
        return "长尾期"
    return "爆发期"

