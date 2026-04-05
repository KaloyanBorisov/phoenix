# type: ignore
"""
Pulls span data from Phoenix Cloud for the 'cron-evals' project and generates
an interactive Plotly HTML report covering latency, token usage, and trace timelines.
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from plotly.subplots import make_subplots

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from phoenix.client import Client

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(_SCRIPT_DIR, "report.html")
PROJECT = "cron-evals"

spans_client = Client(
    base_url=os.environ["PHOENIX_COLLECTOR_ENDPOINT"],
    api_key=os.environ["PHOENIX_API_KEY"],
)

df = spans_client.spans.get_spans_dataframe(project_name=PROJECT)
df["duration_ms"] = (df["end_time"] - df["start_time"]).dt.total_seconds() * 1000
df["start_time_local"] = df["start_time"].dt.tz_convert("UTC")

# ── Root spans only (no parent) ───────────────────────────────────────────────
root_df = df[df["parent_id"].isna()].copy()

# ── LLM spans only ────────────────────────────────────────────────────────────
llm_df = df[df["span_kind"] == "LLM"].copy()

# ── Embedding spans only ──────────────────────────────────────────────────────
emb_df = df[df["span_kind"] == "EMBEDDING"].copy()


# ── Build figures ─────────────────────────────────────────────────────────────

# 1. Trace timeline (Gantt) — one row per root trace
fig_timeline = px.timeline(
    root_df.sort_values("start_time_local"),
    x_start="start_time",
    x_end="end_time",
    y="context.trace_id",
    color="status_code",
    hover_data={"duration_ms": ":.1f", "name": True},
    title="Trace Timeline — Root Spans",
    color_discrete_map={"OK": "#2ecc71", "ERROR": "#e74c3c"},
    labels={"context.trace_id": "Trace ID"},
)
fig_timeline.update_yaxes(showticklabels=False)

# 2. Latency distribution by span kind
fig_latency = px.box(
    df,
    x="span_kind",
    y="duration_ms",
    color="span_kind",
    points="all",
    title="Latency Distribution by Span Kind (ms)",
    labels={"duration_ms": "Duration (ms)", "span_kind": "Span Kind"},
)

# 3. Token usage over time (LLM spans)
fig_tokens = go.Figure()
if not llm_df.empty:
    fig_tokens = px.scatter(
        llm_df.dropna(subset=["attributes.llm.token_count.total"]),
        x="start_time",
        y="attributes.llm.token_count.total",
        color="attributes.llm.model_name",
        size="attributes.llm.token_count.total",
        hover_data={
            "attributes.llm.token_count.prompt": True,
            "attributes.llm.token_count.completion": True,
            "duration_ms": ":.1f",
        },
        title="Token Usage per LLM Call Over Time",
        labels={
            "attributes.llm.token_count.total": "Total Tokens",
            "attributes.llm.model_name": "Model",
        },
    )

# 4. Prompt vs completion tokens (stacked bar per LLM call)
if not llm_df.empty:
    token_df = llm_df.dropna(
        subset=["attributes.llm.token_count.prompt", "attributes.llm.token_count.completion"]
    ).copy()
    token_df["label"] = token_df["start_time"].dt.strftime("%H:%M:%S")
    fig_token_split = go.Figure(
        data=[
            go.Bar(
                name="Prompt",
                x=token_df["label"],
                y=token_df["attributes.llm.token_count.prompt"],
                marker_color="#3498db",
            ),
            go.Bar(
                name="Completion",
                x=token_df["label"],
                y=token_df["attributes.llm.token_count.completion"],
                marker_color="#e67e22",
            ),
        ]
    )
    fig_token_split.update_layout(
        barmode="stack",
        title="Prompt vs Completion Tokens per LLM Call",
        xaxis_title="Call Time (UTC)",
        yaxis_title="Tokens",
    )
else:
    fig_token_split = go.Figure().update_layout(title="No LLM token data available")

# 5. Span kind breakdown (pie)
fig_pie = px.pie(
    df,
    names="span_kind",
    title="Span Kind Distribution",
    hole=0.4,
)

# 6. End-to-end latency of root spans over time
fig_e2e = px.line(
    root_df.sort_values("start_time"),
    x="start_time",
    y="duration_ms",
    markers=True,
    title="End-to-End Trace Latency Over Time (ms)",
    labels={"duration_ms": "Duration (ms)", "start_time": "Time (UTC)"},
)
fig_e2e.add_hline(
    y=root_df["duration_ms"].mean(),
    line_dash="dash",
    line_color="red",
    annotation_text=f"avg {root_df['duration_ms'].mean():.0f} ms",
)

# 7. Embedding latency over time
fig_emb = go.Figure()
if not emb_df.empty:
    fig_emb = px.scatter(
        emb_df,
        x="start_time",
        y="duration_ms",
        color="attributes.embedding.model_name",
        title="Embedding Latency Over Time (ms)",
        labels={"duration_ms": "Duration (ms)"},
    )


# ── Assemble into a single HTML report ────────────────────────────────────────


def _fig_html(fig: go.Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False)


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>cron-evals — Phoenix Trace Report</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #0f1117; color: #e0e0e0; margin: 0; padding: 24px; }}
    h1   {{ color: #fff; border-bottom: 1px solid #333; padding-bottom: 12px; }}
    h2   {{ color: #aaa; font-size: 0.85rem; font-weight: 400; margin: 0 0 4px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
    .card {{ background: #1a1d27; border-radius: 10px; padding: 16px; }}
    .full {{ grid-column: 1 / -1; }}
    .stat {{ font-size: 2rem; font-weight: 700; color: #7c6af7; }}
    .stats {{ display: flex; gap: 32px; margin-bottom: 24px; }}
    .stat-box {{ background: #1a1d27; border-radius: 10px; padding: 16px 24px; }}
  </style>
</head>
<body>
  <h1>cron-evals — Phoenix Trace Report</h1>
  <p style="color:#888">Project: <strong style="color:#fff">{PROJECT}</strong> &nbsp;|&nbsp;
     Spans: <strong style="color:#fff">{len(df)}</strong> &nbsp;|&nbsp;
     Traces: <strong style="color:#fff">{df["context.trace_id"].nunique()}</strong> &nbsp;|&nbsp;
     Period: <strong style="color:#fff">{df["start_time"].min().strftime("%Y-%m-%d %H:%M")} → {df["start_time"].max().strftime("%Y-%m-%d %H:%M")} UTC</strong>
  </p>

  <div class="stats">
    <div class="stat-box">
      <h2>Avg end-to-end latency</h2>
      <div class="stat">{root_df["duration_ms"].mean():.0f} ms</div>
    </div>
    <div class="stat-box">
      <h2>P95 end-to-end latency</h2>
      <div class="stat">{root_df["duration_ms"].quantile(0.95):.0f} ms</div>
    </div>
    <div class="stat-box">
      <h2>Avg tokens / LLM call</h2>
      <div class="stat">{llm_df["attributes.llm.token_count.total"].mean():.0f}</div>
    </div>
    <div class="stat-box">
      <h2>Error rate</h2>
      <div class="stat">{(df["status_code"] == "ERROR").mean() * 100:.1f}%</div>
    </div>
  </div>

  <div class="grid">
    <div class="card full">{_fig_html(fig_timeline)}</div>
    <div class="card full">{_fig_html(fig_e2e)}</div>
    <div class="card">{_fig_html(fig_latency)}</div>
    <div class="card">{_fig_html(fig_pie)}</div>
    <div class="card full">{_fig_html(fig_tokens)}</div>
    <div class="card full">{_fig_html(fig_token_split)}</div>
    <div class="card full">{_fig_html(fig_emb)}</div>
  </div>
</body>
</html>"""

with open(OUTPUT_PATH, "w") as f:
    f.write(html)

print(f"Report saved to {OUTPUT_PATH}")
