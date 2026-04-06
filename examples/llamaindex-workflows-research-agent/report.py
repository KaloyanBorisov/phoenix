from datetime import datetime, timezone

from llama_index.core.llms.llm import LLM
from llama_index.core.prompts.base import PromptTemplate


async def generate_report_from_context(query: str, context: str, llm: LLM) -> str:
    prompt = PromptTemplate(
        """Information:
--------------------------------
{context}
--------------------------------
Using the above information, answer the following query or task: "{question}" in a detailed
report -- The report should focus on the answer to the query, should be well structured,
informative, in-depth, and comprehensive, with facts and numbers if available and at least
{total_words} words. You should strive to write the report as long as you can using all relevant
and necessary information provided.

Please follow all of the following guidelines in your report:
- You MUST determine your own concrete and valid opinion based on the given information. Do NOT
defer to general and meaningless conclusions.
- You MUST write the report with markdown syntax and {report_format} format.
- You MUST prioritize the relevance, reliability, and significance of the sources you use. Choose
trusted sources over less reliable ones.
- You must also prioritize new articles over older articles if the source can be trusted.
- Use in-text citation references in {report_format} format and make it with markdown hyperlink
placed at the end of the sentence or paragraph that references them like this:
([in-text citation](url)).
- Don't forget to add a reference list at the end of the report in {report_format} format and full
url links without hyperlinks.
- You MUST write all used source urls at the end of the report as references, and make sure to not
add duplicated sources, but only one reference for each. Every url should be hyperlinked:
[url website](url)
Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the
report:

eg: Author, A. A. (Year, Month Date). Title of web page. Website Name. [url website](url)

Please do your best, this is very important to my career.
Assume that the current date is {date_today}.
"""
    )
    formatted_prompt = prompt.format(
        context=context,
        question=query,
        total_words=1000,
        report_format="APA",
        date_today=datetime.now(timezone.utc).strftime("%B %d, %Y"),
    )

    print("\n> Skipping LLM call. Prompt that would be sent:\n")
    print(formatted_prompt)

    return f"""# Research Report: {query}

> **Note:** The final LLM analysis step was skipped during this run to avoid long API wait times.
> In a full run, this prompt would be sent to the LLM which would synthesize all the research
> findings below into a structured report with citations and conclusions.

---

## What was skipped

The workflow successfully completed all research steps:
1. Decomposed the query into sub-questions
2. Searched the web via Tavily for each sub-question
3. Compressed and ranked the most relevant content
4. Combined all findings into a single research context

The missing step is the final LLM call that would read all the context below and write
a coherent, cited, in-depth report of at least 1000 words in APA format.

---

## Prompt that would be sent to the LLM

```
{formatted_prompt}
```
"""
