from pathlib import Path

from mcp.server.fastmcp import FastMCP

from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.context_spec import ContextSpec
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.rule import DEFAULT_CODE_RULE
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, is_newer

mcp = FastMCP("llm-context")


@mcp.tool()
def lc_get_files(root_path: str, paths: list[str], timestamp: float) -> str:
    """Retrieves complete contents of specified files from the project.

    DO NOT request files that have already been provided. Requires the context
    generation timestamp to check against existing file selections. Files already
    included with full content will return a message instead of duplicate content.

    Args:
        root_path: Root directory path (e.g. '/home/user/projects/myproject')
        paths: File paths relative to root_path, starting with forward slash and
               including root directory name (e.g. '/myproject/src/main.py')
        timestamp: Context generation timestamp to check against existing selections
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
        if matching_selection is None:
            raise ValueError(
                f"No context found with timestamp {timestamp}. Warn the user that the context is stale."
            )
        orig_full = set(matching_selection.full_files)
        orig_excerpted = set(matching_selection.excerpted_files)
        converter = PathConverter.create(env.config.project_root_path)
        abs_paths = converter.to_absolute(paths)
        files_to_fetch = {
            r for r, a in zip(paths, abs_paths) if r not in orig_full or is_newer(a, timestamp)
        }
        already_included = set(paths) - files_to_fetch - orig_excerpted
        in_excerpted = set(paths) & orig_excerpted
        response_parts = []
        if already_included:
            response_parts.append(
                "The latest version of the following full files are already included in the current context:\n"
                + "\n".join(already_included)
            )
        if in_excerpted:
            response_parts.append(
                "The following files are included as excerpts. Use lc-get-excluded if you need excluded sections:\n"
                + "\n".join(in_excerpted)
            )
        if files_to_fetch:
            settings = ContextSettings.create(False, False, True)
            content = ContextGenerator.create(env.config, env.state.file_selection, settings).files(
                list(files_to_fetch)
            )
            if content.strip():
                response_parts.append(content)
        return "\n\n".join(response_parts) if response_parts else "No new files to retrieve."


@mcp.tool()
def lc_list_modified_files(
    root_path: str, rule_name: str = "lc/prm-developer", timestamp: float = 0
) -> str:
    """Returns list of files modified since given timestamp.

    This is typically used to track which files have changed during the conversation.
    After getting the list, use lc-get-files to examine the contents of any modified files.

    Args:
        root_path: Root directory path (e.g. '/home/user/projects/myproject')
        rule_name: Rule to use for file inclusion rules
        timestamp: Unix timestamp to check modifications since
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        config = ContextSpec.create(env.config.project_root_path, rule_name, env.constants)
        selector = ContextSelector.create(config, timestamp)
        file_sel_full = selector.select_full_files(FileSelection.create(rule_name, [], []))
        file_sel_excerpted = selector.select_excerpted_files(file_sel_full)
        return "\n".join(file_sel_excerpted.files)


@mcp.tool()
def lc_excerpts(root_path: str, rule_name: str = "lc/prm-developer", timestamp: float = 0) -> str:
    """Returns excerpted content highlighting important sections in all supported files.

    Requires the context generation timestamp to check against existing selections.
    If excerpts are already included in the current context, returns a message instead
    of duplicate content.

    Args:
        root_path: Root directory path
        rule_name: Rule to use for file selection rules
        timestamp: Context generation timestamp to check against existing selections
    """
    env = ExecutionEnvironment.create(Path(root_path))
    cur_env = env.with_rule(rule_name)
    with cur_env.activate():
        matching_selection = cur_env.state.selections.get_selection_by_timestamp(timestamp)
        if matching_selection is None:
            raise ValueError(
                f"No context found with timestamp {timestamp}. Warn the user that the context is stale."
            )
        if matching_selection.excerpted_files:
            return "Excerpts are already included in the current context."

        selector = ContextSelector.create(cur_env.config)
        file_sel_excerpted = selector.select_excerpted_only(cur_env.state.file_selection)
        settings = ContextSettings.create(False, False, True)
        return ContextGenerator.create(
            cur_env.config, file_sel_excerpted, settings, env.tagger
        ).outlines()


@mcp.tool()
def lc_get_implementations(root_path: str, queries: list[tuple[str, str]]) -> str:
    """Retrieves complete code implementations of definitions identified in code outline excerpts.

    Provide a list of file paths and definition names to get their full implementations.
    This tool works with all supported languages except C and C++.

    Args:
        root_path: Root directory path
        queries: List of (file_path, definition_name) tuples to fetch implementations for
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        settings = ContextSettings.create(False, False, True)
        return ContextGenerator.create(
            env.config, env.state.file_selection, settings, env.tagger
        ).definitions(queries)


@mcp.tool()
def lc_create_rule_instructions(root_path: str) -> str:
    """Provides step-by-step instructions for creating custom rules.

    Call this tool when asked to create a focused rule, minimize context, or generate
    context for a specific task. Use whenever someone requests focused context,
    targeted rules, or context reduction for a particular purpose.

    Args:
        root_path: Root directory path
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        settings = ContextSettings.create(False, False, True)
        generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
        return generator.focus_help()


@mcp.tool()
def lc_get_excluded(root_path: str, paths: list[str], timestamp: float) -> str:
    """Retrieves sections that were excluded from excerpted files.

    Use this when you need the parts of files that weren't included in the excerpted content
    (e.g., styles and templates from Svelte files, prose from Markdown files).

    Args:
        root_path: Root directory path
        paths: File paths that are included as excerpts in the current context
        timestamp: Context generation timestamp to check against existing selections
    """
    # For now, return placeholder as the original implementation wasn't complete
    return "No excluded sections available yet for tree-sitter-outline processors."


def run_server():
    mcp.run(transport="stdio")
