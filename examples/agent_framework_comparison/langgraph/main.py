import os
import sys
import asyncio
import logging
import gradio as gr
sys.path.insert(1, os.path.join(sys.path[0], ".."))
from dotenv import load_dotenv
from langgraph.router import run_agent
from utils.instrument import Framework, instrument

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



def gradio_interface(message, history):
    return run_agent(message)


def launch_app():
    """
    Launches the LangGraph Copilot Agent application.

    This function creates a new asyncio event loop, sets it as the current event loop for the thread,
    and then launches the Gradio ChatInterface with the specified function and title.
    """
     # Create new event loop
    loop = asyncio.new_event_loop()
    # Set it as the current event loop for this thread
    asyncio.set_event_loop(loop)

    iface = gr.ChatInterface(fn=gradio_interface, title="LangGraph Copilot Agent")
    iface.launch()


if __name__ == "__main__":
    instrument(project_name="langgraph-agent-demo", framework=Framework.LANGGRAPH)
    launch_app()
