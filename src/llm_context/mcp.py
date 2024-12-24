import asyncio
from pathlib import Path

from mcp.server import Server  # type: ignore
from mcp.server.stdio import stdio_server  # type: ignore
from mcp.shared.exceptions import McpError  # type: ignore
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, TextContent, Tool  # type: ignore
from pydantic import BaseModel, Field, ValidationError  # type: ignore

from llm_context.context_generator import ContextGenerator
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector


class ContextRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    profile_name: str = Field(
        "code",
        description="Profile to use (e.g. 'code', 'copy', 'full') - defines file inclusion and presentation rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )


project_context_tool = Tool(
    name="project_context",
    description=(
        "Generates a structured repository overview including: "
        "1) Directory tree with file status (✓ full, ○ outline, ✗ excluded) "
        "2) Complete contents of key files "
        "3) Smart outlines highlighting important definitions in supported languages. "
        "The output is customizable via profiles that control file inclusion rules and presentation format. "
        "The assistant tracks previously retrieved project context in the conversation and checks this history before making new requests."
    ),
    inputSchema=ContextRequest.model_json_schema(),
)


async def project_context(arguments: dict) -> list[TextContent]:
    request = ContextRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    cur_env = env.with_profile(request.profile_name)
    with cur_env.activate():
        selector = ContextSelector.create(cur_env.config)
        file_sel_full = selector.select_full_files(cur_env.state.file_selection)
        file_sel_out = (
            selector.select_outline_files(file_sel_full)
            if selector.has_outliner(False)
            else file_sel_full
        )
        cur_env = cur_env.with_state(cur_env.state.with_selection(file_sel_out))
        cur_env.state.store()
        context = ContextGenerator.create(cur_env.config, cur_env.state.file_selection).context(
            "context-mcp"
        )
        return [TextContent(type="text", text=context)]


class FilesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    paths: list[str] = Field(
        ...,
        description="File paths relative to root_path, starting with a forward slash and including the root directory name. For example, if root_path is '/home/user/projects/myproject', then a valid path would be '/myproject/src/main.py",
    )


get_files_tool = Tool(
    name="get_files",
    description=(
        "IMPORTANT: Check previously retrieved file contents before making new requests. Retrieves (read-only) complete contents of specified files from the project. The assistant cannot modify files with this tool - it only reads their contents."
    ),
    inputSchema=FilesRequest.model_json_schema(),
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
        return [project_context_tool, get_files_tool]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        handlers = {"project_context": project_context, "get_files": get_files}
        try:
            return await handlers[name](arguments)
        except KeyError:
            raise McpError(INVALID_PARAMS, f"Unknown tool: {name}")
        except ValidationError as e:
            raise McpError(INVALID_PARAMS, str(e))
        except Exception as e:
            raise McpError(INTERNAL_ERROR, str(e))

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options(), raise_exceptions=True
        )


def run_server():
    asyncio.run(serve())
