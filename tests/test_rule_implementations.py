import pytest

from llm_context import cli


@pytest.mark.parametrize("project_name", ["p", "long-project-name"])
def test_context_extracts_project_relative_rule_implementation(
    make_project, monkeypatch, capsys, project_name
):
    root = make_project(project_name)
    (root / "src").mkdir()
    (root / "src" / "helper.py").write_text('def useful():\n    return "IMPLEMENTATION_BODY"\n')
    (root / ".llm-context" / "rules" / "prm-definition.md").write_text("""---
description: Extract only a definition
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
implementations:
  - ["/src/helper.py", "useful"]
---
""")
    capsys.readouterr()
    monkeypatch.setattr("sys.argv", ["lc-context", "-r", "prm-definition"])
    cli.context()
    pack = capsys.readouterr().out
    assert 'return "IMPLEMENTATION_BODY"' in pack
    assert f"/{project_name}/src/helper.py" in pack
    assert "**0** file(s) included in full" in pack
