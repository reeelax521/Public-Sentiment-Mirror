# 舆情镜像

面向日常与学术场景的社交媒体舆情感知、语义分析、风险研判与报告生成系统。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\streamlit run app.py
```

如果你使用的是我已经在上级目录创建好的本地环境，也可以在本文件夹运行：

```powershell
..\.venv\Scripts\python -m streamlit run app.py
```

打开浏览器后，按左侧页面顺序使用：

1. 数据中心
2. 数据清洗
3. 舆情概览
4. 主题观点
5. 情感立场
6. 风险研判
7. 报告生成

## 当前能力

- CSV/Excel 上传、文本粘贴、样例数据
- 字段映射与标准化
- 文本清洗、去重、质量诊断
- 高频词、TF-IDF 关键词、词云
- TF-IDF + K-means 观点聚类
- 轻量情感词典分析
- 规则立场检测
- 不确定信息识别
- 舆情风险辅助评分
- Markdown 与 Word 报告下载

## 方法说明

第一版优先使用轻量、可解释的方法，保证课程展示和作品集演示能够稳定运行。SBERT、BERTopic、BERT 情感分类等高级模型将作为后续可选模块接入，不影响基础功能。

## 合规说明

系统默认以用户上传数据、粘贴文本和案例库为入口，不提供绕过平台权限的自动爬取能力。若使用演示数据，报告中会标注“本案例数据为演示数据，不代表真实平台完整舆情”。
