from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from llm_context.excerpters.parser import Source


@dataclass(frozen=True)
class Excerpt:
    rel_path: str
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Excerpts:
    excerpts: list[Excerpt]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Excluded:
    sections: dict[str, str]  # section_name -> content
    metadata: dict[str, Any]


class Excerpter(ABC):
    @abstractmethod
    def excerpt(self, sources: list[Source]) -> Excerpts:
        pass

    @abstractmethod
    def excluded(self, sources: list[Source]) -> list[Excluded]:
        pass
