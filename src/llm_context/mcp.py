import asyncio
from pathlib import Path

from mcp.server import NotificationOptions, Server  # type: ignore
from mcp.server.models import InitializationOptions  # type: ignore
from mcp.server.stdio import stdio_server  # type: ignore
from mcp.shared.exceptions import McpError  # type: ignore
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, TextContent, Tool  # type: ignore
from pydantic import BaseModel, Field, ValidationError  # type: ignore

from llm_context.context_generator import ContextGenerator
from llm_context.exec_env import ExecutionEnvironment


class ContextRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    profile_name: str = Field(
        "code",
        description="Profile to use (e.g. 'code', 'copy', 'full') - defines file inclusion and presentation rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )


async def get_context(arguments: dict) -> list[TextContent]:
    request = ContextRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    cur_env = env.with_profile(request.profile)
    with cur_env.activate():
        context = ContextGenerator.create(cur_env.config, cur_env.state.file_selection).context()
        return [TextContent(type="text", text=context)]


class FilesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    paths: list[str] = Field(
        ...,
        description="File paths relative to root (e.g. ['/myproject/src/main.py'])",
        min_items=1,
    )


async def get_files(arguments: dict) -> list[TextContent]:
    request = FilesRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    with env.activate():
        context = ContextGenerator.create(env.config, env.state.file_selection).files(request.paths)
        return [TextContent(type="text", text=context)]


async def serve() -> None:
    server = Server("llm-context")

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [
            Tool(
                name="project_context",
                description=(
                    "Generates a detailed overview of a (usually source code) project, including folder structure, "
                    "complete contents of some files, and outlines of others. "
                    "The profile determines which files are present in full, in outline or excluded entirely."
                ),
                inputSchema=ContextRequest.model_json_schema(),
            ),
            Tool(
                name="get_files",
                description=(
                    "Retrieves complete contents of specified files from the project. Files must be "
                    "specified using root-relative paths (e.g. '/project_name/src/file.py')."
                ),
                inputSchema=FilesRequest.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        handlers = {"project_context": get_context, "get_files": get_files}
        try:
            return await handlers[name](arguments)
        except KeyError:
            raise McpError(INVALID_PARAMS, f"Unknown tool: {name}")
        except ValidationError as e:
            raise McpError(INVALID_PARAMS, str(e))
        except Exception as e:
            raise McpError(INTERNAL_ERROR, str(e))

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
