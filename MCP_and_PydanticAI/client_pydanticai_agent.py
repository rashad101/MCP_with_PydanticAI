import asyncio
import os
import logfire
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logfire.instrument_openai()

server = MCPServerHTTP(
    url='http://localhost:8585/sse')
agent = Agent('gpt-4o-mini', mcp_servers=[server])


def get_prompt(query) -> str:
    return f"""Answer the user query. Fist look for the answer into the internal knowledge. If you cannot \
                             find the answer in the internal knowledge then generate the answer from your own pre-trained \
                             knowledge\n\n user query: {query}"""


async def main():
    async with agent.run_mcp_servers():
        query = "Which sport is the king of sports ?"
        result = await agent.run(get_prompt(query))

        while True:
            print(f"\nSystem Response: {result.output}")

            user_query = input("User query: ")
            if user_query == "q":
                print("Exiting the system....")
            result = await agent.run(get_prompt(user_query), message_history=result.new_messages())


if __name__ == "__main__":
    asyncio.run(main())
