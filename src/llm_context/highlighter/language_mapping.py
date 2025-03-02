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
        "ts": "typescript",
    }
    extension = filename.split(".")[-1]
    return ext_to_lang.get(extension)


def to_query_file_name(pfx: str, lang: str) -> Optional[str]:
    return f"tree-sitter-{lang}-{"tags" if pfx == "tag" else "body"}.scm" if lang else None


@dataclass(frozen=True)
class LangQuery:
    def get_tag_query(self, language: str) -> str:
        if language == "typescript":
            return self._read_tag_query("javascript") + self._read_tag_query("typescript")
        return self._read_tag_query(language)

    def _read_tag_query(self, language: str) -> str:
        return self._read_query("tag", language)

    def _read_query(self, pfx: str, language: str) -> str:
        query_file_name = to_query_file_name(pfx, language)
        if not query_file_name:
            raise ValueError(f"Unsupported language: {language}")
        try:
            return (
                resources.files(f"llm_context.highlighter.{pfx}-qry")
                .joinpath(query_file_name)
                .read_text()
            )
        except FileNotFoundError:
            raise ValueError(f"Query file not found for language: {language}")
