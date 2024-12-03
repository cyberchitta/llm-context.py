import logging
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from llm_context.config import ProjectLayout
from llm_context.context_generator import ContextSpec
from llm_context.file_selector import ContextSelector
from llm_context.state import FileSelection, StateStore


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
    file_selection: FileSelection

    @staticmethod
    def load(project_layout: ProjectLayout) -> "ExecutionState":
        return ExecutionState.create(
            project_layout, StateStore(project_layout.state_store_path).load()
        )

    @staticmethod
    def create(project_layout: ProjectLayout, file_selection: FileSelection) -> "ExecutionState":
        return ExecutionState(project_layout, file_selection)

    def store(self):
        StateStore(self.project_layout.state_store_path).save(self.file_selection)

    def with_selection(self, file_selection: FileSelection) -> "ExecutionState":
        return ExecutionState.create(self.project_layout, file_selection)

    def with_profile(self, profile_name: str) -> "ExecutionState":
        return self.with_selection(self.file_selection.with_profile(profile_name))


@dataclass(frozen=True)
class ExecutionEnvironment:
    _current: ClassVar[ContextVar[Optional["ExecutionEnvironment"]]] = ContextVar(
        "current_env", default=None
    )
    config: ContextSpec
    runtime: RuntimeContext
    state: ExecutionState

    @staticmethod
    def create(project_root: Path) -> "ExecutionEnvironment":
        runtime = RuntimeContext.create()
        project_layout = ProjectLayout(project_root)
        state = ExecutionState.load(project_layout)
        config = ContextSpec.create(project_root, state.file_selection.profile)
        return ExecutionEnvironment(config, runtime, state)

    def with_state(self, new_state: ExecutionState) -> "ExecutionEnvironment":
        return ExecutionEnvironment(self.config, self.runtime, new_state)

    def with_profile(self, profile: str) -> "ExecutionEnvironment":
        if profile == self.state.file_selection.profile:
            return self
        config = ContextSpec.create(self.config.project_root_path, profile)
        selector = ContextSelector.create(config)
        file_selection = selector.select_full_files(self.state.file_selection)
        outline_selection = selector.select_outline_files(file_selection)
        return self.with_state(self.state.with_selection(outline_selection))

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
