from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLOR_SEQUENCE = ["#2454A6", "#D64F3C", "#4E9F70", "#F0A43A", "#7B61A8", "#5E7D8A"]


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str):
    return px.bar(df, x=x, y=y, title=title, color_discrete_sequence=COLOR_SEQUENCE)


def pie_chart(df: pd.DataFrame, names: str, values: str, title: str):
    return px.pie(df, names=names, values=values, title=title, color_discrete_sequence=COLOR_SEQUENCE)


def line_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None):
    return px.line(df, x=x, y=y, color=color, markers=True, title=title, color_discrete_sequence=COLOR_SEQUENCE)


def radar_chart(metrics: dict[str, float], label_map: dict[str, str]):
    labels = [label_map.get(key, key) for key in metrics]
    values = list(metrics.values())
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + values[:1],
            theta=labels + labels[:1],
            fill="toself",
            name="风险指标",
        )
    )
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        showlegend=False,
        title="舆情风险雷达图",
    )
    return fig

