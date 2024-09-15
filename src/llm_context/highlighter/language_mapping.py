from dataclasses import dataclass
from importlib import resources
from typing import Optional


def to_language(filename: str) -> Optional[str]:
    ext_to_lang = {
        "c": "c",
        "cc": "cpp",
        "cs": "c_sharp",
        "cpp": "cpp",
        "el": "elisp",
        "ex": "elixir",
        "elm": "elm",
        "go": "go",
        "java": "java",
        "js": "javascript",
        "mjs": "javascript",
        "ml": "ocaml",
        "php": "php",
        "py": "python",
        "ql": "ql",
        "rb": "ruby",
        "rs": "rust",
        "ts": "typescript",
    }
    extension = filename.split(".")[-1]
    return ext_to_lang.get(extension)


def to_query_file_name(lang: str) -> Optional[str]:
    return f"tree-sitter-{lang}-tags.scm" if lang else None


@dataclass(frozen=True)
class TagQuery:
    def get_query(self, language: str) -> str:
        if language == "typescript":
            return self._read_query("javascript") + self._read_query("typescript")
        return self._read_query(language)

    def _read_query(self, language: str) -> str:
        query_file_name = to_query_file_name(language)
        if not query_file_name:
            raise ValueError(f"Unsupported language: {language}")
        try:
            return (
                resources.files("llm_context.highlighter.tag-qry")
                .joinpath(query_file_name)
                .read_text()
            )
        except FileNotFoundError:
            raise ValueError(f"Query file not found for language: {language}")
