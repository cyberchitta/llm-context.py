import asyncio
from pathlib import Path

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from llm_context import cli
from llm_context.mcp import mcp


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.chdir(root)
    (root / ".gitignore").write_text(".claude/\n")
    monkeypatch.setattr("sys.argv", ["lc-init"])
    cli.init_project()
    return root


def call(name, **arguments):
    return asyncio.run(mcp.call_tool(name, arguments))


def test_stale_timestamp_message_reaches_the_model(project):
    with pytest.raises(ToolError, match="No context found with timestamp"):
        call(
            "lc_missing",
            root_path=str(project),
            param_type="f",
            data='["/project/a.py"]',
            timestamp=123,
        )


def test_unknown_rule_message_reaches_the_model(project):
    with pytest.raises(ToolError, match="no-such-rule"):
        call("lc_preview", root_path=str(project), rule_name="no-such-rule")
