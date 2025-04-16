import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    # Define individual agents
    spanish_agent = Agent(
        name="Spanish agent",
        instructions="You only respond in Spanish. Your answers should be concise and entirely in Spanish.",
    )

    english_agent = Agent(
        name="English agent",
        instructions="You only respond in English. Your answers should be concise and entirely in English.",
    )

    bigquery_agent = Agent(
        name="BigQuery agent",
        instructions="You handle blockchain transaction queries. When provided a wallet address, retrieve and display recent transaction details.",
        mcp_servers=[mcp_server],
    )

    # Triage agent routes queries based on content
    triage_agent = Agent(
        name="Triage agent",
        instructions=(
            "Determine the intent of the query. If the input is in Spanish, hand off to the Spanish agent. "
            "If the input contains a wallet address or transaction-related keywords, hand off to the BigQuery agent. "
            "Otherwise, hand off to the English agent."
        ),
        handoffs=[spanish_agent, bigquery_agent, english_agent],
    )

    message = "Hola, ¿cómo estás?"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=triage_agent, input=message)
    print(result.final_output)

    message = "Can you tell me the most recent transactions for wallet 0x37305b1cd40574e4c5ce33f8e8306be057fd7341?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=triage_agent, input=message)
    print(result.final_output)

    message = "What's the secret word?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=triage_agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE Example", trace_id=trace_id):
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
            )
            await run(server)


if __name__ == "__main__":
    # Let's make sure the user has uv installed
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed. Please install it: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # We'll run the SSE server in a subprocess. Usually this would be a remote server, but for this
    # demo, we'll run it locally at http://localhost:8000/sse
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "server.py")

        print("Starting SSE server at http://localhost:8000/sse ...")

        # Run `uv run server.py` to start the SSE server
        process = subprocess.Popen(["uv", "run", server_file])
        # Give it 3 seconds to start
        time.sleep(3)

        print("SSE server started. Running example...\n\n")
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
