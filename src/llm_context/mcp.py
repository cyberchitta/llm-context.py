import asyncio
from importlib.metadata import version as pkg_ver
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData, TextContent, Tool
from pydantic import ValidationError

from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.context_spec import ContextSpec
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.mcp_tools import (
    ContextRequest,
    FilesRequest,
    FocusHelpRequest,
    ImplementationsRequest,
    ListModifiedFilesRequest,
    OutlinesRequest,
    get_tool_definitions,
)
from llm_context.rule import DEFAULT_CODE_RULE
from llm_context.rule_parser import RuleLoader
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, is_newer

TOOL_DEFINITIONS = get_tool_definitions()
TOOLS = [
    Tool(name=tool_def["name"], description=tool_def["description"], inputSchema=tool_def["schema"])
    for tool_def in TOOL_DEFINITIONS
]


async def project_context(arguments: dict) -> list[TextContent]:
    request = ContextRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    cur_env = env.with_rule(request.rule_name)
    with cur_env.activate():
        selector = ContextSelector.create(cur_env.config)
        file_sel_full = selector.select_full_files(cur_env.state.file_selection)
        file_sel_out = selector.select_outline_files(file_sel_full)
        settings = ContextSettings.create(False, False, True)
        generator = ContextGenerator.create(cur_env.config, file_sel_out, settings, env.tagger)
        context, context_timestamp = generator.context()
        updated_selection = file_sel_out.with_timestamp(context_timestamp)
        updated_env = cur_env.with_state(cur_env.state.with_selection(updated_selection))
        updated_env.state.store()
        return [TextContent(type="text", text=context)]


async def get_files(arguments: dict) -> list[TextContent]:
    request = FilesRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    with env.activate():
        matching_selection = env.state.selections.get_selection_by_timestamp(request.timestamp)
        if matching_selection is None:
            message = f"No context found with timestamp {request.timestamp}. Warn the user that the context is stale."
            raise McpError(ErrorData(code=INVALID_PARAMS, message=message))
        orig = set(matching_selection.full_files)
        converter = PathConverter.create(env.config.project_root_path)
        paths = list(zip(request.paths, converter.to_absolute(request.paths)))
        files_to_fetch = {r for r, a in paths if r not in orig or is_newer(a, request.timestamp)}
        already_included = set(request.paths) - files_to_fetch
        response_parts = []
        if already_included:
            response_parts.append(
                "The following full files are already included in the current context:\n"
                + "\n".join(already_included)
            )
        if files_to_fetch:
            settings = ContextSettings.create(False, False, True)
            content = ContextGenerator.create(env.config, env.state.file_selection, settings).files(
                files_to_fetch
            )
            if content.strip():
                response_parts.append(content)
        final_response = (
            "\n\n".join(response_parts) if response_parts else "No new files to retrieve."
        )
        return [TextContent(type="text", text=final_response)]


async def list_modified_files(arguments: dict) -> list[TextContent]:
    request = ListModifiedFilesRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    with env.activate():
        config = ContextSpec.create(env.config.project_root_path, request.rule_name, env.constants)
        selector = ContextSelector.create(config, request.timestamp)
        file_sel_full = selector.select_full_files(FileSelection.create(request.rule_name, [], []))
        file_sel_out = selector.select_outline_files(file_sel_full)
    return [TextContent(type="text", text="\n".join(file_sel_out.files))]


async def code_outlines(arguments: dict) -> list[TextContent]:
    request = OutlinesRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    cur_env = env.with_rule(request.rule_name)
    with cur_env.activate():
        matching_selection = cur_env.state.selections.get_selection_by_timestamp(request.timestamp)
        if matching_selection is None:
            message = f"No context found with timestamp {request.timestamp}. Warn the user that the context is stale."
            raise McpError(ErrorData(code=INVALID_PARAMS, message=message))
        if matching_selection.outline_files:
            message = "Code outlines are already included in the current context."
            return [TextContent(type="text", text=message)]
        selector = ContextSelector.create(cur_env.config)
        file_sel_out = selector.select_outline_only(cur_env.state.file_selection)
        settings = ContextSettings.create(False, False, True)
        content = ContextGenerator.create(
            cur_env.config, file_sel_out, settings, env.tagger
        ).outlines()
        return [TextContent(type="text", text=content)]


async def get_implementations(arguments: dict) -> list[TextContent]:
    request = ImplementationsRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    with env.activate():
        settings = ContextSettings.create(False, False, True)
        context = ContextGenerator.create(
            env.config, env.state.file_selection, settings, env.tagger
        ).definitions(request.queries)
        return [TextContent(type="text", text=context)]


async def get_focus_help(arguments: dict) -> list[TextContent]:
    request = FocusHelpRequest(**arguments)
    env = ExecutionEnvironment.create(Path(request.root_path))
    with env.activate():
        settings = ContextSettings.create(False, False, True)
        generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
        content = generator.focus_help()
        return [TextContent(type="text", text=content)]


async def serve() -> None:
    server: Server = Server("llm-context", pkg_ver("llm-context"))

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return TOOLS

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        handlers = {
            "lc-project-context": project_context,
            "lc-get-files": get_files,
            "lc-list-modified-files": list_modified_files,
            "lc-code-outlines": code_outlines,
            "lc-get-implementations": get_implementations,
            "lc-create-rule-instructions": get_focus_help,
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
