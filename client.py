import asyncio, json
from typing import Optional
from contextlib import AsyncExitStack
from api_key import api_key
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI


class MCPClient:
    def __init__(self):

        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description.split('\n\n    Args:')[0].strip(),  # 去除参数部分，保留主描述
                    "parameters": {
                        "type": "object",
                        "properties": {
                            param_name: {
                                "type": param_info["type"],
                                "description": param_info.get("title", "")  # 使用 title 作为描述
                            }
                            for param_name, param_info in tool.inputSchema.get("properties", {}).items()
                        },
                        "required": tool.inputSchema.get("required", [])
                    }
                }
            }
            for tool in response.tools
        ]

        # Initial Claude API call
        response = self.anthropic.chat.completions.create(
            model="qwen3-235b-a22b",
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
            extra_body={"enable_thinking": False},  # 关闭思考模式，思考模式不支持 function calling

        )

        # Process response and handle tool calls
        final_text = []

        function_name = response.choices[0].message.tool_calls[0].function.name
        arguments_string = response.choices[0].message.tool_calls[0].function.arguments
        print(function_name, arguments_string)
        for content in response.choices:
            if content.finish_reason == 'stop':
                final_text.append(content.text)
            elif content.finish_reason == 'tool_calls':
                tool_name = content.message.tool_calls[0].function.name
                tool_args = json.loads(content.message.tool_calls[0].function.arguments)
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                      "role": "assistant",
                      "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.chat.completions.create(
                    model="qwen3-235b-a22b",
                    max_tokens=1000,
                    messages=messages,
                    extra_body={"enable_thinking": False},  # 关闭思考模式，思考模式不支持 function calling
                    stream=False
                )

                final_text.append(response.choices[0].message.content)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())