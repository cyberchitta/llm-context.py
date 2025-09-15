from pathlib import Path
from typing import Optional

from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.context_spec import ContextSpec
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.state import FileSelection


def get_prompt(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, False)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
    return generator.prompt()


def select_all_files(env: ExecutionEnvironment) -> FileSelection:
    selector = ContextSelector.create(env.config)
    file_sel_full = selector.select_full_files(env.state.file_selection)
    return selector.select_excerpted_files(file_sel_full)


def get_missing_files(env: ExecutionEnvironment, paths: list[str], timestamp: float) -> str:
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. Warn the user that the context is stale."
        )
    settings = ContextSettings.create(False, False, True)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
    return generator.missing_files(paths, matching_selection, timestamp)


def list_modified_files(env: ExecutionEnvironment, rule_name: str, timestamp: float) -> list[str]:
    config = ContextSpec.create(env.config.project_root_path, rule_name, env.constants)
    selector = ContextSelector.create(config, timestamp)
    file_sel_full = selector.select_full_files(FileSelection.create(rule_name, [], []))
    file_sel_excerpted = selector.select_excerpted_files(file_sel_full)
    return file_sel_excerpted.files


def get_excluded(env: ExecutionEnvironment, paths: list[str], timestamp: float) -> str:
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(f"No context found with timestamp {timestamp}...")
    settings = ContextSettings.create(False, False, True)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings, env.tagger)
    return generator.excluded(paths, matching_selection, timestamp)


def get_implementations(env: ExecutionEnvironment, queries: list[tuple[str, str]]) -> str:
    settings = ContextSettings.create(False, False, True)
    return ContextGenerator.create(
        env.config, env.state.file_selection, settings, env.tagger
    ).definitions(queries)


def get_focus_help(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, True)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
    return generator.focus_help()


def generate_context(env: ExecutionEnvironment, settings: ContextSettings) -> tuple[str, float]:
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings, env.tagger)
    return generator.context()


def get_outlines(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, False)
    selector = ContextSelector.create(env.config)
    file_sel_excerpted = selector.select_excerpted_only(env.state.file_selection)
    return ContextGenerator.create(env.config, file_sel_excerpted, settings, env.tagger).outlines()


def get_context(
    env: ExecutionEnvironment,
    with_prompt: bool = False,
    with_user_notes: bool = False,
    tools_available: bool = True,
    output_file: Optional[str] = None,
) -> tuple[str, float]:
    settings = ContextSettings.create(with_prompt, with_user_notes, tools_available)
    content, context_timestamp = generate_context(env, settings)
    if output_file:
        Path(output_file).write_text(content)
    return content, context_timestamp
