import logging
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Optional

from llm_context.context_spec import ContextSpec
from llm_context.file_selector import ContextSelector
from llm_context.profile import ToolConstants
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
    profile_name: str

    @staticmethod
    def load(project_layout: ProjectLayout) -> "ExecutionState":
        store = StateStore(project_layout.state_store_path)
        selections, current_profile = store.load()
        return ExecutionState(project_layout, selections, current_profile)

    @staticmethod
    def create(
        project_layout: ProjectLayout, selections: AllSelections, profile_name: str
    ) -> "ExecutionState":
        return ExecutionState(project_layout, selections, profile_name)

    @property
    def file_selection(self) -> FileSelection:
        return self.selections.get_selection(self.profile_name)

    def store(self):
        StateStore(self.project_layout.state_store_path).save(self.selections, self.profile_name)

    def with_selection(self, file_selection: FileSelection) -> "ExecutionState":
        new_selections = self.selections.with_selection(file_selection)
        return ExecutionState(self.project_layout, new_selections, self.profile_name)

    def with_profile(self, profile_name: str) -> "ExecutionState":
        return ExecutionState(self.project_layout, self.selections, profile_name)


@dataclass(frozen=True)
class ExecutionEnvironment:
    _current: ClassVar[ContextVar[Optional["ExecutionEnvironment"]]] = ContextVar(
        "current_env", default=None
    )
    config: ContextSpec
    runtime: RuntimeContext
    state: ExecutionState
    constants: ToolConstants
    tagger: Optional[Any]

    @staticmethod
    def create(project_root: Path) -> "ExecutionEnvironment":
        runtime = RuntimeContext.create()
        project_layout = ProjectLayout(project_root)
        state = ExecutionState.load(project_layout)
        constants = ToolConstants.load(project_layout.state_path)
        config = ContextSpec.create(project_root, state.file_selection.profile_name, constants)
        tagger = ExecutionEnvironment._tagger(project_root)
        return ExecutionEnvironment(config, runtime, state, constants, tagger)

    @staticmethod
    def _tagger(project_root: Path):
        if ContextSelector.has_outliner(False):
            from llm_context.highlighter.parser import ASTFactory
            from llm_context.highlighter.tagger import ASTBasedTagger

            return ASTBasedTagger.create(str(project_root), ASTFactory.create())
        else:
            return None

    def with_state(self, new_state: ExecutionState) -> "ExecutionEnvironment":
        return ExecutionEnvironment(
            self.config, self.runtime, new_state, self.constants, self.tagger
        )

    def with_profile(self, profile_name: str) -> "ExecutionEnvironment":
        if profile_name == self.state.file_selection.profile_name:
            return self
        config = ContextSpec.create(self.config.project_root_path, profile_name, self.constants)
        empty_selection = FileSelection.create(profile_name, [], [])
        selector = ContextSelector.create(config)
        file_selection = selector.select_full_files(empty_selection)
        outline_selection = (
            selector.select_outline_files(file_selection)
            if selector.has_outliner(False)
            else file_selection
        )
        new_state = self.state.with_selection(outline_selection).with_profile(profile_name)
        return ExecutionEnvironment(config, self.runtime, new_state, self.constants, self.tagger)

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
