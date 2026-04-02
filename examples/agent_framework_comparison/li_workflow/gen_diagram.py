from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1560, 1100
bg = (15, 20, 35)
img = Image.new("RGB", (W, H), bg)
d = ImageDraw.Draw(img)

# ── font helpers ──────────────────────────────────────────────────────────────
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

F_TITLE  = font(22, bold=True)
F_HEAD   = font(16, bold=True)
F_BODY   = font(13)
F_SMALL  = font(11)
F_CODE   = font(12)

# ── colours ───────────────────────────────────────────────────────────────────
C_USER    = (52, 152, 219)    # blue
C_PREP    = (46, 204, 113)    # green
C_ROUTER  = (155, 89, 182)    # purple
C_TOOL    = (230, 126, 34)    # orange
C_STOP    = (231, 76, 60)     # red
C_EVENT   = (241, 196, 15)    # yellow
C_MEM     = (52, 73, 94)      # dark slate
C_ARROW   = (189, 195, 199)
C_WHITE   = (255, 255, 255)
C_LGRAY   = (189, 195, 199)
C_DGRAY   = (44, 62, 80)

# ── helpers ───────────────────────────────────────────────────────────────────
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

def multiline(lines, x, y, fnt, fill=C_WHITE, spacing=4):
    for line in lines:
        bb = d.textbbox((0, 0), line, font=fnt)
        th = bb[3]-bb[1]
        d.text((x, y), line, font=fnt, fill=fill)
        y += th + spacing
    return y

def arrow(x1, y1, x2, y2, color=C_ARROW, width=2, head=8):
    d.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # arrowhead (pointing down / right)
    if x1 == x2:  # vertical
        d.polygon([(x2, y2), (x2-head//2, y2-head), (x2+head//2, y2-head)], fill=color)
    else:          # horizontal
        d.polygon([(x2, y2), (x2-head, y2-head//2), (x2-head, y2+head//2)], fill=color)

def curved_arrow_left(x, y_top, y_bot, color=C_ARROW, width=2, head=8, offset=30):
    """Left-side return arrow from y_bot back up to y_top."""
    x_left = x - offset
    pts = [(x, y_bot), (x_left, y_bot), (x_left, y_top), (x, y_top)]
    for i in range(len(pts)-1):
        d.line([pts[i], pts[i+1]], fill=color, width=width)
    d.polygon([(x, y_top), (x-head//2, y_top+head), (x+head//2, y_top+head)], fill=color)

# ══════════════════════════════════════════════════════════════════════════════
# Title
# ══════════════════════════════════════════════════════════════════════════════
center_text("LlamaIndex AgentFlow — Workflow Diagram", W//2, 28, font(20, bold=True), C_WHITE)

# ══════════════════════════════════════════════════════════════════════════════
# Layout: main column x=120..720, memory column x=790..1340
# ══════════════════════════════════════════════════════════════════════════════
MX, MY_START = 120, 60   # main column left, y start after title
BW = 620                  # box width main
RX = 800                  # memory panel x

# ── 1. Gradio User ────────────────────────────────────────────────────────────
y = 55
box((MX, y), (BW, 60), C_USER, outline=(100,180,240), outline_w=2)
center_text("Gradio UI", MX + BW//2, y+18, F_HEAD)
center_text('user types message → workflow.run(input=message)', MX + BW//2, y+42, F_BODY)

arrow(MX + BW//2, y+60, MX + BW//2, y+85, width=2)

# event label
ev_y = y + 68
box((MX+BW//2 - 130, ev_y), (260, 22), C_EVENT, radius=5)
center_text("StartEvent(input='user message')", MX+BW//2, ev_y+11, F_SMALL, (20,20,20))

# ── 2. prepare_agent ──────────────────────────────────────────────────────────
y2 = y + 90
box((MX, y2), (BW, 120), C_PREP, outline=(80,210,130), outline_w=2)
center_text("Step: prepare_agent", MX + BW//2, y2+16, F_HEAD)
lines = [
    "  Input:  StartEvent(input='user message string')",
    "  Action: wrap in ChatMessage(role='user')",
    "          put in ChatMemoryBuffer",
    "          retrieve full history → list[ChatMessage]",
    "  Output: RouterInputEvent(input=[ChatMessage(role='user', ...)])",
]
multiline(lines, MX+10, y2+32, F_SMALL, spacing=3)

arrow(MX + BW//2, y2+120, MX + BW//2, y2+145, width=2)

ev2_y = y2 + 128
box((MX+BW//2 - 175, ev2_y), (350, 22), C_EVENT, radius=5)
center_text("RouterInputEvent(input=[list of ChatMessages])", MX+BW//2, ev2_y+11, F_SMALL, (20,20,20))

# ── 3. router ─────────────────────────────────────────────────────────────────
y3 = y2 + 150
box((MX, y3), (BW, 125), C_ROUTER, outline=(180,120,210), outline_w=2)
center_text("Step: router", MX + BW//2, y3+16, F_HEAD)
lines3 = [
    "  Input:  RouterInputEvent(input=[list of ChatMessages])",
    "  Action: inject system prompt if missing",
    "          llm.achat_with_tools(messages, tools=[sql_tool, calc_tool])",
    "          put LLM response in ChatMemoryBuffer",
    "  Branch: tool calls present? → ToolCallEvent",
    "          no tool calls?       → StopEvent (final answer)",
]
multiline(lines3, MX+10, y3+32, F_SMALL, spacing=3)

# two output arrows
cx = MX + BW//2
# left branch — tool call
arrow(cx - 120, y3+125, cx - 120, y3+152, width=2)
ev3l_y = y3 + 135
box((MX, ev3l_y), (240, 22), C_EVENT, radius=5)
center_text("ToolCallEvent(tool_calls=[...])", MX+120, ev3l_y+11, F_SMALL, (20,20,20))

# right branch — stop
arrow(cx + 120, y3+125, cx + 120, y3+152, width=2)
ev3r_y = y3 + 135
box((MX + BW - 240, ev3r_y), (240, 22), C_EVENT, radius=5)
center_text("StopEvent(result='final answer')", MX + BW - 120, ev3r_y+11, F_SMALL, (20,20,20))

# ── 4. tool_call_handler ──────────────────────────────────────────────────────
y4 = y3 + 158
box((MX, y4), (BW, 115), C_TOOL, outline=(240,160,60), outline_w=2)
center_text("Step: tool_call_handler", MX + BW//2, y4+16, F_HEAD)
lines4 = [
    "  Input:  ToolCallEvent(tool_calls=[ToolSelection(...)])",
    "  Action: for each ToolSelection:",
    "            look up callable in SkillMap by tool_name",
    "            execute tool(**tool_kwargs)",
    "            wrap result as ChatMessage(role='tool')",
    "            append to ChatMemoryBuffer",
    "  Output: RouterInputEvent(input=full memory) → loops back",
]
multiline(lines4, MX+10, y4+32, F_SMALL, spacing=2)

# loop-back arrow on left side
loop_x = MX - 10
arrow(loop_x, y4+57, loop_x, y3+62, width=2, color=(241,196,15))
# horizontal connectors
d.line([(MX, y4+57), (loop_x, y4+57)], fill=(241,196,15), width=2)
d.line([(loop_x, y3+62), (MX, y3+62)], fill=(241,196,15), width=2)
# label
center_text("RouterInputEvent", loop_x - 58, (y4+57 + y3+62)//2, F_SMALL, (241,196,15))

# ── 5. StopEvent / end ────────────────────────────────────────────────────────
y5 = y4 + 118
# right branch continues down to workflow end
stop_x = cx + 120
arrow(stop_x, y3 + 157, stop_x, y5, width=2, color=C_STOP)
box((MX + BW//2, y5), (BW//2 - 10, 52), C_STOP, outline=(240,100,80), outline_w=2)
center_text("Workflow ends", MX + BW//2 + (BW//2-10)//2, y5+16, F_HEAD)
center_text("return StopEvent.result to Gradio", MX + BW//2 + (BW//2-10)//2, y5+36, F_BODY)

# ══════════════════════════════════════════════════════════════════════════════
# Memory State Panel (right side)
# ══════════════════════════════════════════════════════════════════════════════
mem_panel_y = 55
mem_panel_h = H - 80
box((RX, mem_panel_y), (W - RX - 30, mem_panel_h), C_MEM, radius=12,
    outline=(80,100,120), outline_w=2)

center_text("ChatMemoryBuffer — state over time", RX + (W-RX-30)//2, mem_panel_y+18, F_HEAD)

mx = RX + 14
my = mem_panel_y + 38

def mem_state(title, entries, y_start, title_color=(241,196,15)):
    box((mx, y_start), (W-RX-58, 18), (30,40,60), radius=4)
    center_text(title, mx + (W-RX-58)//2, y_start+9, F_SMALL, title_color)
    yy = y_start + 22
    for role, txt, col in entries:
        box((mx+4, yy), (W-RX-66, 18), col, radius=3)
        left_text(f"  {role}: {txt}", mx+6, yy+3, F_SMALL, C_WHITE)
        yy += 22
    return yy + 6

my = mem_state("Initial — after prepare_agent",
    [("user", '"What is 2+3?"', (52,73,140))], my)

my = mem_state("Loop 1 — after router (tool call chosen)",
    [("user",      '"What is 2+3?"',             (52,73,140)),
     ("assistant", 'tool_call: calculator(a=2, b=3)', (100,60,140))], my)

my = mem_state("Loop 1 — after tool_call_handler",
    [("user",      '"What is 2+3?"',             (52,73,140)),
     ("assistant", 'tool_call: calculator(a=2, b=3)', (100,60,140)),
     ("tool",      'result: 5',                  (120,80,30))], my)

my = mem_state("Loop 2 — after router (final answer)",
    [("user",      '"What is 2+3?"',             (52,73,140)),
     ("assistant", 'tool_call: calculator(a=2, b=3)', (100,60,140)),
     ("tool",      'result: 5',                  (120,80,30)),
     ("assistant", '"The answer is 5."',         (80,100,30))], my)

# legend divider
d.line([(mx, my+4), (W-46, my+4)], fill=(80,100,120), width=1)
my += 14

# Event colour legend
center_text("Event Legend", RX + (W-RX-30)//2, my+8, F_HEAD)
my += 22
legend = [
    (C_USER,   "Gradio UI / workflow entry"),
    (C_PREP,   "prepare_agent step"),
    (C_ROUTER, "router step"),
    (C_TOOL,   "tool_call_handler step"),
    (C_STOP,   "StopEvent / workflow end"),
    (C_EVENT,  "Event labels / loop arrow"),
]
for col, label in legend:
    box((mx+4, my), (16, 16), col, radius=3)
    left_text(label, mx+26, my+2, F_SMALL)
    my += 22

# ══════════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════════
out = "/home/kaloyan/phoenix/examples/agent_framework_comparison/li_workflow/agentflow_diagram.png"
img.save(out, "PNG")
print("saved", out)
