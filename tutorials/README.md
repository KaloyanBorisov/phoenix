# Tutorials Overview

This folder contains Phoenix tutorials organized by topic, covering the full MLOps workflow — **tracing → evaluation → experiments → prompt management** — across all major LLM frameworks.

---

## Agents (`agents/`)

Notebooks demonstrating **5 agentic design patterns** across 7 frameworks:

| Pattern | AutoGen | CrewAI | OpenAI | LangGraph | Google GenAI | SmolAgents |
|---|---|---|---|---|---|---|
| Prompt Chaining | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Routing | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Parallelization | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Orchestrator | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Evaluator-Optimizer | ✓ | — | ✓ | ✓ | ✓ | — |

Additional one-offs: **Agno** tracing, **Google ADK** financial advisor, **OpenAI** basic agent.

---

## Evals (`evals/`)

LLM evaluation tutorials covering:

- **Quickstart** and intro to evals 2.0
- **Agent evals**: tool selection, tool calling, parameter extraction
- **RAG evals**: LlamaIndex RAG evaluation
- **Code evals**: functionality and readability classification
- **Advanced**: CoT explanations, benchmark dataset + custom evaluator, Bedrock tracing + evals, optimizing LLM-as-judge prompts, session/trace-level evals, OpenAI agents cookbook

---

## Tracing (`tracing/`)

Integration-specific tracing tutorials for ~18 frameworks/providers:

LangChain, LangGraph, LlamaIndex, OpenAI, Anthropic, AutoGen, CrewAI, DSPy, Groq, Haystack, SmolAgents, Vertex AI, Google Agent Engine, Agno — plus manual instrumentation, RAG tracing, sessions, span filtering, and text2cypher evals.

---

## Experiments (`experiments/`)

Dataset and experiment management:

- **Quickstarts**: datasets & experiments, Python experiments
- **Use cases**: summarization, text-to-SQL, tool calling eval dataset, synthetic dataset generation, LlamaIndex experiments, experiments with repetitions & splits, agents cookbook

---

## Prompts (`prompts/`)

Prompt engineering techniques:

- Chain of Thought, Few Shot, ReAct prompting
- Hallucination evaluation, prompt optimization
- Phoenix prompt management (`phoenix_prompt_tutorial`)
- Import from Anthropic / OpenAI

---

## Integrations (`integrations/`)

Third-party integrations:

- **AWS Bedrock** agents tracing + evals
- **Weaviate** tracing + evals
- **Ragas** agents cookbook
- **CleanLab TLM** trace evaluation

---

## AI Evals Course (`ai_evals_course/`)

Homework solutions (HW1–HW5) for a structured AI evals course, with HW3 and HW5 having dedicated Phoenix implementations featuring judge development, evaluation pipelines, and agent trace generation.

---

## Other Categories

| Folder | Content |
|---|---|
| `annotations/` | Custom annotations tool for eval-driven development |
| `human_feedback/` | Chatbot with human feedback loop |
| `multi_modal/` | Image classification + tracing with images |
| `mcp/` | Tracing between MCP client and server |
| `quickstarts/` | Python quickstart, Agno agent for evals |
| `deployment/` | AWS CloudFormation templates for Phoenix deployment |
