import asyncio
from pathlib import Path

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, TextContent, Tool
from pydantic import BaseModel, Field

from llm_context.context_generator import ContextGenerator
from llm_context.exec_env import ExecutionEnvironment


class ContextRequest(BaseModel):
    root_path: str = Field(..., description="Project root directory path")
    profile: str = Field("code", description="Context profile")


async def get_context(arguments: dict) -> list[TextContent]:
    env = ExecutionEnvironment.create(Path(arguments["root_path"]))
    cur_env = env.with_profile(arguments.get("profile", "code"))
    with cur_env.activate():
        context = ContextGenerator.create(cur_env.config, cur_env.state.file_selection).context()
        return [TextContent(type="text", text=context)]


class FilesRequest(BaseModel):
    root_path: str = Field(..., description="Project root directory path")
    paths: list[str] = Field(
        ..., description="List of root-relative file paths (e.g. '/project_name/src/file.py')"
    )


async def get_files(arguments: dict) -> list[TextContent]:
    env = ExecutionEnvironment.create(Path(arguments["root_path"]))
    with env.activate():
        context = ContextGenerator.create(env.config, env.state.file_selection).files(
            arguments["paths"]
        )
        return [TextContent(type="text", text=context)]


async def serve() -> None:
    server = Server("llm-context")

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [
            Tool(
                name="get_context",
                description="Generate context from source code directory",
                inputSchema=ContextRequest.model_json_schema(),
            ),
            Tool(
                name="get_files",
                description="Get contents from specified root-relative files",
                inputSchema=FilesRequest.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            handlers = {"get_context": get_context, "get_files": get_files}
            if name not in handlers:
                raise McpError(INVALID_PARAMS, f"Unknown tool: {name}")
            return await handlers[name](arguments)
        except Exception as e:
            raise McpError(INVALID_PARAMS, str(e))

    options = InitializationOptions(
        server_name="llm-context",
        server_version="0.1.1",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


def run_server():
    asyncio.run(serve())
