from __future__ import annotations

import streamlit as st

from src.risk import DEFAULT_WEIGHTS, METRIC_NAMES, calculate_risk_score
from src.sentiment import batch_analyze_sentiment
from src.stance import batch_detect_stance
from src.uncertainty import batch_detect_uncertainty, uncertainty_summary
from src.visualization import radar_chart
from src.state import init_state


init_state()
st.title("风险研判")
st.caption("基于文本信号进行舆情风险辅助评分，结果仅用于分析参考。")

df = st.session_state.analysis_df
if df is None:
    base_df = st.session_state.cluster_df if st.session_state.cluster_df is not None else st.session_state.clean_df
    if base_df is None:
        st.info("请先完成“数据清洗”。")
        st.stop()
    target = st.session_state.get("target_entity", "") or "学校"
    df = batch_detect_uncertainty(batch_detect_stance(batch_analyze_sentiment(base_df), target))

st.warning("本风险等级为基于文本信号的辅助研判结果，不代表对现实事件风险的确定性判断。")

with st.sidebar:
    st.header("风险权重")
    weights = {}
    for key, default in DEFAULT_WEIGHTS.items():
        weights[key] = st.slider(METRIC_NAMES[key], 0, 40, int(default), 1)

if st.button("计算风险评分", type="primary"):
    risk_result = calculate_risk_score(df, weights)
    st.session_state.risk_result = risk_result
    st.success("风险评分已更新。")

if st.session_state.risk_result is not None:
    result = st.session_state.risk_result
    left, right = st.columns([1, 2])
    with left:
        st.metric("风险评分", result["score"])
        st.metric("风险等级", result["level"])
        if result["reasons"]:
            st.write("主要风险来源：")
            for reason in result["reasons"]:
                st.write(f"- {reason}")
    with right:
        st.plotly_chart(radar_chart(result["metrics"], METRIC_NAMES), use_container_width=True)

    st.subheader("不确定信息摘要")
    summary = uncertainty_summary(df)
    cols = st.columns(3)
    cols[0].metric("不确定表达数量", summary["count"])
    cols[1].metric("不确定表达占比", f"{summary['ratio']}%")
    cols[2].metric("高频不确定词", "、".join(summary["terms"][:3]) if summary["terms"] else "暂无")
    for example in summary["examples"]:
        st.write(f"- {example}")

else:
    st.info("点击“计算风险评分”生成结果。")

