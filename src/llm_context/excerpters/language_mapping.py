from dataclasses import dataclass
from importlib import resources
from typing import Optional


def to_language(filename: str) -> Optional[str]:
    ext_to_lang = {
        "c": "c",
        "cc": "cpp",
        "cs": "csharp",
        "cpp": "cpp",
        "el": "elisp",
        "ex": "elixir",
        "elm": "elm",
        "go": "go",
        "java": "java",
        "js": "javascript",
        "mjs": "javascript",
        "php": "php",
        "py": "python",
        "rb": "ruby",
        "rs": "rust",
        "svelte": "svelte",
        "ts": "typescript",
        "vue": "vue",
    }
    extension = filename.split(".")[-1]
    return ext_to_lang.get(extension)


_tag_languages = [
    "c",
    "cpp",
    "csharp",
    "elisp",
    "elixir",
    "elm",
    "go",
    "java",
    "javascript",
    "php",
    "python",
    "ruby",
    "rust",
    "typescript",
]


@dataclass(frozen=True)
class LangQuery:
    def get_tag_query(self, language: str) -> str:
        assert language in _tag_languages
        if language == "typescript":
            return self._read_tag_query("javascript") + self._read_tag_query("typescript")
        return self._read_tag_query(language)

    def _read_tag_query(self, language: str) -> str:
        filename = f"{language}-tags.scm"
        return resources.files("llm_context.excerpters.ts-qry").joinpath(filename).read_text()
