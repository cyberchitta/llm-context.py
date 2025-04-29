import asyncio
from importlib.metadata import version as pkg_ver
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData, TextContent, Tool
from pydantic import BaseModel, Field, ValidationError

from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.rule import DEFAULT_CODE_RULE


class ContextRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    rule_name: str = Field(
        DEFAULT_CODE_RULE,
        description="Rule to use (e.g. 'code', 'copy', 'full') - defines file inclusion and presentation rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )


project_context_tool = Tool(
    name="lc-project-context",
    description=(
        "⛔️ DO NOT USE this tool when you already have the project context. First check if project context is already available in the conversation before making any new requests. Use lc-get-files for retrieving specific files, and only use this tool when a broad repository overview is needed.\n\n"
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
    cur_env = env.with_rule(request.rule_name)
    with cur_env.activate():
        selector = ContextSelector.create(cur_env.config)
        file_sel_full = selector.select_full_files(cur_env.state.file_selection)
        file_sel_out = selector.select_outline_files(file_sel_full)
        cur_env = cur_env.with_state(cur_env.state.with_selection(file_sel_out))
        cur_env.state.store()
        settings = ContextSettings.create(False, False)
        context = ContextGenerator.create(
            cur_env.config, cur_env.state.file_selection, settings, env.tagger
        ).context()
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
    name="lc-get-files",
    description="⚠️ ALWAYS SEARCH THE ENTIRE CONVERSATION CONTEXT FIRST! DO NOT request files that have already been provided. IMPORTANT: Check previously retrieved file contents before making new requests. Retrieves (read-only) complete contents of specified files from the project. For this project, this is the preferred method for all file content analysis and text searches - simply retrieve the relevant files and examine their contents. The assistant cannot modify files with this tool - it only reads their contents.",
    inputSchema=FilesRequest.model_json_schema(),
)


async def get_files(arguments: dict) -> list[TextContent]:
    request = FilesRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    with env.activate():
        settings = ContextSettings.create(False, False)
        context = ContextGenerator.create(env.config, env.state.file_selection, settings).files(
            request.paths
        )
        return [TextContent(type="text", text=context)]


class ListModifiedFilesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    rule_name: str = Field(
        DEFAULT_CODE_RULE,
        description="Rule to use (e.g. 'code', 'copy', 'full') - defines file inclusion and presentation rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )
    timestamp: float = Field(..., description="Unix timestamp to check modifications since")


list_modified_files_tool = Tool(
    name="lc-list-modified-files",
    description=(
        "IMPORTANT: First get the generation timestamp from the project context. "
        "Returns a list of paths to files that have been modified since a given timestamp. "
        "This is typically used to track which files have changed during the conversation. "
        "After getting the list, use lc-get-files to examine the contents of any modified files of interest."
    ),
    inputSchema=ListModifiedFilesRequest.model_json_schema(),
)


async def list_modified_files(arguments: dict) -> list[TextContent]:
    request = ListModifiedFilesRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    cur_env = env.with_rule(request.rule_name)
    with cur_env.activate():
        selector = ContextSelector.create(cur_env.config, request.timestamp)
        file_sel_full = selector.select_full_files(cur_env.state.file_selection)
        file_sel_out = selector.select_outline_files(file_sel_full)
    return [TextContent(type="text", text="\n".join(file_sel_out.files))]


class OutlinesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    rule_name: str = Field(
        DEFAULT_CODE_RULE,
        description="Rule to use for file selection rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )


outlines_tool = Tool(
    name="lc-code-outlines",
    description=(
        "Returns smart outlines highlighting important definitions in all supported code files. "
        "This provides a high-level overview of code structure without retrieving full file contents. "
        "Outlines show key definitions (classes, functions, methods) in the codebase. "
        "Use lc-get-implementations to retrieve the full implementation of any definition shown in these outlines."
    ),
    inputSchema=OutlinesRequest.model_json_schema(),
)


async def code_outlines(arguments: dict) -> list[TextContent]:
    request = OutlinesRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    cur_env = env.with_rule(request.rule_name)
    with cur_env.activate():
        selector = ContextSelector.create(cur_env.config)
        file_sel_out = selector.select_outline_only(cur_env.state.file_selection)
        settings = ContextSettings.create(False, False)
        content = ContextGenerator.create(
            cur_env.config, file_sel_out, settings, env.tagger
        ).outlines()
        return [TextContent(type="text", text=content)]


class ImplementationsRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    queries: list[tuple[str, str]] = Field(
        ...,
        description="List of (file_path, definition_name) tuples to fetch implementations for",
    )


get_implementations_tool = Tool(
    name="lc-get-implementations",
    description="Retrieves complete code implementations of definitions identified in code outlines. Provide a list of file paths and definition names to get their full implementations. This tool works with all supported languages except C and C++.",
    inputSchema=ImplementationsRequest.model_json_schema(),
)


async def get_implementations(arguments: dict) -> list[TextContent]:
    request = ImplementationsRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    with env.activate():
        settings = ContextSettings.create(False, False)
        context = ContextGenerator.create(
            env.config, env.state.file_selection, settings, env.tagger
        ).definitions(request.queries)
        return [TextContent(type="text", text=context)]


async def serve() -> None:
    server: Server = Server("llm-context", pkg_ver("llm-context"))

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [
            project_context_tool,
            get_files_tool,
            list_modified_files_tool,
            outlines_tool,
            get_implementations_tool,
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        handlers = {
            "lc-project-context": project_context,
            "lc-get-files": get_files,
            "lc-list-modified-files": list_modified_files,
            "lc-code-outlines": code_outlines,
            "lc-get-implementations": get_implementations,
        }
        try:
            return await handlers[name](arguments)
        except KeyError:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Unknown tool: {name}"))
        except ValidationError as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=str(e)))

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options(), raise_exceptions=True
        )


def run_server():
    asyncio.run(serve())
