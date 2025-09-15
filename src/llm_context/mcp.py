import ast
from importlib.metadata import version as pkg_ver
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from llm_context import commands
from llm_context.exec_env import ExecutionEnvironment

mcp = FastMCP("llm-context")


@mcp.tool()
def lc_changed(root_path: str, rule_name: str = "lc/prm-developer", timestamp: float = 0) -> str:
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
def lc_outlines(root_path: str) -> str:
    """Returns excerpted content highlighting important sections in all supported files.
    Args:
        root_path: Root directory path
        rule_name: Rule to use for file selection rules
        timestamp: Context generation timestamp to check against existing selections
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        return commands.get_outlines(env)


@mcp.tool()
def lc_rule_instructions(root_path: str) -> str:
    """Provides step-by-step instructions for creating custom rules.
    Args:
        root_path: Root directory path
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        return commands.get_focus_help(env)


@mcp.tool()
def lc_missing(root_path: str, param_type: str, data: str, timestamp: float) -> str:
    """Unified tool for retrieving missing context (files, implementations, or excluded sections).
    Args:
        root_path: Root directory path (e.g. '/home/user/projects/myproject')
        param_type: Type of data - 'f' for files, 'i' for implementations, 'e' for excluded sections
        data: JSON string containing the data (file paths in /{project-name}/ format or implementation queries)
        timestamp: Context generation timestamp
    """
    env = ExecutionEnvironment.create(Path(root_path))
    with env.activate():
        if param_type == "f":
            file_list = ast.literal_eval(data)
            return commands.get_missing_files(env, file_list, timestamp)
        elif param_type == "i":
            impl_list = ast.literal_eval(data)
            return commands.get_implementations(env, impl_list)
        elif param_type == "e":
            file_list = ast.literal_eval(data)
            return commands.get_excluded(env, file_list, timestamp)
        else:
            raise ValueError(
                f"Invalid parameter type: {param_type}. Use 'f' for files, 'i' for implementations, or 'e' for excluded sections."
            )


def run_server():
    mcp.run(transport="stdio")
