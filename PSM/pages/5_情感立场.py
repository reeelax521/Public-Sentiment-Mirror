from __future__ import annotations

import streamlit as st

from src.sentiment import batch_analyze_sentiment, sentiment_distribution, sentiment_over_time
from src.stance import batch_detect_stance, stance_distribution
from src.uncertainty import batch_detect_uncertainty
from src.visualization import line_chart, pie_chart
from src.state import init_state


init_state()
st.title("情感立场")
st.caption("识别文本情绪倾向，并初步判断对目标对象的支持、反对、中立或无关。")

df = st.session_state.cluster_df if st.session_state.cluster_df is not None else st.session_state.clean_df
if df is None:
    st.info("请先完成“数据清洗”。")
    st.stop()

target = st.text_input("立场分析目标对象", value=st.session_state.get("target_entity", "") or "学校")

if st.button("运行情感与立场分析", type="primary"):
    analysis_df = batch_analyze_sentiment(df)
    analysis_df = batch_detect_stance(analysis_df, target)
    analysis_df = batch_detect_uncertainty(analysis_df)
    st.session_state.analysis_df = analysis_df
    st.session_state.target_entity = target
    st.success("情感、立场与不确定信息识别完成。")

if st.session_state.analysis_df is not None:
    analysis_df = st.session_state.analysis_df
    left, right = st.columns(2)
    with left:
        sentiment_df = sentiment_distribution(analysis_df)
        st.subheader("情感分布")
        st.dataframe(sentiment_df, use_container_width=True)
        st.plotly_chart(pie_chart(sentiment_df, "sentiment_label", "count", "情感分布"), use_container_width=True)

    with right:
        stance_df = stance_distribution(analysis_df)
        st.subheader("立场分布")
        st.dataframe(stance_df, use_container_width=True)
        st.plotly_chart(pie_chart(stance_df, "stance_label", "count", "立场分布"), use_container_width=True)

    timed = sentiment_over_time(analysis_df)
    if not timed.empty:
        st.subheader("情感时间变化")
        st.plotly_chart(line_chart(timed, "date", "count", "不同情感随时间变化", color="sentiment_label"), use_container_width=True)

    st.subheader("分析结果预览")
    preview_cols = [
        col
        for col in ["content", "clean_content", "sentiment_label", "sentiment_score", "stance_label", "uncertainty_flag", "uncertainty_terms"]
        if col in analysis_df.columns
    ]
    st.dataframe(analysis_df[preview_cols].head(30), use_container_width=True)

