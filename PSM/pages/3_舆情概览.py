from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.timeline import aggregate_by_time, detect_peak_period, estimate_lifecycle_stage, overview_metrics
from src.visualization import bar_chart, line_chart, pie_chart
from src.state import init_state


init_state()
st.title("舆情概览")
st.caption("观察样本规模、平台分布、互动量和时间热度变化。")

df = st.session_state.clean_df if st.session_state.clean_df is not None else st.session_state.raw_df
if df is None:
    st.info("请先在“数据中心”导入数据。")
    st.stop()

metrics = overview_metrics(df)
cols = st.columns(4)
cols[0].metric("文本数量", metrics["text_count"])
cols[1].metric("平台数量", metrics["platform_count"])
cols[2].metric("总互动量", metrics["total_interactions"])
cols[3].metric("平均文本长度", metrics["average_length"])

left, right = st.columns(2)

with left:
    if "platform" in df.columns:
        platform_df = df["platform"].fillna("未知").value_counts().reset_index()
        platform_df.columns = ["platform", "count"]
        st.plotly_chart(pie_chart(platform_df, "platform", "count", "平台分布"), use_container_width=True)
    else:
        st.info("当前数据没有 platform 字段。")

with right:
    interaction_cols = [col for col in ["like_count", "comment_count", "repost_count"] if col in df.columns]
    if interaction_cols:
        totals = pd.DataFrame({"metric": interaction_cols, "count": [int(df[col].sum()) for col in interaction_cols]})
        st.plotly_chart(bar_chart(totals, "metric", "count", "互动量构成"), use_container_width=True)
    else:
        st.info("当前数据没有互动量字段。")

time_series = aggregate_by_time(df)
if not time_series.empty:
    st.subheader("时间热度变化")
    st.plotly_chart(line_chart(time_series, "publish_time", "count", "文本数量时间走势"), use_container_width=True)
    st.info(f"峰值日期：{detect_peak_period(time_series)}；生命周期初步判断：{estimate_lifecycle_stage(time_series)}。")
else:
    st.info("当前数据没有有效 publish_time 字段，因此暂不展示时间演化图。")
