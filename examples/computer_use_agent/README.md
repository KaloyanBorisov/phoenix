# Computer Use Agent

## Overview

A conversational agent that can **control a computer** — executing Bash commands, editing files, taking screenshots, and interacting with GUI applications — built with **LangGraph** and **Anthropic's Computer Use beta API**, with a **Gradio** web UI and end-to-end observability via **Arize Phoenix**.

The agent runs inside a **Docker container with a full Ubuntu desktop** (X11 + noVNC). Every action the agent takes is visible in real time through a browser-based VNC viewer, and every LLM call and tool invocation is traced in Phoenix.

> **⚠️ Safety:** Because the agent can execute arbitrary system-level commands, always run it inside the provided Docker VM — never directly on your host machine.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Docker Container                          │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                  Gradio UI  (app.py)                      │   │
│  │                                                           │   │
│  │  ┌─────────────────────┐   ┌───────────────────────────┐ │   │
│  │  │  Configuration Panel│   │      Chat Panel           │ │   │
│  │  │  - Phoenix API Key  │   │  - Chat history display   │ │   │
│  │  │  - Anthropic API Key│   │  - Message input          │ │   │
│  │  │  - Project Name     │   │  - Submit button          │ │   │
│  │  │  - Phoenix URL      │   └────────────┬──────────────┘ │   │
│  │  └──────────┬──────────┘                │                 │   │
│  │             │ initialize_agent()         │ chat_with_agent()  │
│  └─────────────┼──────────────────────────-┼─────────────────┘  │
│                │                            │                    │
│                ▼                            ▼                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LangGraph Agent  (agent.py)                  │   │
│  │                                                          │   │
│  │   START                                                  │   │
│  │     │                                                    │   │
│  │     ▼                                                    │   │
│  │  ┌─────────────────────┐   tool_calls?                  │   │
│  │  │      agent node     │ ──────────────────────────┐    │   │
│  │  │  claude-opus-4-0    │ ◄─────────────────────────┤    │   │
│  │  │  (beta: computer-   │   ToolResult              │    │   │
│  │  │   use-2025-01-24,   │                           ▼    │   │
│  │  │   prompt-caching)   │              ┌────────────────┐│   │
│  │  └─────────────────────┘              │   tools node   ││   │
│  │     │                                 │                ││   │
│  │     │ no tool_calls / role=assistant  │  ┌──────────┐  ││   │
│  │     ▼                                 │  │ Computer │  ││   │
│  │    END                                │  │  Tool    │  ││   │
│  │                                       │  └──────────┘  ││   │
│  │  [MemorySaver — persists messages     │  ┌──────────┐  ││   │
│  │   per thread_id / session_id]         │  │  Bash    │  ││   │
│  │                                       │  │  Tool    │  ││   │
│  │                                       │  └──────────┘  ││   │
│  │                                       │  ┌──────────┐  ││   │
│  │                                       │  │  Edit    │  ││   │
│  │                                       │  │  Tool    │  ││   │
│  │                                       │  └──────────┘  ││   │
│  │                                       └────────────────┘│   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               Ubuntu Desktop Environment                   │  │
│  │  Xvfb (virtual display) + Mutter (WM) + tint2 (taskbar)   │  │
│  │  Firefox · gedit · Terminal                                │  │
│  │  noVNC → accessible at http://localhost:8080               │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                  Arize Phoenix Observability                     │
│                                                                  │
│  register() + AnthropicBetaInstrumentor → auto-instruments       │
│  all Anthropic beta API calls (LLM + tool results)               │
│                                                                  │
│  using_session(session_id) → groups traces per user session      │
│  manual agent span → wraps each full conversation turn           │
│                                                                  │
│  Trace tree per turn:                                            │
│    agent-{session_id}  [agent]                                   │
│      ├── claude-opus-4-0          [llm]                          │
│      ├── computer_tool            [tool]  (screenshot / click)   │
│      ├── bash_tool                [tool]  (shell command)        │
│      └── claude-opus-4-0          [llm]  (follow-up reasoning)   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Components

### `app.py` — Gradio UI & Entry Point
- Loads environment variables from `.env` via `python-dotenv`
- Pre-fills configuration fields from env vars (`ANTHROPIC_API_KEY`, `PHOENIX_API_KEY`, `PHOENIX_COLLECTOR_ENDPOINT`, `PHOENIX_PROJECT_NAME`)
- **Two-column layout**: narrow configuration panel (left) + full-width chat panel (right)
- `initialize_agent()` — registers the Phoenix tracer, initializes the Anthropic client and tool collection, compiles the LangGraph agent
- `chat_with_agent()` — appends the user message to conversation history, invokes the agent asynchronously, wraps each turn in a Phoenix `agent` span, returns the assistant reply
- Each session gets a UUID used as both LangGraph `thread_id` (memory persistence) and Phoenix `session_id` (trace grouping)

### `agent.py` — LangGraph State Machine
- `StateGraph(ComputerUseState)` — state carries the full message list, tool results, iteration counters, and a completion flag
- **`agent` node** — calls `claude-opus-4-0` via the Anthropic beta API with two beta flags: `computer-use-2025-01-24` (computer use tools) and `prompt-caching-2024-07-31` (cost reduction via caching)
- **`tools` node** — iterates over tool-use blocks in the last assistant message, dispatches each to `ToolCollection.run()`, and packages results as `BetaToolResultBlockParam`
- **`router`** — conditional edge: routes back to `agent` if any tool was called, routes to `END` if the last message is a plain assistant reply
- **`MemorySaver`** — in-memory checkpoint keyed by `thread_id`; preserves the full conversation across multiple `ainvoke` calls

### `tools/` — Three Anthropic Computer Use Tools

| Tool | Class | Description |
|---|---|---|
| `computer` | `ComputerTool` | Takes screenshots, moves the mouse, clicks, types, scrolls, and presses keys via the `computer_use` beta tool spec. Uses `DISPLAY`, `WIDTH`, `HEIGHT` env vars to target the virtual X11 display. |
| `bash` | `BashTool` | Runs arbitrary shell commands in a persistent bash session inside the container. Supports long-running processes and environment variable persistence across calls. |
| `str_replace_editor` | `EditTool` | Views, creates, and edits files using `view`, `create`, `str_replace`, `insert`, and `undo_edit` commands — equivalent to a code editor operated programmatically. |

### `instrumentor.py` — Custom Anthropic Beta Instrumentation
- `AnthropicBetaInstrumentor` wraps the Anthropic beta messages API with OpenInference-compatible spans
- Records input messages, model parameters, and raw response content as span attributes
- Works alongside Phoenix's `register()` auto-instrumentation to produce a complete trace tree

### `utils.py` — Prompt & Message Utilities
- `SYSTEM_PROMPT` — detailed system capabilities block: informs the model it is running on Ubuntu with internet access, how to launch GUI apps, how to handle large outputs, and the current date
- `make_api_tool_result()` — converts a `ToolResult` (text output or base64 screenshot) into a `BetaToolResultBlockParam` for the next LLM call
- `response_to_params()` — converts a raw `BetaMessage` into a list of `BetaTextBlockParam` / `BetaToolUseBlockParam` for appending to the message history
- `inject_prompt_caching()` — sets `cache_control: ephemeral` breakpoints on the 3 most recent user turns to maximise prompt cache hits
- `maybe_filter_to_n_most_recent_images()` — removes old screenshot images from the message history in chunks to stay within context limits while preserving cache locality

---

## Requirements

- Docker
- Anthropic API key
- Arize Phoenix account (cloud) or local Phoenix server

---

## Installation

No manual dependency installation needed — everything is bundled in the Docker image.

```bash
# Build the image
docker build -t computer-use-agent .

# Run/Recreate the container
docker run -d --name computer-use-agent -p 5900:5900 -p 6080:6080 -p 7860:7860 -p 8080:8080 computer-use-agent:latest
```

| Port | Service |
|---|---|
| `7860` | Gradio chat UI |
| `8080` | noVNC desktop viewer (browser) |
| `6080` | noVNC WebSocket proxy |
| `5900` | Raw VNC (optional, for VNC clients) |

---

## Configuration

Create a `.env` file in this directory (already in `.gitignore`):

```env
ANTHROPIC_API_KEY=sk-ant-...
PHOENIX_API_KEY=eyJ...
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/<your-workspace>
PHOENIX_PROJECT_NAME=Computer Use Agent
```

These values will be pre-filled in the UI automatically. For a local Phoenix instance:

```env
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
```

---

## Usage

1. Start the container (see Installation above).
2. Open **[http://localhost:7860](http://localhost:7860)** for the chat UI.
3. Open **[http://localhost:8080](http://localhost:8080)** to watch the agent control the desktop in real time.
4. In the chat UI, fill in your API keys and click **"Set API Keys & Initialize"**.
5. Start chatting. The agent will use the Ubuntu desktop to carry out your request.

### Example Prompts

```
Open a terminal and show me the current disk usage.
```
```
Open Firefox and search for the Python documentation for the `asyncio` module.
```
```
Write a Python script to count word frequencies in a text file, save it to ~/word_count.py, and run it on /etc/os-release.
```
```
Take a screenshot of the desktop and describe what you see.
```
```
Open gedit, write a short poem, and save it to ~/poem.txt.
```

---

## Files

| File | Purpose |
|---|---|
| `app.py` | Gradio UI, session management, Phoenix tracing |
| `agent.py` | LangGraph state machine, Anthropic client, tool collection wiring |
| `instrumentor.py` | Custom OpenInference instrumentation for Anthropic beta API |
| `utils.py` | System prompt, message/tool-result conversion, prompt caching, image pruning |
| `tools/computer.py` | Screenshot, mouse, keyboard computer-use tool |
| `tools/bash.py` | Persistent bash shell tool |
| `tools/edit.py` | File view/create/edit tool |
| `tools/collection.py` | `ToolCollection` — dispatch layer for all tools |
| `tools/base.py` | `BaseAnthropicTool`, `ToolResult`, `ToolError` base classes |
| `requirements.txt` | Python dependencies (pre-installed in Docker image) |
| `Dockerfile` | Ubuntu desktop + noVNC + Python environment |
| `image/` | Startup scripts for Xvfb, Mutter, tint2, noVNC, and the HTTP server |
| `.env` | Local secrets (not committed) |

---

## Observability

All agent activity is traced in Phoenix:

- **Per-turn spans** named `agent-{session_id}` wrap the full conversation turn with input/output recorded
- **Auto-instrumented spans** capture every Anthropic LLM call and tool invocation inside the turn
- **Session grouping** via `using_session(session_id)` links all turns from one user together
- **Screenshot tool results** (base64 PNG) are included in tool-result spans so you can see exactly what the agent saw

View traces at your Phoenix project URL (e.g. `https://app.phoenix.arize.com/s/<your-workspace>`).
