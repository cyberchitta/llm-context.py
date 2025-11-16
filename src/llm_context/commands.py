from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.context_spec import ContextSpec
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, is_newer


def get_prompt(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, False, False)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
    return generator.prompt()


def select_all_files(env: ExecutionEnvironment) -> FileSelection:
    selector = ContextSelector.create(env.config)
    file_sel_full = selector.select_full_files(env.state.file_selection)
    return selector.select_excerpted_files(file_sel_full)


def get_missing_files(env: ExecutionEnvironment, paths: list[str], timestamp: float) -> str:
    PathConverter.create(env.config.project_root_path).validate_with_error(paths)
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. Warn the user that the context is stale."
        )
    settings = ContextSettings.create(False, False, True, False)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings, env.tagger)
    return generator.missing_files(paths, matching_selection, timestamp)


def list_modified_files(env: ExecutionEnvironment, timestamp: float) -> str:
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. The context may be stale or deleted."
        )
    config = ContextSpec.create(
        env.config.project_root_path, matching_selection.rule_name, env.constants
    )
    selector = ContextSelector.create(config)
    file_sel_full = selector.select_full_files(matching_selection)
    file_sel_excerpted = selector.select_excerpted_files(file_sel_full)
    current_files = set(file_sel_excerpted.files)
    original_files = set(matching_selection.files)
    converter = PathConverter.create(env.config.project_root_path)
    modified = {
        f
        for f in (current_files & original_files)
        if is_newer(converter.to_absolute([f])[0], timestamp)
    }
    added = current_files - original_files
    removed = original_files - current_files
    result = [
        f"{label}:\n" + "\n".join(sorted(files))
        for label, files in [("Added", added), ("Modified", modified), ("Removed", removed)]
        if files
    ]
    return "\n\n".join(result) if result else "No changes"


def get_excluded(env: ExecutionEnvironment, paths: list[str], timestamp: float) -> str:
    PathConverter.create(env.config.project_root_path).validate_with_error(paths)
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(f"No context found with timestamp {timestamp}...")
    settings = ContextSettings.create(False, False, True, False)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings, env.tagger)
    return generator.excluded(paths, matching_selection, timestamp)


def get_implementations(env: ExecutionEnvironment, queries: list[tuple[str, str]]) -> str:
    PathConverter.create(env.config.project_root_path).validate_with_error([p for p, _ in queries])
    settings = ContextSettings.create(False, False, True, False)
    return ContextGenerator.create(
        env.config, env.state.file_selection, settings, env.tagger
    ).definitions(queries)


def get_focus_help(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, True, False)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
    return generator.focus_help()


def generate_context(env: ExecutionEnvironment, settings: ContextSettings) -> tuple[str, float]:
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings, env.tagger)
    return generator.context()


def get_outlines(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, False, False)
    selector = ContextSelector.create(env.config)
    file_sel_excerpted = selector.select_excerpted_only(env.state.file_selection)
    return ContextGenerator.create(env.config, file_sel_excerpted, settings, env.tagger).outlines()
