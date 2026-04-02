from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1560, 1060
bg = (15, 20, 35)
img = Image.new("RGB", (W, H), bg)
d = ImageDraw.Draw(img)

# ── font helpers ───────────────────────────────────────────────────────────────
def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = font(22, bold=True)
F_HEAD  = font(16, bold=True)
F_BODY  = font(13)
F_SMALL = font(12)

# ── colours ────────────────────────────────────────────────────────────────────
C_USER     = (52, 152, 219)    # blue  — UI / User Proxy
C_MANAGER  = (155, 89, 182)    # purple — Manager
C_CALC     = (46, 204, 113)    # green — Calculator
C_SQL      = (230, 126, 34)    # orange — SQL Query
C_ANALYZER = (52, 152, 219)    # blue  — Data Analyzer
C_TOOL     = (231, 76, 60)     # red   — Tool execution
C_TRACE    = (241, 196, 15)    # yellow — tracing
C_ARROW    = (189, 195, 199)
C_WHITE    = (255, 255, 255)
C_DARK     = (30, 39, 46)
C_PANEL    = (22, 30, 50)

# ── helpers ────────────────────────────────────────────────────────────────────
def box(xy, wh, fill, radius=10, outline=None, outline_w=2):
    x, y = xy; w, h = wh
    d.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=fill,
                         outline=outline or fill, width=outline_w)

def center_text(text, cx, cy, fnt, fill=C_WHITE):
    bb = d.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.text((cx - tw//2, cy - th//2), text, font=fnt, fill=fill)

def left_text(text, x, y, fnt, fill=C_WHITE):
    d.text((x, y), text, font=fnt, fill=fill)

def arrow(x1, y1, x2, y2, color=C_ARROW, width=2, head=8):
    d.line([(x1, y1), (x2, y2)], fill=color, width=width)
    if x1 == x2:  # vertical
        d.polygon([(x2, y2), (x2-head//2, y2-head), (x2+head//2, y2-head)], fill=color)
    else:          # horizontal
        d.polygon([(x2, y2), (x2-head, y2-head//2), (x2-head, y2+head//2)], fill=color)

# ══════════════════════════════════════════════════════════════════════════════
# Title
# ══════════════════════════════════════════════════════════════════════════════
center_text("AutoGen Multi-Agent — Architecture Diagram", W//2, 28, font(20, bold=True))

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — main flow  (x=40..700)
# ══════════════════════════════════════════════════════════════════════════════
LX, BW = 40, 640

# 1. Gradio UI
y = 55
box((LX, y), (BW, 58), C_USER, outline=(100,180,240))
center_text("Gradio ChatInterface  (main.py)", LX+BW//2, y+18, F_HEAD)
center_text("User types message  →  gradio_interface(message)", LX+BW//2, y+40, F_BODY)

arrow(LX+BW//2, y+58, LX+BW//2, y+80)

# span label
span_y = y + 62
box((LX+BW//2-145, span_y), (290, 22), C_TRACE, radius=5)
center_text('OTel span "autogen" [AGENT]  — records input/output', LX+BW//2, span_y+11, F_SMALL, (20,20,20))

# 2. run_autogen_agents
y2 = y + 86
box((LX, y2), (BW, 100), C_MANAGER, outline=(180,120,210))
center_text("run_autogen_agents()  (router.py)", LX+BW//2, y2+16, F_HEAD)
lines = [
    "  • Extracts parent OTel context (TraceContextTextMapPropagator)",
    '  • Opens child span "agents_call" [CHAIN]',
    "  • Builds LLM config → llama-3.2-3b via LM Studio (localhost:1234)",
    "  • Creates 5 agents + 2 registered tools",
    "  • Starts GroupChat(max_round=15) and GroupChatManager",
]
for i, line in enumerate(lines):
    left_text(line, LX+10, y2+34+i*13, F_SMALL)

arrow(LX+BW//2, y2+100, LX+BW//2, y2+122)

# 3. GroupChat label
gc_y = y2 + 106
box((LX+BW//2-120, gc_y), (240, 22), C_TRACE, radius=5)
center_text("GroupChat  initiated by User_Proxy", LX+BW//2, gc_y+11, F_SMALL, (20,20,20))

# 4. GroupChat Manager box
y3 = y2 + 130
box((LX, y3), (BW, 75), (60, 40, 90), outline=C_MANAGER)
center_text("GroupChatManager  (LLM-driven speaker selection)", LX+BW//2, y3+16, F_HEAD)
left_text("  Each round: LLM picks which agent speaks next", LX+10, y3+36, F_SMALL)
left_text("  Manager orchestrates: calls agents, aggregates results, appends TERMINATE", LX+10, y3+52, F_SMALL)

arrow(LX+BW//2, y3+75, LX+BW//2, y3+97)

# 5. Agents row
y4 = y3 + 100
agent_w = 148
agent_h = 80
gap = 10
agents = [
    ("Manager", C_MANAGER, "Orchestrates\nall agents"),
    ("Calculator", C_CALC, "Calls\nCalculator_Tool"),
    ("SQL_Query", C_SQL, "Generates &\nruns SQL"),
    ("Data_Analyzer", C_ANALYZER, "Analyzes\ndata"),
    ("User_Proxy", C_USER, "Executes tools\nTerminates"),
]
agent_xs = []
total_w = len(agents) * agent_w + (len(agents)-1) * gap
start_x = LX + (BW - total_w) // 2
for i, (name, col, desc) in enumerate(agents):
    ax = start_x + i * (agent_w + gap)
    agent_xs.append(ax + agent_w//2)
    box((ax, y4), (agent_w, agent_h), col, outline=(255,255,255), outline_w=1)
    center_text(name, ax+agent_w//2, y4+20, F_HEAD)
    for j, dline in enumerate(desc.split("\n")):
        center_text(dline, ax+agent_w//2, y4+42+j*16, F_SMALL)

# arrows from GroupChatManager to each agent
for ax_cx in agent_xs:
    arrow(ax_cx, y3+75, ax_cx, y4, color=(180,180,180), width=1, head=6)

# 6. Tool execution boxes (below Calculator and SQL_Query agents)
y5 = y4 + agent_h + 30
tool_w = 280
tool_h = 70

# Calculator tool
calc_ax = agent_xs[1]
box((calc_ax - tool_w//2, y5), (tool_w, tool_h), (30, 80, 50), outline=C_CALC)
center_text("calculator_tool  (calculator.py)", calc_ax, y5+16, F_HEAD)
left_text("  Input: CalculatorInput(a, b, operator)", calc_ax-tool_w//2+8, y5+34, F_SMALL)
left_text("  OTel span [CHAIN]  →  returns int", calc_ax-tool_w//2+8, y5+52, F_SMALL)
arrow(calc_ax, y4+agent_h, calc_ax, y5, color=C_CALC, width=2, head=7)

# SQL tool
sql_ax = agent_xs[2]
box((sql_ax - tool_w//2, y5), (tool_w, tool_h), (80, 50, 20), outline=C_SQL)
center_text("run_sql_query  (sql_query.py)", sql_ax, y5+16, F_HEAD)
left_text("  Input: SQLQueryInput(sql_query)", sql_ax-tool_w//2+8, y5+34, F_SMALL)
left_text("  Sanitizes → run_query() → returns str", sql_ax-tool_w//2+8, y5+52, F_SMALL)
arrow(sql_ax, y4+agent_h, sql_ax, y5, color=C_SQL, width=2, head=7)

# User_Proxy executes tools — dashed lines
proxy_ax = agent_xs[4]
mid_y = y4 + agent_h + 15
d.line([(proxy_ax, y4+agent_h), (proxy_ax, mid_y)], fill=C_USER, width=2)
d.line([(proxy_ax, mid_y), (calc_ax, mid_y)], fill=C_USER, width=2)
d.line([(proxy_ax, mid_y), (sql_ax, mid_y)], fill=C_USER, width=2)
center_text("User_Proxy executes tool calls", proxy_ax - 60, mid_y - 10, F_SMALL, C_USER)

# 7. Final output
y6 = y5 + tool_h + 30
box((LX, y6), (BW, 54), (50, 80, 50), outline=(100,200,100))
center_text('Manager sends final message ending with "TERMINATE"', LX+BW//2, y6+18, F_HEAD)
center_text("User_Proxy detects TERMINATE → chat ends → last message returned to Gradio", LX+BW//2, y6+38, F_BODY)

# arrows from tools back up to manager
arrow(calc_ax, y5+tool_h, calc_ax, y6, color=C_ARROW, width=1, head=5)
arrow(sql_ax, y5+tool_h, sql_ax, y6, color=C_ARROW, width=1, head=5)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — OTel Trace tree
# ══════════════════════════════════════════════════════════════════════════════
RX = 720
PW = W - RX - 20
box((RX, 55), (PW, H-75), C_PANEL, radius=12, outline=(60,80,110))
center_text("OpenTelemetry Trace Hierarchy  →  Phoenix", RX+PW//2, 70, F_HEAD, C_TRACE)

px = RX + 18
py = 92

def trace_row(label, color, indent=0, y=None):
    global py
    if y is not None:
        py = y
    ix = px + indent * 22
    box((ix, py), (PW - indent*22 - 36, 28), color, radius=6, outline=(255,255,255), outline_w=1)
    center_text(label, ix + (PW - indent*22 - 36)//2, py+14, F_SMALL)
    py += 34

trace_row('span: "autogen"  [AGENT]  — main.py', C_USER)
left_text("  Records: INPUT_VALUE=user message, OUTPUT_VALUE=final answer", px+22, py, F_SMALL, C_ARROW)
py += 20
trace_row('  span: "agents_call"  [CHAIN]  — router.py', C_MANAGER, indent=1)
left_text("  Records: INPUT_VALUE=query, LLM_TOOLS=[calculator, run_sql_query]", px+44, py, F_SMALL, C_ARROW)
py += 20
trace_row('    span: "calculator_tool"  [CHAIN]', C_CALC, indent=2)
left_text("    Records: INPUT_VALUE=CalculatorInput, OUTPUT_VALUE=int result", px+66, py, F_SMALL, C_ARROW)
py += 20
trace_row('    span: "run_sql_query"  [CHAIN]', C_SQL, indent=2)
left_text("    Records: INPUT_VALUE=sql string, OUTPUT_VALUE=query results", px+66, py, F_SMALL, C_ARROW)
py += 30

# divider
d.line([(px, py), (RX+PW-18, py)], fill=(60,80,110), width=1)
py += 14

# Agents legend
center_text("Agent Roles", RX+PW//2, py+8, F_HEAD, C_WHITE)
py += 26
legend = [
    (C_MANAGER,  "Manager         — orchestrates agents, aggregates, sends TERMINATE"),
    (C_CALC,     "Calculator      — calls Calculator_Tool (arithmetic on integers)"),
    (C_SQL,      "SQL_Query       — generates SQL, calls SQL_Query_Executor_Tool"),
    (C_ANALYZER, "Data_Analyzer   — interprets SQL results, no tools"),
    (C_USER,     "User_Proxy      — executes tools, detects TERMINATE, ends chat"),
]
for col, label in legend:
    box((px+4, py), (18, 18), col, radius=4)
    left_text(label, px+28, py+3, F_SMALL)
    py += 26

d.line([(px, py+4), (RX+PW-18, py+4)], fill=(60,80,110), width=1)
py += 18

# Typical flow
center_text("Typical Conversation Flow", RX+PW//2, py+8, F_HEAD, C_WHITE)
py += 26
steps = [
    "1. User sends query via Gradio",
    '2. Manager reads query, decides to call SQL_Query first',
    "3. SQL_Query agent generates SQL → User_Proxy runs it",
    "4. Results returned to GroupChat",
    "5. Manager routes results to Data_Analyzer",
    "6. Data_Analyzer produces insights",
    '7. Manager aggregates → sends final reply + "TERMINATE"',
    "8. User_Proxy detects TERMINATE → chat ends",
    "9. Last message returned to Gradio UI",
]
for step in steps:
    left_text(step, px+6, py, F_SMALL)
    py += 20

# ══════════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════════
out = os.path.join(os.path.dirname(__file__), "autogen_diagram.jpg")
img.save(out, "JPEG", quality=92)
print("saved", out)
