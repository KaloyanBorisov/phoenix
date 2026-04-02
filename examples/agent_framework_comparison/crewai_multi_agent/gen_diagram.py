import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(22, 15))
ax.set_xlim(0, 22)
ax.set_ylim(0, 15)
ax.axis("off")
fig.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#1a1a2e")

BG = "#1a1a2e"

def box(x, y, w, h, edge_color, title, lines=None, title_size=13):
    """Draw a rounded box with a title and optional body lines."""
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.15",
                          linewidth=2, edgecolor=edge_color,
                          facecolor=edge_color + "28")
    ax.add_patch(rect)
    n = len(lines) if lines else 0
    total_text_h = title_size * 0.035 + n * 0.38
    start_y = y + h / 2 + total_text_h / 2
    ax.text(x + w / 2, start_y, title,
            ha="center", va="center",
            fontsize=title_size, fontweight="bold", color=edge_color)
    if lines:
        for i, line in enumerate(lines):
            ax.text(x + w / 2, start_y - 0.42 - i * 0.38,
                    line, ha="center", va="center",
                    fontsize=10, color="#dddddd",
                    fontfamily="monospace")

def arrow(x1, y1, x2, y2, color, lw=2.0, label=None, rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=18,
                                connectionstyle=f"arc3,rad={rad}"))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.15, my, label, ha="left", va="center",
                fontsize=9, color=color,
                bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="none"))

# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(11, 14.4, "CrewAI  Multi-Agent Architecture",
        ha="center", va="center", fontsize=20, fontweight="bold", color="#ffffff")
ax.text(11, 13.9, "Process.hierarchical  •  LLM: gpt-4o",
        ha="center", va="center", fontsize=12, color="#aaaaaa")

# ── User Query ────────────────────────────────────────────────────────────────
box(7.5, 12.6, 7, 1.0, "#00e5ff", "User Query",
    lines=["crew.kickoff(query)  →  result.raw"], title_size=14)

# ── Manager Agent ─────────────────────────────────────────────────────────────
box(5.5, 10.5, 11, 1.7, "#ff9800", "Manager Agent",
    lines=[
        "role='Manager'   |   allow_delegation=True",
        "goal: identify needed agents, delegate, aggregate, return final answer",
    ], title_size=14)

arrow(11, 12.6, 11, 12.2, "#00e5ff", label="query")
arrow(11, 10.5, 11, 10.0, "#ff9800", label="delegates")

# ── Crew boundary ─────────────────────────────────────────────────────────────
crew_rect = FancyBboxPatch((0.3, 3.0), 21.4, 9.3,
                           boxstyle="round,pad=0.2",
                           linewidth=1.5, edgecolor="#404060",
                           facecolor="none", linestyle="--")
ax.add_patch(crew_rect)
ax.text(0.7, 12.2, "Crew(agents=[...], tasks=[task], process=Process.hierarchical, manager_agent=manager)",
        fontsize=9, color="#606080", fontfamily="monospace")

# ── Specialist Agents ─────────────────────────────────────────────────────────
agents = [
    (0.5,  "#4caf50", "Calculator Agent", [
        "role='Calculator'",
        "allow_delegation=False",
        "tools=[CalculatorTool()]",
        "goal: arithmetic +  -  *  /",
    ]),
    (7.5,  "#ab47bc", "SQL Query Agent", [
        "role='SQL Query'",
        "allow_delegation=False",
        "tools=[SQLQueryTool()]",
        "backstory=SQL_SYSTEM_PROMPT",
        ".format(SCHEMA=..., TABLE=...)",
    ]),
    (14.5, "#2196f3", "Data Analyzer Agent", [
        "role='Data Analyzer'",
        "allow_delegation=False",
        "# no tools – pure LLM",
        "goal: insights & trends",
    ]),
]

agent_cx = []
for ax_x, color, name, lines in agents:
    box(ax_x, 7.0, 6.5, 2.8, color, name, lines=lines, title_size=13)
    cx = ax_x + 3.25
    agent_cx.append((cx, color))
    # arrow from manager down to each agent
    ax.annotate("", xy=(cx, 9.8), xytext=(11, 10.5),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                                mutation_scale=16,
                                connectionstyle="arc3,rad=0.0"))

# ── Tools ─────────────────────────────────────────────────────────────────────
tools = [
    (0.5,  "#4caf50", "CalculatorTool", [
        "def _run(self, op, a, b):",
        "  ops = {'+':add, '-':sub,",
        "         '*':mul, '/':div}",
        "  return ops[op](a, b)",
    ]),
    (7.5,  "#ab47bc", "SQLQueryTool", [
        "def _run(self, query):",
        "  conn = sqlite3.connect(DB)",
        "  result = conn.execute(query)",
        "  return result.fetchall()",
    ]),
]

for tx, color, name, lines in tools:
    box(tx, 4.0, 6.5, 2.7, color, name, lines=lines, title_size=12)
    arrow(tx + 3.25, 7.0, tx + 3.25, 6.7, color=color, label="uses")

# ── DB ────────────────────────────────────────────────────────────────────────
box(7.5, 3.1, 6.5, 0.75, "#ab47bc", "SQLite Database",
    lines=["get_schema()  |  get_table()"], title_size=11)
arrow(10.75, 4.0, 10.75, 3.85, "#ab47bc")

# ── Task ──────────────────────────────────────────────────────────────────────
box(14.5, 4.0, 6.5, 2.7, "#2196f3", "Task", lines=[
    "Task(",
    '  description=query,',
    '  expected_output=',
    '    "final result in one msg"',
    ")",
], title_size=12)

# ── result arrow back up (curved) ─────────────────────────────────────────────
ax.annotate("", xy=(7.5, 13.1), xytext=(5.5, 10.5),
            arrowprops=dict(arrowstyle="-|>", color="#00e5ff", lw=2,
                            mutation_scale=18,
                            connectionstyle="arc3,rad=-0.35"))
ax.text(5.3, 11.9, "result.raw", ha="center", va="center",
        fontsize=10, color="#00e5ff",
        bbox=dict(boxstyle="round,pad=0.3", fc=BG, ec="#00e5ff", lw=1))

plt.tight_layout(pad=0.5)
plt.savefig("crewai_multi_agent/crewai_diagram.jpg", dpi=180,
            bbox_inches="tight", facecolor=fig.get_facecolor())
print("saved")
