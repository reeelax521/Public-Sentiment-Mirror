from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.preprocess import load_stopwords, segment_text


def tokenize_texts(texts: Iterable[str]) -> list[list[str]]:
    stopwords = load_stopwords()
    return [segment_text(text, stopwords) for text in texts]


def word_frequency(texts: Iterable[str], top_n: int = 50) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for tokens in tokenize_texts(texts):
        counter.update(tokens)
    return pd.DataFrame(counter.most_common(top_n), columns=["word", "count"])


def extract_keywords_tfidf(texts: list[str], top_n: int = 30) -> pd.DataFrame:
    from sklearn.feature_extraction.text import TfidfVectorizer

    if not texts:
        return pd.DataFrame(columns=["word", "score"])

    vectorizer = TfidfVectorizer(tokenizer=lambda value: segment_text(value), token_pattern=None)
    matrix = vectorizer.fit_transform(texts)
    scores = matrix.mean(axis=0).A1
    words = vectorizer.get_feature_names_out()
    rows = sorted(zip(words, scores), key=lambda item: item[1], reverse=True)[:top_n]
    return pd.DataFrame(rows, columns=["word", "score"])


def get_chinese_font_path() -> str | None:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return None


def generate_wordcloud_image(texts: Iterable[str]):
    from wordcloud import WordCloud

    tokens = []
    for parts in tokenize_texts(texts):
        tokens.extend(parts)
    font_path = get_chinese_font_path()
    return WordCloud(
        width=1200,
        height=620,
        background_color="white",
        font_path=font_path,
        collocations=False,
        max_words=120,
    ).generate(" ".join(tokens)).to_image()

