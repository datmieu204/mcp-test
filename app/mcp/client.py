import asyncio
import os
import json 
from typing import Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class SseServerParameters:
    def __init__(self, url: str):
        self.url = url

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        self.openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # async def connect_to_server(self):
    #     """
    #     Connect to the MCP server via stdio transport.
    #     """
    #     server_params = StdioServerParameters(
    #         command="python",
    #         args=["-m", "app.mcp.mcp_server"],
    #         cwd=".",
    #         env=None
    #     )

    #     stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
    #     self.stdio, self.write = stdio_transport
    #     self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

    #     await self.session.initialize()

    #     # List available tools and print them
    #     response = await self.session.list_tools()
    #     tools = response.tools
    #     print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def connect_to_server(self):
        """
        Connect to the MCP server via SSE transport.
        """
        server_params = SseServerParameters(
            url="http://127.0.0.1:8099/sse", 
        )
        
        sse_transport = await self.exit_stack.enter_async_context(sse_client(server_params.url))
        self.sse, self.write = sse_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.sse, self.write))

        await self.session.initialize()

        # List tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        if not self.session:
            raise RuntimeError("Client not connected.")

        # List tools
        response = await self.session.list_tools()
        
        available_tools = []
        for tool in response.tools:
            available_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

        messages = [{"role": "user", "content": query}]
        final_text = []

        while True:
            try:
                api_response = await self.openai.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=messages,
                    tools=available_tools,
                    tool_choice="auto", 
                )
                
                assistant_message = api_response.choices[0].message
                messages.append(assistant_message)

                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            tool_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON arguments for tool '{tool_name}'")
                            tool_args = {}

                        print(f"[Calling tool '{tool_name}' with args {tool_args}]")
                        
                        try:
                            result = await self.session.call_tool(tool_name, tool_args)
                            tool_result_content = result.content
                            print(f"Tool '{tool_name}' returned: {tool_result_content}")
                        except Exception as e:
                            tool_result_content = f"Error: {str(e)}"
                            print(f"Error during tool call: {tool_result_content}")


                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result_content
                        })

                else:
                    if assistant_message.content:
                        final_text.append(assistant_message.content)
                    break

            except Exception as e:
                print(f"API Error: {str(e)}")
                return ""

        return "".join(final_text)

    async def chat_loop(self):
        print("\nOpenAI-powered MCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError in chat loop: {str(e)}")

    async def cleanup(self):
        if self.exit_stack:
            await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())