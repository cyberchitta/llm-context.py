import asyncio

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from llm_context.mcp import mcp


@pytest.fixture
def project(make_project):
    return make_project()


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
    with pytest.raises(ToolError, match="no-such-rule") as error:
        call("lc_preview", root_path=str(project), rule_name="no-such-rule")
    assert ".." not in str(error.value)


def test_unknown_param_type_message_reaches_the_model(project):
    with pytest.raises(ToolError, match="Invalid parameter type: x"):
        call("lc_missing", root_path=str(project), param_type="x", data="[]", timestamp=0)
