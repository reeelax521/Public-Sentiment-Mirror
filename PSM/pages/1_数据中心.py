from __future__ import annotations

import streamlit as st

from src.preprocess import (
    STANDARD_COLUMNS,
    build_dataframe_from_text,
    infer_column_mapping,
    list_sample_files,
    load_sample_data,
    load_user_data,
    standardize_columns,
)
from src.state import init_state


init_state()
st.title("数据中心")
st.caption("导入文本数据，并把不同来源的字段统一到系统标准字段。")

source = st.radio("选择数据来源", ["内置样例", "上传文件", "粘贴文本"], horizontal=True)
raw_df = None
source_note = ""

if source == "内置样例":
    sample_files = list_sample_files()
    if not sample_files:
        st.warning("data/sample 中没有样例数据。")
    else:
        selected = st.selectbox("选择样例数据", [path.name for path in sample_files])
        raw_df = load_sample_data(selected)
        source_note = "本案例数据为演示数据，不代表真实平台完整舆情。"

elif source == "上传文件":
    uploaded = st.file_uploader("上传 CSV 或 Excel 文件", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        raw_df = load_user_data(uploaded)
        source_note = "本报告基于用户上传数据生成，请在正式提交前补充数据来源说明。"

else:
    event_name = st.text_input("事件/项目名称", value=st.session_state.get("event_name", ""))
    platform = st.text_input("文本来源", value="文本粘贴")
    pasted = st.text_area("每行粘贴一条文本", height=220)
    if pasted.strip():
        raw_df = build_dataframe_from_text(pasted, platform=platform, event_name=event_name)
        source_note = "本报告基于用户粘贴文本生成。"

if raw_df is not None:
    st.subheader("原始数据预览")
    st.dataframe(raw_df.head(20), use_container_width=True)
    st.caption(f"共 {len(raw_df)} 条记录，{len(raw_df.columns)} 个字段。")

    st.subheader("字段映射")
    inferred = infer_column_mapping([str(col) for col in raw_df.columns])
    columns = [""] + [str(col) for col in raw_df.columns]
    mapping = {}
    grid = st.columns(3)
    for index, standard in enumerate(STANDARD_COLUMNS):
        with grid[index % 3]:
            default = inferred.get(standard, "")
            default_index = columns.index(default) if default in columns else 0
            mapping[standard] = st.selectbox(
                standard,
                columns,
                index=default_index,
                key=f"mapping_{standard}",
            )

    if st.button("保存为当前项目数据", type="primary"):
        standardized = standardize_columns(raw_df, mapping)
        st.session_state.raw_df = standardized
        st.session_state.clean_df = None
        st.session_state.analysis_df = None
        st.session_state.risk_result = None
        st.session_state.source_note = source_note
        if "event_name" in standardized.columns and standardized["event_name"].notna().any():
            st.session_state.event_name = str(standardized["event_name"].dropna().iloc[0])
        st.success("数据已保存。下一步进入左侧“数据清洗”。")

if st.session_state.raw_df is not None:
    with st.expander("当前项目数据"):
        st.dataframe(st.session_state.raw_df.head(20), use_container_width=True)

