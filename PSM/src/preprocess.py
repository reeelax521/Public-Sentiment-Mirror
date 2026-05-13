from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import jieba
except Exception:  # pragma: no cover
    jieba = None

from src.paths import CONFIG_DIR, SAMPLE_DIR


STANDARD_COLUMNS = [
    "id",
    "platform",
    "event_name",
    "publish_time",
    "content",
    "like_count",
    "comment_count",
    "repost_count",
    "url",
    "author_type",
    "target",
]

COLUMN_ALIASES = {
    "id": ["id", "编号", "序号", "文本编号"],
    "platform": ["platform", "平台", "来源", "source", "渠道"],
    "event_name": ["event_name", "事件", "事件名称", "项目", "话题"],
    "publish_time": ["publish_time", "发布时间", "时间", "日期", "created_at", "time", "date"],
    "content": ["content", "文本", "正文", "内容", "评论", "评论内容", "留言", "回答", "text"],
    "like_count": ["like_count", "点赞", "点赞数", "赞", "likes"],
    "comment_count": ["comment_count", "评论数", "回复数", "comments"],
    "repost_count": ["repost_count", "转发数", "分享数", "收藏数", "reposts", "shares"],
    "url": ["url", "链接", "原文链接", "link"],
    "author_type": ["author_type", "作者类型", "用户类型", "身份"],
    "target": ["target", "对象", "目标对象", "立场对象"],
}

URL_RE = re.compile(r"https?://\S+|www\.\S+")
HTML_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE,
)


def list_sample_files() -> list[Path]:
    return sorted(SAMPLE_DIR.glob("*.csv"))


def load_user_data(file: Any) -> pd.DataFrame:
    suffix = Path(file.name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file)
    raise ValueError("仅支持 CSV、XLSX 或 XLS 文件。")


def load_sample_data(file_name: str | None = None) -> pd.DataFrame:
    files = list_sample_files()
    if not files:
        raise FileNotFoundError("data/sample 中还没有样例数据。")
    target = SAMPLE_DIR / file_name if file_name else files[0]
    return pd.read_csv(target)


def build_dataframe_from_text(pasted_text: str, platform: str = "文本粘贴", event_name: str = "") -> pd.DataFrame:
    lines = [line.strip() for line in pasted_text.splitlines() if line.strip()]
    return pd.DataFrame(
        {
            "id": range(1, len(lines) + 1),
            "platform": platform,
            "event_name": event_name,
            "content": lines,
        }
    )


def infer_column_mapping(columns: list[str]) -> dict[str, str]:
    lowered = {str(col).strip().lower(): col for col in columns}
    mapping: dict[str, str] = {}
    for standard, aliases in COLUMN_ALIASES.items():
        found = ""
        for alias in aliases:
            if alias.lower() in lowered:
                found = lowered[alias.lower()]
                break
        mapping[standard] = found
    return mapping


def standardize_columns(df: pd.DataFrame, mapping: dict[str, str] | None = None) -> pd.DataFrame:
    result = df.copy()
    mapping = mapping or infer_column_mapping([str(col) for col in result.columns])

    for standard, source in mapping.items():
        if not source or source not in result.columns:
            continue
        if standard in result.columns:
            result[standard] = result[standard].where(result[standard].notna(), result[source])
        else:
            result = result.rename(columns={source: standard})

    if "id" not in result.columns:
        result.insert(0, "id", range(1, len(result) + 1))

    if "content" in result.columns:
        result["content"] = result["content"].fillna("").astype(str)

    for column in ["like_count", "comment_count", "repost_count"]:
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0).astype(int)

    if "publish_time" in result.columns:
        result["publish_time"] = pd.to_datetime(result["publish_time"], errors="coerce")

    return result


def clean_text(text: Any, remove_urls: bool = True, remove_emoji: bool = False) -> str:
    if pd.isna(text):
        return ""
    value = str(text)
    value = HTML_RE.sub(" ", value)
    if remove_urls:
        value = URL_RE.sub(" ", value)
    if remove_emoji:
        value = EMOJI_RE.sub(" ", value)
    value = value.replace("\u200b", " ")
    value = SPACE_RE.sub(" ", value).strip()
    return value


def load_stopwords() -> set[str]:
    path = CONFIG_DIR / "stopwords.txt"
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def segment_text(text: Any, stopwords: set[str] | None = None) -> list[str]:
    stopwords = stopwords or load_stopwords()
    cleaned = clean_text(text)
    if not cleaned:
        return []
    if jieba is None:
        return [token for token in re.split(r"\W+", cleaned) if token and token not in stopwords]
    tokens = jieba.lcut(cleaned)
    return [
        token.strip()
        for token in tokens
        if token.strip() and token.strip() not in stopwords and len(token.strip()) > 1
    ]


def preprocess_dataframe(
    df: pd.DataFrame,
    remove_urls: bool = True,
    remove_emoji: bool = False,
    remove_duplicates: bool = True,
    min_length: int = 1,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if "content" not in df.columns:
        raise ValueError("数据中没有 content 字段，请先在数据中心完成字段映射。")

    raw = df.copy()
    result = df.copy()
    result["clean_content"] = result["content"].apply(
        lambda value: clean_text(value, remove_urls=remove_urls, remove_emoji=remove_emoji)
    )
    result["text_length"] = result["clean_content"].str.len()

    blank_mask = result["clean_content"].str.len() == 0
    short_mask = result["text_length"] < min_length
    before_drop = len(result)
    result = result.loc[~blank_mask & ~short_mask].copy()
    removed_blank = before_drop - len(result)

    duplicate_count = int(result.duplicated(subset=["clean_content"]).sum())
    if remove_duplicates:
        result = result.drop_duplicates(subset=["clean_content"]).copy()

    stopwords = load_stopwords()
    result["tokens"] = result["clean_content"].apply(lambda text: " ".join(segment_text(text, stopwords)))

    report = get_data_quality_report(raw, result)
    report["removed_blank_or_short"] = removed_blank
    report["duplicate_text_count"] = duplicate_count
    report["removed_duplicates"] = duplicate_count if remove_duplicates else 0
    return result.reset_index(drop=True), report


def get_data_quality_report(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> dict[str, Any]:
    raw_count = len(raw_df)
    valid_count = len(clean_df)
    report: dict[str, Any] = {
        "raw_count": raw_count,
        "valid_count": valid_count,
        "retention_rate": round(valid_count / raw_count * 100, 2) if raw_count else 0,
        "average_length": round(float(clean_df["clean_content"].str.len().mean()), 2)
        if "clean_content" in clean_df.columns and not clean_df.empty
        else 0,
        "platform_count": int(clean_df["platform"].nunique()) if "platform" in clean_df.columns else 0,
    }

    if "publish_time" in clean_df.columns and clean_df["publish_time"].notna().any():
        time_min = clean_df["publish_time"].min()
        time_max = clean_df["publish_time"].max()
        report["time_range"] = f"{time_min:%Y-%m-%d} 至 {time_max:%Y-%m-%d}"
    else:
        report["time_range"] = "无有效时间字段"

    return report


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")

