import asyncio
import os
import subprocess
import sys

from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.utils.workflow import draw_all_possible_flows
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from phoenix.otel import register
from workflow import ResearchAssistantWorkflow

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


async def main():
    load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))
    llm = OpenAI(model="gpt-4o-mini", timeout=300.0)
    embed_model = OpenAIEmbedding(model="text-embedding-3-small")

    endpoint = os.environ["PHOENIX_COLLECTOR_ENDPOINT"].rstrip("/") + "/v1/traces"
    tracer_provider = register(
        project_name="research_assistant",
        endpoint=endpoint,
        batch=True,
    )
    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

    workflow = ResearchAssistantWorkflow(
        llm=llm, embed_model=embed_model, verbose=True, timeout=600.0
    )
    # draw_all_possible_flows(workflow, filename="research_assistant_workflow.html")
    topic = sys.argv[1]
    report_file = await workflow.run(query=topic)
    subprocess.run(["open", report_file])


if __name__ == "__main__":
    asyncio.run(main())
