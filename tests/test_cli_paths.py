from pathlib import Path

import pytest

from llm_context import cli


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setattr("pyperclip.copy", lambda _: pytest.fail("Unexpected clipboard write"))
    monkeypatch.chdir(root)
    (root / ".gitignore").write_text(".claude/\n")
    monkeypatch.setattr("sys.argv", ["lc-init"])
    cli.init_project()
    (root / "src").mkdir()
    (root / "src" / "helper.py").write_text('def useful():\n    return "HELPER_BODY"\n')
    return root


@pytest.mark.parametrize("overview", ["full", "focused"])
def test_cli_uses_posix_paths_for_nested_files(project, monkeypatch, capsys, overview):
    (project / ".llm-context" / "rules" / "prm-test.md").write_text(f"""---
description: Nested files
overview: {overview}
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/helper.py"]
---
""")
    capsys.readouterr()
    monkeypatch.setattr("sys.argv", ["lc-preview", "-r", "prm-test"])
    cli.preview()
    assert "/project/src/helper.py" in capsys.readouterr().out
    monkeypatch.setattr("sys.argv", ["lc-context", "-r", "prm-test"])
    cli.context()
    pack = capsys.readouterr().out
    assert 'return "HELPER_BODY"' in pack
    assert "/project/src/helper.py" in pack
    assert "/project/src\\" not in pack
    if overview == "focused":
        assert "/project/src/ (1 files)" in pack
