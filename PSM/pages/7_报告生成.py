from __future__ import annotations

import streamlit as st

from src.report import build_report_context, generate_docx_report_bytes, generate_markdown_report
from src.state import init_state


init_state()
st.title("报告生成")
st.caption("汇总当前分析结果，生成可提交、可继续修改的结构化报告。")

df = st.session_state.analysis_df
if df is None:
    df = st.session_state.cluster_df
if df is None:
    df = st.session_state.clean_df
if df is None:
    st.info("请先完成数据清洗，最好再运行主题、情感和风险分析。")
    st.stop()

context = build_report_context(
    df,
    quality_report=st.session_state.quality_report,
    keyword_df=st.session_state.keyword_df,
    cluster_keywords=st.session_state.cluster_keywords,
    risk_result=st.session_state.risk_result,
    target=st.session_state.get("target_entity", ""),
    source_note=st.session_state.get("source_note", ""),
)
markdown_report = generate_markdown_report(context)

st.subheader("报告预览")
edited = st.text_area("可以在这里直接微调报告文本", value=markdown_report, height=520)

left, right = st.columns(2)
with left:
    st.download_button(
        "下载 Markdown 报告",
        data=edited.encode("utf-8-sig"),
        file_name="yuqing_report.md",
        mime="text/markdown",
    )
with right:
    try:
        docx_bytes = generate_docx_report_bytes(edited)
        st.download_button(
            "下载 Word 报告",
            data=docx_bytes,
            file_name="yuqing_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as error:
        st.warning(f"Word 报告暂时无法生成：{error}")
