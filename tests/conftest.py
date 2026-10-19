from pathlib import Path

import pytest

from llm_context import cli


@pytest.fixture
def make_project(tmp_path, monkeypatch):
    """Return a factory that runs `lc-init` in a fresh project under a fake home.

    Clipboard writes fail the test, so commands must be routed to stdout.
    """

    def make(name: str = "project") -> Path:
        root = tmp_path / name
        root.mkdir()
        home = tmp_path / "home"
        home.mkdir(exist_ok=True)
        monkeypatch.setattr(Path, "home", lambda: home)
        monkeypatch.setattr("pyperclip.copy", lambda _: pytest.fail("Unexpected clipboard write"))
        monkeypatch.chdir(root)
        (root / ".gitignore").write_text(".claude/\n")
        monkeypatch.setattr("sys.argv", ["lc-init"])
        cli.init_project()
        return root

    return make
