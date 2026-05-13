from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from src.preprocess import segment_text


def cluster_texts_kmeans(texts: list[str], n_clusters: int = 5) -> pd.DataFrame:
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer

    valid_texts = [str(text) for text in texts if str(text).strip()]
    if not valid_texts:
        return pd.DataFrame(columns=["content", "cluster"])

    n_clusters = max(1, min(n_clusters, len(valid_texts)))
    if n_clusters == 1:
        return pd.DataFrame({"content": valid_texts, "cluster": [0] * len(valid_texts)})

    vectorizer = TfidfVectorizer(tokenizer=lambda value: segment_text(value), token_pattern=None)
    matrix = vectorizer.fit_transform(valid_texts)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = model.fit_predict(matrix)
    return pd.DataFrame({"content": valid_texts, "cluster": labels})


def attach_clusters(df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    clustered = cluster_texts_kmeans(df[source_col].fillna("").astype(str).tolist(), n_clusters)
    result = df.copy().reset_index(drop=True)
    result["cluster"] = clustered["cluster"].values if len(clustered) == len(result) else -1
    return result


def extract_cluster_keywords(df: pd.DataFrame, top_n: int = 8) -> dict[int, list[str]]:
    keywords: dict[int, list[str]] = {}
    if "cluster" not in df.columns:
        return keywords
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    for cluster_id, group in df.groupby("cluster"):
        counter: Counter[str] = Counter()
        for text in group[source_col].fillna("").astype(str):
            counter.update(segment_text(text))
        keywords[int(cluster_id)] = [word for word, _ in counter.most_common(top_n)]
    return keywords


def extract_representative_comments(df: pd.DataFrame, top_n: int = 3) -> dict[int, list[str]]:
    representatives: dict[int, list[str]] = {}
    if "cluster" not in df.columns:
        return representatives
    source_col = "clean_content" if "clean_content" in df.columns else "content"
    for cluster_id, group in df.groupby("cluster"):
        ranked = group.assign(_length=group[source_col].fillna("").astype(str).str.len())
        rows = ranked.sort_values("_length", ascending=False).head(top_n)
        representatives[int(cluster_id)] = rows[source_col].fillna("").astype(str).tolist()
    return representatives


def cluster_summary(df: pd.DataFrame, cluster_keywords: dict[int, list[str]] | None = None) -> pd.DataFrame:
    if "cluster" not in df.columns:
        return pd.DataFrame(columns=["cluster", "count", "ratio", "keywords"])
    total = len(df)
    rows: list[dict[str, Any]] = []
    for cluster_id, group in df.groupby("cluster"):
        rows.append(
            {
                "cluster": int(cluster_id),
                "count": len(group),
                "ratio": round(len(group) / total * 100, 2) if total else 0,
                "keywords": "、".join((cluster_keywords or {}).get(int(cluster_id), [])),
            }
        )
    return pd.DataFrame(rows).sort_values("count", ascending=False)

