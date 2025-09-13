from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.context_spec import ContextSpec
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.state import FileSelection
from llm_context.utils import PathConverter, is_newer


def get_prompt(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, False)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings)
    return generator.prompt()


def select_full_files(env: ExecutionEnvironment) -> FileSelection:
    selector = ContextSelector.create(env.config)
    return selector.select_full_files(env.state.file_selection)


def select_excerpted_files(env: ExecutionEnvironment) -> FileSelection:
    selector = ContextSelector.create(env.config)
    return selector.select_excerpted_files(env.state.file_selection)


def select_all_files(env: ExecutionEnvironment) -> FileSelection:
    selector = ContextSelector.create(env.config)
    file_sel_full = selector.select_full_files(env.state.file_selection)
    return selector.select_excerpted_files(file_sel_full)


def get_files(env: ExecutionEnvironment, paths: list[str], timestamp: float) -> str:
    matching_selection = env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. Warn the user that the context is stale."
        )
    orig_full = set(matching_selection.full_files)
    orig_excerpted = set(matching_selection.excerpted_files)
    converter = PathConverter.create(env.config.project_root_path)
    abs_paths = converter.to_absolute(paths)
    files_to_fetch = {
        r for r, a in zip(paths, abs_paths) if r not in orig_full or is_newer(a, timestamp)
    }
    already_included = set(paths) - files_to_fetch - orig_excerpted
    in_excerpted = set(paths) & orig_excerpted
    response_parts = []
    if already_included:
        response_parts.append(
            "The latest version of the following full files are already included in the current context:\n"
            + "\n".join(already_included)
        )
    if in_excerpted:
        response_parts.append(
            "The following files are included as excerpts. Use lc-get-excluded if you need excluded sections:\n"
            + "\n".join(in_excerpted)
        )
    if files_to_fetch:
        settings = ContextSettings.create(False, False, True)
        content = ContextGenerator.create(env.config, env.state.file_selection, settings).files(
            list(files_to_fetch)
        )
        if content.strip():
            response_parts.append(content)
    return "\n\n".join(response_parts) if response_parts else "No new files to retrieve."


def list_modified_files(env: ExecutionEnvironment, rule_name: str, timestamp: float) -> list[str]:
    config = ContextSpec.create(env.config.project_root_path, rule_name, env.constants)
    selector = ContextSelector.create(config, timestamp)
    file_sel_full = selector.select_full_files(FileSelection.create(rule_name, [], []))
    file_sel_excerpted = selector.select_excerpted_files(file_sel_full)
    return file_sel_excerpted.files


def get_excerpts(env: ExecutionEnvironment, rule_name: str, timestamp: float) -> str:
    cur_env = env.with_rule(rule_name)
    matching_selection = cur_env.state.selections.get_selection_by_timestamp(timestamp)
    if matching_selection is None:
        raise ValueError(
            f"No context found with timestamp {timestamp}. Warn the user that the context is stale."
        )
    if matching_selection.excerpted_files:
        return "Excerpts are already included in the current context."
    selector = ContextSelector.create(cur_env.config)
    file_sel_excerpted = selector.select_excerpted_only(cur_env.state.file_selection)
    settings = ContextSettings.create(False, False, True)
    return ContextGenerator.create(
        cur_env.config, file_sel_excerpted, settings, env.tagger
    ).outlines()


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


def get_files_from_paths(env: ExecutionEnvironment, paths: list[str]) -> str:
    settings = ContextSettings.create(False, False, False)
    return ContextGenerator.create(env.config, env.state.file_selection, settings).files(paths)


def get_outlines(env: ExecutionEnvironment) -> str:
    settings = ContextSettings.create(False, False, False)
    selector = ContextSelector.create(env.config)
    file_sel_excerpted = selector.select_excerpted_only(env.state.file_selection)
    return ContextGenerator.create(env.config, file_sel_excerpted, settings, env.tagger).outlines()
