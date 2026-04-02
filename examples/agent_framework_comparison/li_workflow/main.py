import os
import sys
import logging
import asyncio
import gradio as gr
from llama_index.llms.openai import OpenAI
sys.path.insert(1, os.path.join(sys.path[0], ".."))
from router import AgentFlow
from utils.instrument import Framework, instrument
from opentelemetry import context
from opentelemetry.context import Context
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

@asynccontextmanager
async def managed_otel_context():
    # Store the token at a higher scope
    token = None
    try:
        # Create a new context
        ctx = Context()
        # Get the current context token
        token = context.attach(ctx)
        yield
    finally:
        # Safely detach the context
        if token is not None:
            try:
                context.detach(token)
            except ValueError as e:
                # Log the error but don't raise it
                logging.debug(f"Context detachment warning: {e}")

async def gradio_interface(message, history):
    try:
        async with managed_otel_context():
            llm = OpenAI(model="gpt-4")
            workflow = AgentFlow(llm=llm)
            response = await workflow.run(input=message)
            return response
    except Exception as e:
        logging.error(f"Error in gradio_interface: {e}")
        raise

def launch_app():
    iface = gr.ChatInterface(fn=gradio_interface, title="LlamaIndex Workflow Agent")
    iface.launch()

if __name__ == "__main__":
    instrument(project_name="li-workflow", framework=Framework.LLAMA_INDEX)
    asyncio.run(launch_app())
