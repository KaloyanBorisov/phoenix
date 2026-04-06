# Llama Researcher

In this tutorial, we'll create LLama-Researcher using LlamaIndex workflows, inspired by [GPT-Researcher.](https://github.com/assafelovic/gpt-researcher)

Credit to [rsrohan99](https://github.com/rsrohan99) for the original implementation.

Stack Used:

- LlamaIndex workflows for orchestration
- Tavily API as the search engine api
- Arize Phoenix for tracing and evaluation

## How it works

Instead of asking the LLM one broad question directly, the workflow **decomposes → researches → compresses → synthesizes**:

```
1 LLM call → N sub-queries
                │
    ┌───────────┼───────────┐
 Tavily(q1)  Tavily(q2)  Tavily(q3)   ← parallel web searches
    │            │            │
 compress     compress     compress    ← parallel doc compression
    │            │            │
    └───────────┬───────────┘
             wait for all
                │
           1 LLM call → final report
```

### Steps

**1. Decompose** (`create_sub_queries`)
- Receives your query and asks the LLM to split it into focused sub-questions
- The LLM understands the semantic meaning of your question and generates concrete, searchable angles
- Default: 3 sub-queries

**2. Fan-out** (`deligate_sub_queries`)
- Fires each sub-query as an independent parallel event into the workflow engine
- This is where parallel execution begins

**3. Research** (`get_docs_for_subquery`)
- One instance runs per sub-query simultaneously
- Calls Tavily search — a search API built for AI agents that returns clean page content (not HTML)
- Tracks visited URLs to avoid scraping the same page twice

**4. Compress** (`compress_docs`)
- Embeds the scraped docs using an embedding model
- Keeps only chunks semantically relevant to the sub-query, trimming raw web content down
- Up to 3 run concurrently (`num_workers=3`)

**5. Fan-in** (`combine_contexts`)
- Blocks until **all** compressed results arrive (using `ctx.collect_events()`)
- Merges all findings into one combined research context

**6. Synthesize** (`write_report`)
- Sends the full combined context to the LLM to write a structured report
- Converts markdown output to PDF

## Evaluating the research quality

The workflow retrieves web chunks to answer sub-queries, but you don't know if those chunks are trustworthy. The `evaluate_traces.ipynb` notebook audits the quality of the research inputs after a run.

The workflow is the **doer**, Phoenix is the **observer**, and the notebook is the **auditor**.

It evaluates:
- **Were the chunks biased?** — do the sources have an agenda or are they objective?
- **Per sub-query** — which search angle pulled in bad sources?

If your report turns out biased, you can trace it back to exactly which sub-query fetched biased sources and which specific chunks caused it.

### How the evaluation works

**1. Connect to Phoenix** — open a client connection to your running Phoenix instance

**2. Pull the traces** — fetch all document chunks retrieved during the workflow run

**3. Set up the judge LLM** — use `gpt-4o` to evaluate each chunk with the prompt: *"Here is the original question and a document — is this document biased?"*

**4. Run the evaluation** — `llm_classify` scores each chunk as `Biased / Somewhat Biased / Somewhat Unbiased / Unbiased` with a numeric score (1.0 → 0.0)

**5. Aggregate to span level** — averages chunk scores per sub-query to get one overall bias label per search

**6. Send results back to Phoenix** — two evaluation types are logged:
- **Document level** — bias score for each individual web chunk
- **Span level** — aggregated bias score for each sub-query search

```
Span (sub-query search)        ← overall bias score
  └── chunk 1                  ← individual bias score
  └── chunk 2                  ← individual bias score
  └── chunk 3                  ← individual bias score
```

Run the notebook after a workflow run to see the bias scores sitting right next to the traces in the Phoenix UI.

## How to use

- Clone the repo

```bash
git clone https://github.com/Arize-ai/phoenix
cd examples/llamaindex-workflows-research-agent
```

- Install dependencies

```bash
pip install -r requirements.txt
```

- Create `.env` file and add `OPENAI_API_KEY`, `TAVILY_API_KEY` and `PHOENIX_API_KEY`

```bash
cp .env.example .env
```

- Run the workflow with the topic to research

```bash
 python run.py "topic to research"
```
