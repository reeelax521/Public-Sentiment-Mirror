from __future__ import annotations

import streamlit as st

from src.state import init_state


st.set_page_config(
    page_title="舆情镜像",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()

st.title("舆情镜像")
st.caption("面向日常与学术场景的社交媒体舆情感知、语义分析、风险研判与报告生成系统")

st.markdown(
    """
欢迎来到第一版项目骨架。这个系统先保证本地可运行、数据可导入、分析链路可闭环，
再逐步增强语义模型和作品集展示效果。

**当前版本已经包含：**

- 数据上传、文本粘贴和内置案例数据
- 字段映射、数据清洗与质量诊断
- 高频词、TF-IDF 关键词、词云和 K-means 观点聚类
- 轻量情感分析、规则立场检测、不确定信息识别
- 舆情风险辅助评分与 Markdown/Word 报告生成

**建议使用顺序：**

1. 打开左侧 `数据中心`，上传或选择样例数据。
2. 进入 `数据清洗`，执行清洗并保存结果。
3. 依次查看 `舆情概览`、`主题观点`、`情感立场`、`风险研判`。
4. 最后进入 `报告生成`，下载课程作业可用的初版分析报告。
"""
)

st.info(
    "第一版以可解释、轻量、可运行为优先。SBERT、BERTopic、BERT 情感模型会作为后续增强模块接入。"
)

with st.expander("项目定位"):
    st.markdown(
        """
本项目面向社交媒体热点事件、问卷开放题、访谈文本和日常评论材料，通过数据清洗、
关键词提取、观点聚类、情感分析、立场检测、不确定信息识别、风险辅助评分和报告生成，
帮助用户快速理解大量文本中的公众情绪、核心议题、观点阵营和风险信号。
"""
    )
