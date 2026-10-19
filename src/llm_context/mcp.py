import ast
from contextlib import contextmanager
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from llm_context import commands
from llm_context.exceptions import LLMContextError
from llm_context.exec_env import ExecutionEnvironment

mcp = MCPServer("llm-context")


@contextmanager
def _activated(root_path: str):
    """Activate the project env; report expected failures to the model.

    MCPServer (mcp 2.x) shows the model only "Error executing tool <name>" for any
    exception other than ToolError, which hides messages such as a stale timestamp
    or an unknown rule.
    """
    try:
        env = ExecutionEnvironment.create(Path(root_path))
        with env.activate():
            yield env
    except (ValueError, SyntaxError, LLMContextError) as e:
        raise ToolError(str(e)) from e


@mcp.tool()
def lc_changed(root_path: str, timestamp: float) -> str:
    """Returns list of files modified since given timestamp.
    Args:
        root_path: Root directory path (e.g. '/home/user/projects/myproject')
        timestamp: Unix timestamp to check modifications since
    """
    with _activated(root_path) as env:
        return commands.list_modified_files(env, timestamp)


@mcp.tool()
def lc_outlines(root_path: str, rule_name: str) -> str:
    """Returns excerpted content highlighting important sections in all supported files.
    Args:
        root_path: Root directory path
        rule_name: Rule to use for file selection rules
    """
    with _activated(root_path) as env:
        return commands.get_outlines(env, rule_name)


@mcp.tool()
def lc_rule_instructions(root_path: str) -> str:
    """Provides step-by-step instructions for creating custom rules.
    Args:
        root_path: Root directory path
    """
    with _activated(root_path) as env:
        return commands.get_focus_help(env)


@mcp.tool()
def lc_preview(root_path: str, rule_name: str) -> str:
    """Preview what files a rule selects and their sizes.
    Args:
        root_path: Root directory path (e.g. '/home/user/projects/myproject')
        rule_name: Name of the rule to preview (e.g. 'prm-code', 'tmp-prm-auth-jwt')
    """
    with _activated(root_path) as env:
        return commands.preview_rule(env, rule_name)


@mcp.tool()
def lc_missing(root_path: str, param_type: str, data: str, timestamp: float) -> str:
    """Unified tool for retrieving missing context (files, implementations, or excluded sections).
    Args:
        root_path: Root directory path (e.g. '/home/user/projects/myproject')
        param_type: Type of data - 'f' for files, 'i' for implementations, 'e' for excluded sections
        data: JSON string containing the data (file paths in /{project-name}/ format or implementation queries)
        timestamp: Context generation timestamp
    """
    with _activated(root_path) as env:
        if param_type == "f":
            file_list = ast.literal_eval(data)
            return commands.get_missing_files(env, file_list, timestamp)
        elif param_type == "i":
            impl_list = ast.literal_eval(data)
            return commands.get_implementations(env, impl_list, timestamp)  # ← Pass timestamp
        elif param_type == "e":
            file_list = ast.literal_eval(data)
            return commands.get_excluded(env, file_list, timestamp)
        else:
            raise ValueError(
                f"Invalid parameter type: {param_type}. Use 'f' for files, 'i' for implementations, or 'e' for excluded sections."
            )


def run_server():
    mcp.run(transport="stdio")
