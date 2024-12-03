import asyncio
from importlib.metadata import version as pkg_ver
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
    cur_env = env.with_profile(request.profile_name)
    with cur_env.activate():
        context = ContextGenerator.create(cur_env.config, cur_env.state.file_selection).context()
        return [TextContent(type="text", text=context)]


class FilesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    paths: list[str] = Field(
        ...,
        description="File paths relative to root_path, starting with a forward slash and including the root directory name. For example, if root_path is '/home/user/projects/myproject', then a valid path would be '/myproject/src/main.py",
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
    version = pkg_ver("llm-context")

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [
            Tool(
                name="project_context",
                description=(
                    "Generates a structured repository overview including: "
                    "1) Directory tree with file status (✓ full, ○ outline, ✗ excluded) "
                    "2) Complete contents of key files "
                    "3) Smart outlines highlighting important definitions in supported languages. "
                    "The output is customizable via profiles that control file inclusion rules and presentation format."
                ),
                inputSchema=ContextRequest.model_json_schema(),
            ),
            Tool(
                name="get_files",
                description=("Retrieves complete contents of specified files from the project."),
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
        server_version=version,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


def run_server():
    asyncio.run(serve())
