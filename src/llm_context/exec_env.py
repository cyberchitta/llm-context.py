import logging
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Optional

from llm_context.excerpters.parser import ASTFactory
from llm_context.excerpters.tagger import ASTBasedTagger
from llm_context.rule import ToolConstants
from llm_context.rule_parser import DEFAULT_CODE_RULE
from llm_context.state import AllSelections, FileSelection, StateStore
from llm_context.utils import ProjectLayout


class MessageCollector(logging.Handler):
    messages: list[str]

    def __init__(self, messages: list[str]):
        super().__init__()
        self.messages = messages

    def emit(self, record):
        msg = self.format(record)
        self.messages.append(msg)


@dataclass(frozen=True)
class RuntimeContext:
    _logger: logging.Logger
    _collector: MessageCollector

    @staticmethod
    def create() -> "RuntimeContext":
        logger = logging.getLogger("llm-context")
        logger.setLevel(logging.INFO)
        messages: list[str] = []
        collector = MessageCollector(messages)
        logger.addHandler(collector)
        return RuntimeContext(logger, collector)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def messages(self) -> list[str]:
        return self._collector.messages


@dataclass(frozen=True)
class ExecutionState:
    project_layout: ProjectLayout
    selections: AllSelections
    current_rule: str

    @staticmethod
    def load(project_layout: ProjectLayout) -> "ExecutionState":
        store = StateStore(project_layout.state_store_path)
        selections, current_rule = store.load()
        return ExecutionState(project_layout, selections, current_rule)

    @staticmethod
    def create(
        project_layout: ProjectLayout, selections: AllSelections, current_rule: str
    ) -> "ExecutionState":
        return ExecutionState(project_layout, selections, current_rule)

    def get_selection(self, rule_name: str) -> FileSelection:
        return self.selections.get_selection(rule_name)

    def store(self):
        StateStore(self.project_layout.state_store_path).save(self.selections, self.current_rule)

    def with_selection(self, file_selection: FileSelection) -> "ExecutionState":
        new_selections = self.selections.with_selection(file_selection)
        return ExecutionState(self.project_layout, new_selections, self.current_rule)

    def with_current_rule(self, rule_name: str) -> "ExecutionState":
        return ExecutionState(self.project_layout, self.selections, rule_name)


@dataclass(frozen=True)
class ExecutionEnvironment:
    _current: ClassVar[ContextVar[Optional["ExecutionEnvironment"]]] = ContextVar(
        "current_env", default=None
    )
    project_layout: ProjectLayout
    runtime: RuntimeContext
    state: ExecutionState
    constants: ToolConstants
    tagger: Optional[Any]

    @staticmethod
    def create_init(project_root: Path) -> "ExecutionEnvironment":
        runtime = RuntimeContext.create()
        project_layout = ProjectLayout(project_root)
        constants = (
            ToolConstants.load(project_layout.state_path)
            if project_layout.state_path.exists()
            else ToolConstants.create_null()
        )
        empty_selections = AllSelections.create_empty()
        state = ExecutionState.create(project_layout, empty_selections, DEFAULT_CODE_RULE)
        tagger = ExecutionEnvironment._tagger(project_root)
        return ExecutionEnvironment(project_layout, runtime, state, constants, tagger)

    @staticmethod
    def create(project_root: Path) -> "ExecutionEnvironment":
        runtime = RuntimeContext.create()
        project_layout = ProjectLayout(project_root)
        state = ExecutionState.load(project_layout)
        constants = ToolConstants.load(project_layout.state_path)
        tagger = ExecutionEnvironment._tagger(project_root)
        return ExecutionEnvironment(project_layout, runtime, state, constants, tagger)

    @staticmethod
    def _tagger(project_root: Path):
        return ASTBasedTagger.create(str(project_root), ASTFactory.create())

    def with_state(self, new_state: ExecutionState) -> "ExecutionEnvironment":
        return ExecutionEnvironment(
            self.project_layout, self.runtime, new_state, self.constants, self.tagger
        )

    @property
    def logger(self) -> logging.Logger:
        return self.runtime.logger

    @staticmethod
    def current() -> "ExecutionEnvironment":
        env = ExecutionEnvironment._current.get()
        if env is None:
            raise RuntimeError("No active execution environment")
        return env

    @staticmethod
    def has_current() -> bool:
        return ExecutionEnvironment._current.get() is not None

    @contextmanager
    def activate(self):
        token = self._current.set(self)
        try:
            yield self
        finally:
            self._current.reset(token)
