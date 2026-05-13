from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocess import dataframe_to_csv_bytes, preprocess_dataframe
from src.state import init_state


init_state()
st.title("数据清洗")
st.caption("去除空文本、重复文本、URL 等噪声，并生成质量诊断。")

if st.session_state.raw_df is None:
    st.info("请先到“数据中心”导入并保存数据。")
    st.stop()

with st.sidebar:
    st.header("清洗设置")
    remove_urls = st.checkbox("去除 URL", value=True)
    remove_emoji = st.checkbox("去除表情符号", value=False)
    remove_duplicates = st.checkbox("去除重复文本", value=True)
    min_length = st.number_input("最短文本长度", min_value=1, max_value=100, value=2)

if st.button("执行清洗", type="primary"):
    try:
        clean_df, report = preprocess_dataframe(
            st.session_state.raw_df,
            remove_urls=remove_urls,
            remove_emoji=remove_emoji,
            remove_duplicates=remove_duplicates,
            min_length=int(min_length),
        )
        st.session_state.clean_df = clean_df
        st.session_state.quality_report = report
        st.success("清洗完成。")
    except Exception as error:
        st.error(str(error))

if st.session_state.clean_df is not None:
    report = st.session_state.quality_report or {}
    cols = st.columns(5)
    cols[0].metric("原始文本数", report.get("raw_count", 0))
    cols[1].metric("有效文本数", report.get("valid_count", 0))
    cols[2].metric("保留率", f"{report.get('retention_rate', 0)}%")
    cols[3].metric("重复文本数", report.get("duplicate_text_count", 0))
    cols[4].metric("平均长度", report.get("average_length", 0))

    st.write(f"时间跨度：{report.get('time_range', '无有效时间字段')}")

    st.subheader("清洗结果预览")
    st.dataframe(st.session_state.clean_df.head(30), use_container_width=True)

    st.download_button(
        "下载清洗后 CSV",
        data=dataframe_to_csv_bytes(st.session_state.clean_df),
        file_name="yuqing_clean_data.csv",
        mime="text/csv",
    )
