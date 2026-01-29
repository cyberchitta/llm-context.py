from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.context_preview import ContextPreview
from llm_context.context_spec import ContextSpec
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, is_newer


def get_prompt(env: ExecutionEnvironment, rule_name: str) -> str:
    config = ContextSpec.create(env.state.project_layout.root_path, rule_name, env.constants)
    settings = ContextSettings.create(False, False, False, False)
    file_selection = env.state.get_selection(rule_name)
    generator = ContextGenerator.create(config, file_selection, settings)
    return generator.prompt()


def select_all_files(env: ExecutionEnvironment, rule_name: str) -> FileSelection:
    config = ContextSpec.create(env.state.project_layout.root_path, rule_name, env.constants)
    selector = ContextSelector.create(config)
    current_selection = env.state.get_selection(rule_name)
    file_sel_full = selector.select_full_files(current_selection)
    return selector.select_excerpted_files(file_sel_full)


def get_missing_files(env: ExecutionEnvironment, paths: list[str], timestamp: float) -> str:
    PathConverter.create(env.state.project_layout.root_path).validate_with_error(paths)
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. Warn the user that the context is stale."
        )
    config = ContextSpec.create(
        env.state.project_layout.root_path, matching_selection.rule_name, env.constants
    )
    settings = ContextSettings.create(False, False, True, False)
    file_selection = env.state.get_selection(matching_selection.rule_name)
    generator = ContextGenerator.create(config, file_selection, settings, env.tagger)
    return generator.missing_files(paths, matching_selection, timestamp)


def list_modified_files(env: ExecutionEnvironment, timestamp: float) -> str:
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. The context may be stale or deleted."
        )
    config = ContextSpec.create(
        env.state.project_layout.root_path, matching_selection.rule_name, env.constants
    )
    selector = ContextSelector.create(config)
    file_sel_full = selector.select_full_files(matching_selection)
    file_sel_excerpted = selector.select_excerpted_files(file_sel_full)
    current_files = set(file_sel_excerpted.files)
    original_files = set(matching_selection.files)
    converter = PathConverter.create(env.state.project_layout.root_path)
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
    PathConverter.create(env.state.project_layout.root_path).validate_with_error(paths)
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(f"No context found with timestamp {timestamp}...")
    config = ContextSpec.create(
        env.state.project_layout.root_path, matching_selection.rule_name, env.constants
    )
    settings = ContextSettings.create(False, False, True, False)
    file_selection = env.state.get_selection(matching_selection.rule_name)
    generator = ContextGenerator.create(config, file_selection, settings, env.tagger)
    return generator.excluded(paths, matching_selection, timestamp)


def get_implementations(
    env: ExecutionEnvironment, queries: list[tuple[str, str]], timestamp: float
) -> str:
    PathConverter.create(env.state.project_layout.root_path).validate_with_error(
        [p for p, _ in queries]
    )
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. Implementation queries must reference a valid context."
        )
    config = ContextSpec.create(
        env.state.project_layout.root_path, matching_selection.rule_name, env.constants
    )
    settings = ContextSettings.create(False, False, True, False)
    file_selection = env.state.get_selection(matching_selection.rule_name)
    return ContextGenerator.create(config, file_selection, settings, env.tagger).definitions(
        queries
    )


def get_focus_help(env: ExecutionEnvironment) -> str:
    # Use current_rule for focus help
    config = ContextSpec.create(
        env.state.project_layout.root_path, env.state.current_rule, env.constants
    )
    settings = ContextSettings.create(False, False, True, False)
    file_selection = env.state.get_selection(env.state.current_rule)
    generator = ContextGenerator.create(config, file_selection, settings)
    return generator.focus_help()


def generate_context(
    env: ExecutionEnvironment, rule_name: str, settings: ContextSettings
) -> tuple[str, float]:
    config = ContextSpec.create(env.state.project_layout.root_path, rule_name, env.constants)
    file_selection = env.state.get_selection(rule_name)
    generator = ContextGenerator.create(config, file_selection, settings, env.tagger)
    return generator.context()


def get_outlines(env: ExecutionEnvironment, rule_name: str) -> str:
    config = ContextSpec.create(env.state.project_layout.root_path, rule_name, env.constants)
    settings = ContextSettings.create(False, False, False, False)
    selector = ContextSelector.create(config)
    file_selection = env.state.get_selection(rule_name)
    file_sel_excerpted = selector.select_excerpted_only(file_selection)
    return ContextGenerator.create(config, file_sel_excerpted, settings, env.tagger).outlines()


def preview_rule(env: ExecutionEnvironment, rule_name: str) -> str:
    config = ContextSpec.create(env.state.project_layout.root_path, rule_name, env.constants)
    result = ContextPreview.create(config, env.tagger)
    return result.format()
