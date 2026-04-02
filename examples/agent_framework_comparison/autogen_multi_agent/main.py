import os
import sys
import logging
import asyncio

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import gradio as gr
from dotenv import load_dotenv
from openinference.semconv.trace import SpanAttributes
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from router import run_autogen_agents
from utils.instrument import Framework, instrument

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



def gradio_interface(message, _):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("autogen") as span:
        span.set_attribute(SpanAttributes.INPUT_VALUE, message)
        span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, "AGENT")

        context = {}
        TraceContextTextMapPropagator().inject(context)
        agent_response = run_autogen_agents(message, context)

        span.set_attribute(SpanAttributes.OUTPUT_VALUE, agent_response)
        span.set_status(trace.Status(trace.StatusCode.OK))
        return agent_response


def launch_app():

    # Create new event loop
    loop = asyncio.new_event_loop()
    # Set it as the current event loop for this thread
    asyncio.set_event_loop(loop)

    iface = gr.ChatInterface(fn=gradio_interface, title="AutoGen Copilot Multi-Agent")
    iface.launch()


if __name__ == "__main__":
    instrument(project_name="autogen-multi-agent", framework=Framework.AUTOGEN)
    launch_app()
