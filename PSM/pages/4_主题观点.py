from __future__ import annotations

import streamlit as st

from src.keywords import extract_keywords_tfidf, generate_wordcloud_image, word_frequency
from src.preprocess import dataframe_to_csv_bytes
from src.topic_modeling import (
    attach_clusters,
    cluster_summary,
    extract_cluster_keywords,
    extract_representative_comments,
)
from src.visualization import bar_chart
from src.state import init_state


init_state()
st.title("主题观点")
st.caption("用高频词、TF-IDF 和 K-means 聚类观察大家在讨论什么。")

df = st.session_state.clean_df
if df is None:
    st.info("请先完成“数据清洗”。")
    st.stop()

source_col = "clean_content" if "clean_content" in df.columns else "content"
texts = df[source_col].fillna("").astype(str).tolist()

with st.sidebar:
    st.header("分析设置")
    top_n = st.slider("关键词数量", 10, 80, 30, 5)
    n_clusters = st.slider("观点聚类数量 K", 2, min(8, max(2, len(df))), min(4, max(2, min(8, len(df)))))

if st.button("运行主题观点分析", type="primary"):
    word_freq = word_frequency(texts, top_n=top_n)
    keyword_df = extract_keywords_tfidf(texts, top_n=top_n)
    cluster_df = attach_clusters(df, n_clusters=n_clusters)
    cluster_keywords = extract_cluster_keywords(cluster_df)

    st.session_state.word_freq_df = word_freq
    st.session_state.keyword_df = keyword_df
    st.session_state.cluster_df = cluster_df
    st.session_state.cluster_keywords = cluster_keywords
    st.success("主题观点分析完成。")

if st.session_state.keyword_df is not None:
    left, right = st.columns(2)
    with left:
        st.subheader("高频词")
        st.dataframe(st.session_state.word_freq_df, use_container_width=True)
        st.plotly_chart(
            bar_chart(st.session_state.word_freq_df.head(20), "word", "count", "高频词 Top 20"),
            use_container_width=True,
        )

    with right:
        st.subheader("TF-IDF 关键词")
        st.dataframe(st.session_state.keyword_df, use_container_width=True)
        try:
            image = generate_wordcloud_image(texts)
            st.image(image, caption="词云")
        except Exception as error:
            st.warning(f"词云暂时无法生成：{error}")

if st.session_state.cluster_df is not None:
    st.subheader("观点聚类")
    summary_df = cluster_summary(st.session_state.cluster_df, st.session_state.cluster_keywords)
    st.dataframe(summary_df, use_container_width=True)
    st.plotly_chart(bar_chart(summary_df, "cluster", "count", "聚类规模"), use_container_width=True)

    representatives = extract_representative_comments(st.session_state.cluster_df)
    for cluster_id, comments in representatives.items():
        with st.expander(f"主题 {cluster_id}：{'、'.join(st.session_state.cluster_keywords.get(cluster_id, []))}"):
            for item in comments:
                st.write(f"- {item}")

    st.download_button(
        "下载带聚类结果的数据",
        data=dataframe_to_csv_bytes(st.session_state.cluster_df),
        file_name="yuqing_cluster_result.csv",
        mime="text/csv",
    )

