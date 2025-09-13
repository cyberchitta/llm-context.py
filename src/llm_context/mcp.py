import ast
from importlib.metadata import version as pkg_ver
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from llm_context import commands
from llm_context.exec_env import ExecutionEnvironment

mcp = FastMCP("llm-context")


@mcp.tool()
def lc_get_files(root_path: str, paths: list[str], timestamp: float) -> str:
    """Retrieves complete contents of specified files from the project.
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
def lc_list_modified_files(
    root_path: str, rule_name: str = "lc/prm-developer", timestamp: float = 0
) -> str:
    """Returns list of files modified since given timestamp.
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
    Args:
        root_path: Root directory path
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        return commands.get_focus_help(env)


@mcp.tool()
def lc_get_excluded(root_path: str, paths: list[str], timestamp: float) -> str:
    """Retrieves sections that were excluded from excerpted files.
    Args:
        root_path: Root directory path
        paths: File paths that are included as excerpts in the current context
        timestamp: Context generation timestamp to check against existing selections
    """
    # For now, return placeholder as the original implementation wasn't complete
    return "No excluded sections available yet for tree-sitter-outline processors."

@mcp.tool()
def lc_missing(root_path: str, param_type: str, data: str, timestamp: float) -> str:
    """Unified tool for retrieving missing context (files or implementations).
    Args:
        root_path: Root directory path
        param_type: Type of data - 'f' for files, 'i' for implementations  
        data: JSON string containing the data (file paths or implementation queries)
        timestamp: Context generation timestamp (required for files, ignored for implementations)
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        if param_type == "f":
            file_list = ast.literal_eval(data)
            return commands.get_files(env, file_list, timestamp)
        elif param_type == "i":
            impl_list = ast.literal_eval(data)
            return commands.get_implementations(env, impl_list)
        else:
            raise ValueError(f"Invalid parameter type: {param_type}. Use 'f' for files or 'i' for implementations.")

def run_server():
    mcp.run(transport="stdio")
