from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, Field


class ContextRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    rule_name: str = Field(
        "lc/prm-developer",
        description="Rule to use (e.g. 'lc/prm-developer', 'prm-copy') - defines file inclusion and presentation rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )


class FilesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    paths: list[str] = Field(
        ...,
        description="File paths relative to root_path, starting with a forward slash and including the root directory name. For example, if root_path is '/home/user/projects/myproject', then a valid path would be '/myproject/src/main.py'",
    )
    timestamp: float = Field(
        ..., description="Context generation timestamp to check against existing selections"
    )


class ListModifiedFilesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    rule_name: str = Field(
        "lc/prm-developer",
        description="Rule to use (e.g. 'lc/prm-developer', 'prm-copy') - defines file inclusion and presentation rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )
    timestamp: float = Field(..., description="Unix timestamp to check modifications since")


class OutlinesRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    rule_name: str = Field(
        "lc/prm-developer",
        description="Rule to use for file selection rules",
        pattern="^[a-zA-Z0-9_-]+$",
    )
    timestamp: float = Field(
        ..., description="Context generation timestamp to check against existing selections"
    )


class ImplementationsRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )
    queries: list[tuple[str, str]] = Field(
        ..., description="list of (file_path, definition_name) tuples to fetch implementations for"
    )


class FocusHelpRequest(BaseModel):
    root_path: Path = Field(
        ..., description="Root directory path (e.g. '/home/user/projects/myproject')"
    )


TOOL_METADATA: dict[str, dict[str, Any]] = {
    "lc-project-context": {
        "model": ContextRequest,
        "description": (
            "⛔️ DO NOT USE this tool when you already have the project context. "
            "First check if project context is already available in the conversation "
            "before making any new requests. Use lc-get-files for retrieving specific files, "
            "and only use this tool when a broad repository overview is needed.\n\n"
            "Generates a structured repository overview including: "
            "1) Directory tree with file status (✓ full, ○ outline, ✗ excluded) "
            "2) Complete contents of key files "
            "3) Smart outlines highlighting important definitions in supported languages. "
            "The output is customizable via profiles that control file inclusion rules "
            "and presentation format. The assistant tracks previously retrieved project "
            "context in the conversation and checks this history before making new requests."
        ),
    },
    "lc-get-files": {
        "model": FilesRequest,
        "description": (
            "⚠️ ALWAYS SEARCH THE ENTIRE CONVERSATION CONTEXT FIRST! DO NOT request files "
            "that have already been provided. Retrieves (read-only) complete contents "
            "of specified files from the project. Requires the context generation timestamp "
            "to check against existing file selections. Files already included with full content "
            "will return a message instead of duplicate content. Files included as outlines "
            "will be upgraded to full content."
        ),
    },
    "lc-list-modified-files": {
        "model": ListModifiedFilesRequest,
        "description": (
            "IMPORTANT: First get the generation timestamp from the project context. "
            "Returns a list of paths to files that have been modified since a given timestamp. "
            "This is typically used to track which files have changed during the conversation. "
            "After getting the list, use lc-get-files to examine the contents of any modified files of interest."
        ),
    },
    "lc-code-outlines": {
        "model": OutlinesRequest,
        "description": (
            "Returns smart outlines highlighting important definitions in all supported code files. "
            "Requires the context generation timestamp to check against existing selections. "
            "If outlines are already included in the current context, returns a message instead "
            "of duplicate content. This provides a high-level overview of code structure without "
            "retrieving full file contents. Use lc-get-implementations to retrieve the full "
            "implementation of any definition shown in these outlines."
        ),
    },
    "lc-get-implementations": {
        "model": ImplementationsRequest,
        "description": (
            "Retrieves complete code implementations of definitions identified in code outlines. "
            "Provide a list of file paths and definition names to get their full implementations. "
            "This tool works with all supported languages except C and C++."
        ),
    },
    "lc-create-rule-instructions": {
        "model": FocusHelpRequest,
        "description": (
            "Call this tool when asked to create a focused rule, minimize context, or generate context for a specific task. "
            "Provides step-by-step instructions for creating custom rules that include only the minimum necessary files for a given objective. "
            "Use whenever someone requests focused context, targeted rules, or context reduction for a particular purpose."
        ),
    },
}


def pydantic_to_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    schema = model.model_json_schema()
    if "$defs" in schema:
        del schema["$defs"]
    if "title" in schema:
        del schema["title"]
    if "properties" in schema:
        for prop_name, prop_def in schema["properties"].items():
            if prop_def.get("format") == "path":
                prop_def["type"] = "string"
                if "format" in prop_def:
                    del prop_def["format"]
    return schema


def get_tool_definitions() -> list[dict[str, Any]]:
    tools = []
    for tool_name, metadata in TOOL_METADATA.items():
        model = metadata["model"]
        description = metadata["description"]
        schema = pydantic_to_json_schema(model)
        tools.append(
            {"name": tool_name, "description": description, "schema": schema, "model": model}
        )
    return tools


def get_tool_definition(name: str) -> dict[str, Any]:
    tools = get_tool_definitions()
    for tool in tools:
        if tool["name"] == name:
            return tool
    raise ValueError(f"Tool '{name}' not found")


def get_request_model(tool_name: str) -> type[BaseModel]:
    if tool_name not in TOOL_METADATA:
        raise ValueError(f"Tool '{tool_name}' not found")
    return cast(type[BaseModel], TOOL_METADATA[tool_name]["model"])


def get_mcp_tools() -> list[dict[str, Any]]:
    tools = get_tool_definitions()
    return [
        {"name": tool["name"], "description": tool["description"], "inputSchema": tool["schema"]}
        for tool in tools
    ]


def get_dxt_capabilities() -> dict[str, Any]:
    tools = get_tool_definitions()
    return {
        "tools": [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["schema"],
            }
            for tool in tools
        ]
    }


__all__ = [
    "ContextRequest",
    "FilesRequest",
    "ListModifiedFilesRequest",
    "OutlinesRequest",
    "ImplementationsRequest",
    "get_tool_definitions",
    "get_tool_definition",
    "get_request_model",
    "get_mcp_tools",
    "get_dxt_capabilities",
]
