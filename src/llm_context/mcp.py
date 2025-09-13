import asyncio
from importlib.metadata import version as pkg_ver
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from llm_context import commands
from llm_context.exec_env import ExecutionEnvironment

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
        return commands.get_files(env, paths, timestamp)


@mcp.tool()
def lc_list_modified_files(root_path: str, rule_name: str = "lc/prm-developer", timestamp: float = 0) -> str:
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
        files = commands.list_modified_files(env, rule_name, timestamp)
        return "\n".join(files)


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
    with env.activate():
        return commands.get_excerpts(env, rule_name, timestamp)


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
        return commands.get_implementations(env, queries)


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
        return commands.get_focus_help(env)


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
