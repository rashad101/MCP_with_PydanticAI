import asyncio
import json
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from openai import AsyncOpenAI

# loading environment variables
load_dotenv(".env")


class MCPOpenAIClient:

    def __init__(self, model: str = "gpt-4o-mini"):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai_client = AsyncOpenAI()
        self.model = model
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None

    async def load_server(self):
        # defining server params
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"]
        )

        # creating stdio connection with the server
        stdio_connection = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self.stdio, self.write = stdio_connection

        # creating a session with the stdio connection
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # initialize the connectio using a session
        await self.session.initialize()

        # Optional: Checking list of available tools of a session
        # all_tools = await self.session.list_tools()
        # for tool in all_tools.tools:
        #     print(tool)
        #     print(f"{tool.name}: {tool.description}")

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        tools_list = await self.session.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in tools_list.tools
        ]

        return tools

    async def process_query(self, query: str) -> str:
        tools = await self.get_mcp_tools()

        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            tools=tools,
            tool_choice="auto"
        )

        system_response = response.choices[0].message


        # if LLM suggests tool calls then perform the tool calling
        # otherwise return the response as the final system response
        if system_response.tool_calls:
            final_messages = [
                {
                    "role": "user",
                    "content": query
                },
                system_response
            ]

            # execute the tool call
            for tool_call in system_response.tool_calls:
                tool_call_result = await self.session.call_tool(
                    tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments)
                )

                # appending tools result to the final message
                final_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_call_result.content[0].text
                })

            # final system call including the tool call results
            final_system_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=final_messages,
                tools=tools,
                tool_choice="none"
            )

            return final_system_response.choices[0].message.content

        else:
            return system_response.content

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    client = MCPOpenAIClient()
    await client.load_server()

    query = "Which sport is the king of sports ?"
    response = await client.process_query(query)

    print("System response: ", response)

    await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
