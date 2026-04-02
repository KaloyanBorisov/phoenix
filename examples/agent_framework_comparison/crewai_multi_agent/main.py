import os
import sys
import logging
import asyncio

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import gradio as gr
from dotenv import load_dotenv
from router import run_crewai
from utils.instrument import Framework, instrument

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def gradio_interface(message, _):
    return run_crewai(message)


def launch_app():
    
    # Create new event loop
    loop = asyncio.new_event_loop()
    # Set it as the current event loop for this thread
    asyncio.set_event_loop(loop)

    iface = gr.ChatInterface(fn=gradio_interface, title="CrewAI Multi-Agent")
    iface.launch()


if __name__ == "__main__":
    instrument(project_name="crewai-multi-agent", framework=Framework.CREWAI)
    launch_app()
