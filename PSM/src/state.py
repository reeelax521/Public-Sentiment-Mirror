from __future__ import annotations

import streamlit as st


DEFAULT_KEYS = {
    "raw_df": None,
    "clean_df": None,
    "quality_report": None,
    "keyword_df": None,
    "word_freq_df": None,
    "cluster_df": None,
    "cluster_keywords": None,
    "analysis_df": None,
    "risk_result": None,
    "target_entity": "",
    "event_name": "",
    "source_note": "本案例数据为演示数据，不代表真实平台完整舆情。",
}


def init_state() -> None:
    for key, value in DEFAULT_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_working_df():
    clean_df = st.session_state.get("clean_df")
    if clean_df is not None:
        return clean_df
    return st.session_state.get("raw_df")


def has_data() -> bool:
    return st.session_state.get("raw_df") is not None


def has_clean_data() -> bool:
    return st.session_state.get("clean_df") is not None
