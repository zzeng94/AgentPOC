import asyncio
from agents import Agent, Runner

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


async def main():
    queries = [
        "Hola, ¿cómo estás?",
        "Can you provide the recent USDC transactions for wallet 0x37305b1cd40574e4c5ce33f8e8306be057fd7341?",
        "Hello, what is the weather like today?"
    ]
    for query in queries:
        result = await Runner.run(triage_agent, input=query)
        print(f"Input: {query}")
        print(f"Output: {result.final_output}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
