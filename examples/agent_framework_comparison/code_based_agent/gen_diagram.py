from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1560, 1020
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
C_USER     = (52, 152, 219)    # blue  — User / Gradio
C_ROUTER   = (155, 89, 182)    # purple — Router
C_SKILL    = (46, 204, 113)    # green — Skills
C_TOOL     = (230, 126, 34)    # orange — Tool span
C_TRACE    = (241, 196, 15)    # yellow — tracing
C_ARROW    = (189, 195, 199)
C_WHITE    = (255, 255, 255)
C_PANEL    = (22, 30, 50)
C_SQL      = (230, 126, 34)
C_ANALYZE  = (26, 188, 156)    # teal — analyze_data

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
center_text("Code-Based Agent — Architecture Diagram", W//2, 28, font(20, bold=True))

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — main flow  (x=40..680)
# ══════════════════════════════════════════════════════════════════════════════
LX, BW = 40, 640

# 1. Gradio UI
y = 55
box((LX, y), (BW, 60), C_USER, outline=(100, 180, 240))
center_text("Gradio ChatInterface  (main.py)", LX+BW//2, y+18, F_HEAD)
center_text("User types message  →  gradio_interface(message, history)", LX+BW//2, y+40, F_BODY)

arrow(LX+BW//2, y+60, LX+BW//2, y+82)

span_y = y + 64
box((LX+BW//2-155, span_y), (310, 22), C_TRACE, radius=5)
center_text('OTel span "code_based_agent" [AGENT]  — records input/output', LX+BW//2, span_y+11, F_SMALL, (20, 20, 20))

# 2. Router
y2 = y + 88
box((LX, y2), (BW, 110), C_ROUTER, outline=(180, 120, 210))
center_text("router()  (router.py)", LX+BW//2, y2+16, F_HEAD)
lines = [
    "  • Extracts parent OTel context (TraceContextTextMapPropagator)",
    '  • Opens child span "router_call" [CHAIN]',
    "  • Injects system prompt (SYSTEM_PROMPT from router_template.py)",
    "  • Calls OpenAI GPT-4 with tool descriptions from SkillMap",
    "  • If tool_calls present → handle_tool_calls() → recurse",
    "  • Otherwise → returns final text content",
]
for i, line in enumerate(lines):
    left_text(line, LX+10, y2+34+i*13, F_SMALL)

arrow(LX+BW//2, y2+110, LX+BW//2, y2+132)

rspan_y = y2 + 114
box((LX+BW//2-130, rspan_y), (260, 22), C_TRACE, radius=5)
center_text('OTel span "router_call" [CHAIN]', LX+BW//2, rspan_y+11, F_SMALL, (20, 20, 20))

# 3. SkillMap
y3 = y2 + 138
box((LX, y3), (BW, 68), (40, 60, 80), outline=(80, 120, 180))
center_text("SkillMap  (skills/skill_map.py)", LX+BW//2, y3+16, F_HEAD)
left_text("  • Registers skills: GenerateSQLQuery, AnalyzeData", LX+10, y3+36, F_SMALL)
left_text("  • Provides OpenAI function descriptions + callable lookup by name", LX+10, y3+52, F_SMALL)

arrow(LX+BW//2, y3+68, LX+BW//2, y3+90)

# 4. Skills row
y4 = y3 + 94
skill_w = 295
skill_h = 80
gap = 10

skills = [
    ("generate_sql_query", C_SQL, "skills/generate_sql_query.py", "Generates SQL from NL\nRuns query on SQLite DB"),
    ("analyze_data", C_ANALYZE, "skills/analyze_data.py", "Analyzes query results\nReturns insights text"),
]

skill_xs = []
total_w = len(skills) * skill_w + (len(skills) - 1) * gap
start_x = LX + (BW - total_w) // 2
for i, (name, col, path, desc) in enumerate(skills):
    sx = start_x + i * (skill_w + gap)
    cx = sx + skill_w // 2
    skill_xs.append(cx)
    box((sx, y4), (skill_w, skill_h), col, outline=(255, 255, 255), outline_w=1)
    center_text(name, cx, y4+18, F_HEAD)
    center_text(path, cx, y4+36, F_SMALL, (200, 230, 200))
    for j, dline in enumerate(desc.split("\n")):
        center_text(dline, cx, y4+54+j*16, F_SMALL)
    arrow(cx, y3+68, cx, y4, color=col, width=2, head=7)

# OTel TOOL spans under each skill
y5 = y4 + skill_h + 20
for sx_cx, (name, col, _, _) in zip(skill_xs, skills):
    tw = 265
    box((sx_cx - tw//2, y5), (tw, 26), C_TRACE, radius=5)
    center_text(f'OTel span "{name}" [TOOL]', sx_cx, y5+13, F_SMALL, (20, 20, 20))
    arrow(sx_cx, y4+skill_h, sx_cx, y5, color=col, width=2, head=6)

# 5. Final response
y6 = y5 + 50
box((LX, y6), (BW, 52), (50, 80, 50), outline=(100, 200, 100))
center_text("Final response returned to router()  →  Gradio UI", LX+BW//2, y6+16, F_HEAD)
center_text("Outermost span closed; full trace visible in Phoenix", LX+BW//2, y6+36, F_BODY)

for sx_cx in skill_xs:
    arrow(sx_cx, y5+26, sx_cx, y6, color=C_ARROW, width=1, head=5)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — OTel Trace tree + legend
# ══════════════════════════════════════════════════════════════════════════════
RX = 720
PW = W - RX - 20
box((RX, 55), (PW, H - 75), C_PANEL, radius=12, outline=(60, 80, 110))
center_text("OpenTelemetry Trace Hierarchy  →  Phoenix", RX+PW//2, 70, F_HEAD, C_TRACE)

px = RX + 18
py = 92

def trace_row(label, color, indent=0):
    global py
    ix = px + indent * 22
    w = PW - indent * 22 - 36
    box((ix, py), (w, 28), color, radius=6, outline=(255, 255, 255), outline_w=1)
    center_text(label, ix + w//2, py+14, F_SMALL)
    py += 34

trace_row('span: "code_based_agent"  [AGENT]  — main.py', C_USER)
left_text("  INPUT_VALUE=user message,  OUTPUT_VALUE=final answer", px+22, py, F_SMALL, C_ARROW)
py += 20

trace_row('  span: "router_call"  [CHAIN]  — router.py', C_ROUTER, indent=1)
left_text("  INPUT_VALUE=messages list,  PROMPT_TEMPLATE=SYSTEM_PROMPT v0.1", px+44, py, F_SMALL, C_ARROW)
py += 20

trace_row('    span: "generate_sql_query"  [TOOL]', C_SQL, indent=2)
left_text("    TOOL_NAME, TOOL_PARAMETERS, INPUT_VALUE, OUTPUT_VALUE", px+66, py, F_SMALL, C_ARROW)
py += 20

trace_row('    span: "analyze_data"  [TOOL]', C_ANALYZE, indent=2)
left_text("    TOOL_NAME, TOOL_PARAMETERS, INPUT_VALUE, OUTPUT_VALUE", px+66, py, F_SMALL, C_ARROW)
py += 20

trace_row('  span: "router_call"  [CHAIN]  (recursive — after tools)', C_ROUTER, indent=1)
left_text("  Second call with tool results injected into messages", px+44, py, F_SMALL, C_ARROW)
py += 26

d.line([(px, py), (RX+PW-18, py)], fill=(60, 80, 110), width=1)
py += 14

center_text("Component Legend", RX+PW//2, py+8, F_HEAD, C_WHITE)
py += 26
legend = [
    (C_USER,       "Gradio UI           — ChatInterface, wraps calls in AGENT span"),
    (C_ROUTER,     "router()            — LLM call (GPT-4) + recursive tool dispatch"),
    ((40, 60, 80), "SkillMap            — registry: names → OpenAI dicts + callables"),
    (C_SQL,        "generate_sql_query  — NL→SQL, executes against SQLite traces DB"),
    (C_ANALYZE,    "analyze_data        — interprets SQL results, returns insights"),
    (C_TRACE,      "OTel spans          — AGENT / CHAIN / TOOL kinds → Phoenix"),
]
for col, label in legend:
    box((px+4, py), (18, 18), col, radius=4)
    left_text(label, px+28, py+3, F_SMALL)
    py += 26

d.line([(px, py+4), (RX+PW-18, py+4)], fill=(60, 80, 110), width=1)
py += 18

center_text("Typical Conversation Flow", RX+PW//2, py+8, F_HEAD, C_WHITE)
py += 26
steps = [
    "1. User submits query via Gradio",
    '2. main.py opens "code_based_agent" [AGENT] span',
    "3. router() called with message list + OTel context",
    '4. Opens "router_call" [CHAIN] span',
    "5. Injects system prompt if not already present",
    "6. Calls GPT-4 with SkillMap tool descriptions",
    "7. GPT-4 returns tool_calls (e.g. generate_sql_query)",
    "8. handle_tool_calls() executes each skill under a [TOOL] span",
    "9. Tool results appended to messages history",
    "10. router() recurses with updated messages",
    "11. GPT-4 returns final text (no more tool calls)",
    "12. Final answer propagated back to Gradio UI",
    "13. All spans closed; full trace sent to Phoenix",
]
for step in steps:
    left_text(step, px+6, py, F_SMALL)
    py += 20

# ══════════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════════
out = os.path.join(os.path.dirname(__file__), "code_based_agent_diagram.jpg")
img.save(out, "JPEG", quality=92)
print("saved", out)
