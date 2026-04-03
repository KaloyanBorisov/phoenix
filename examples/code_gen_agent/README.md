# Code Generation Agent

## Overview

A conversational Python coding assistant built with **LangGraph**, **LangChain**, and **OpenAI GPT-4o**, with a **Gradio** web UI and end-to-end observability via **Arize Phoenix**.

The agent can generate Python code on demand, execute it in a sandboxed environment, explain existing code, and produce merge request descriptions — all within a multi-turn conversation that retains full history.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Gradio UI (app.py)                  │
│                                                         │
│  ┌──────────────────┐        ┌─────────────────────┐   │
│  │ Configuration    │        │ Chat Panel          │   │
│  │ - Phoenix API Key│        │ - Chat history      │   │
│  │ - OpenAI API Key │        │ - Message input     │   │
│  │ - Project Name   │        │ - Submit button     │   │
│  │ - Phoenix URL    │        └──────────┬──────────┘   │
│  └────────┬─────────┘                   │               │
│           │ initialize_agent()          │ chat_with_agent()
└───────────┼─────────────────────────────┼───────────────┘
            │                             │
            ▼                             ▼
┌───────────────────────────────────────────────────────────┐
│                  LangGraph Agent (agent.py)                │
│                                                           │
│   START                                                   │
│     │                                                     │
│     ▼                                                     │
│  ┌────────┐   tool_calls?   ┌─────────────────────────┐  │
│  │ agent  │ ─────────────► │        tools            │  │
│  │(GPT-4o)│ ◄───────────── │  - generate_code        │  │
│  └────────┘   ToolMessage  │  - execute_code         │  │
│     │                      │  - code_analysis        │  │
│     │ done                 │  - generate_mr_desc     │  │
│     ▼                      └─────────────────────────┘  │
│    END                                                    │
│                                                           │
│   [MemorySaver — persists messages per thread_id]         │
└───────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────┐
│              Tool LLM — GPT-4o (tools.py)                 │
│                                                           │
│  generate_code      → GPT-4o writes Python code          │
│  execute_code       → exec() with captured stdout        │
│  code_analysis      → GPT-4o explains code               │
│  generate_mr_desc   → GPT-4o writes MR description       │
└───────────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────┐
│           Arize Phoenix Observability                     │
│                                                           │
│  register() → auto-instruments LangChain + OpenAI        │
│  using_session(session_id) → groups traces per user      │
│  manual chain span → wraps each full conversation turn   │
│                                                           │
│  Trace tree per turn:                                     │
│    agent-{session_id}  [chain]                           │
│      ├── ChatOpenAI         [llm]                        │
│      ├── generate_code      [tool]                       │
│      │     └── ChatOpenAI   [llm]                        │
│      ├── execute_code       [tool]                       │
│      └── ChatOpenAI         [llm]                        │
└───────────────────────────────────────────────────────────┘
```

---

## Components

### `app.py` — Gradio UI & Entry Point
- Loads environment variables from `.env` via `python-dotenv`
- Pre-fills configuration fields from env vars (`OPENAI_API_KEY`, `PHOENIX_API_KEY`, `PHOENIX_COLLECTOR_ENDPOINT`, `PHOENIX_PROJECT_NAME`)
- `initialize_agent()` — wires up the tracer, both LLM instances, and the LangGraph agent
- `chat_with_agent()` — manages conversation state, wraps each turn in a Phoenix trace span
- Each session gets a UUID used as both LangGraph `thread_id` (memory) and Phoenix `session_id` (trace grouping)

### `agent.py` — LangGraph State Machine
- `StateGraph(MessagesState)` — state is a growing list of LangChain messages
- **`agent` node** — calls GPT-4o with all 4 tools bound (`tool_choice="auto"`)
- **`tools` node** — LangGraph `ToolNode` dispatches to the correct tool by name
- **`router`** — conditional edge: routes to `tools` if the LLM made tool calls, otherwise ends
- **`MemorySaver`** — in-memory checkpoint keyed by `thread_id`; preserves full conversation across turns

### `tools.py` — Four LangChain Tools
| Tool | Description |
|---|---|
| `generate_code` | Prompts a dedicated GPT-4o instance (temperature 0.7) to write clean, executable Python. Strips markdown fences from the response. |
| `execute_code` | Runs code with `exec()` in an isolated namespace, captures stdout. Returns output or error message. |
| `code_analysis` | Prompts GPT-4o to explain what a given code snippet does in detail. |
| `generate_merge_request_description` | Prompts GPT-4o to produce a structured markdown MR description (Title, Purpose, Implementation, Testing, Notes). |

> **Note:** Two separate GPT-4o instances are used — one as the orchestrating agent LLM, one as the tool LLM — to keep tool execution independent from the agent's reasoning.

---

## Requirements

- Python 3.10+
- OpenAI API key
- Arize Phoenix account (cloud) or local Phoenix server

---

## Installation

Recommended: use `uv` to avoid dependency conflicts.

```bash
# Install uv
pip install uv

# Run the app (installs dependencies automatically)
uv run --isolated --with-requirements requirements.txt python app.py
```

---

## Configuration

Create a `.env` file in this directory (already in `.gitignore`):

```env
OPENAI_API_KEY=sk-...
PHOENIX_API_KEY=eyJ...
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/<your-workspace>
PHOENIX_PROJECT_NAME=Copilot Agent
```

These values will be pre-filled in the UI automatically. For a local Phoenix instance, set:

```env
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
```

---

## Usage

1. Start the app:
   ```bash
   python app.py
   ```
2. Open the local or share URL printed in the terminal.
3. Click **"Set API Keys & Initialize"** in the configuration panel.
4. Start chatting. Example prompts:
   - *"Write a Python function that finds all prime numbers up to n using the Sieve of Eratosthenes"*
   - *"Generate a script that calculates Fibonacci numbers and run it"*
   - *"Analyze this code and explain what it does: `[paste code]`"*
   - *"Generate a merge request description for this code: `[paste code]`"*

---

## Files

| File | Purpose |
|---|---|
| `app.py` | Gradio UI, session management, Phoenix tracing |
| `agent.py` | LangGraph state machine, LLM setup, OpenTelemetry registration |
| `tools.py` | Four LangChain tools: generate, execute, analyze, MR description |
| `requirements.txt` | Python dependencies |
| `.env` | Local secrets (not committed) |

---

## Observability

All agent activity is traced in Phoenix:

- **Per-turn spans** named `agent-{session_id}` wrap the full conversation turn
- **Auto-instrumented spans** capture every LLM call and tool invocation inside the turn
- **Session grouping** via `using_session(session_id)` links all turns from one user together
- View traces at your Phoenix project URL (e.g. `https://app.phoenix.arize.com/s/<your-workspace>`)
