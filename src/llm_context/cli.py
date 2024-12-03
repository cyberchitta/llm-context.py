import argparse
from importlib.metadata import version as pkg_ver
from logging import INFO

import pyperclip  # type: ignore

from llm_context.cmd_pipeline import ExecutionResult, create_clipboard_cmd, create_command
from llm_context.context_generator import ContextGenerator
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.folder_structure_diagram import get_fsd
from llm_context.utils import log


def profile_feedback(env: ExecutionEnvironment):
    log(INFO, f"Active profile: {env.state.file_selection.profile}")


@create_command
def init_project(env: ExecutionEnvironment):
    log(INFO, f"LLM Context initialized for project: {env.config.project_root}")
    log(INFO, "You can now edit .llm-context/config.toml to customize ignore patterns.")
    return ExecutionResult(None, env)


def set_profile(profile: str, env: ExecutionEnvironment) -> ExecutionResult:
    if not env.config.has_profile(profile):
        raise ValueError(f"Profile '{profile}' does not exist.")
    nxt_env = env.with_profile(profile)
    nxt_env.state.store()
    log(INFO, f"Active profile set to '{profile}'.")
    return ExecutionResult(None, nxt_env)


@create_command
def set_profile_with_args(env: ExecutionEnvironment) -> ExecutionResult:
    parser = argparse.ArgumentParser(description="Set active profile for LLM context")
    parser.add_argument(
        "profile",
        type=str,
        help="Profile to set as active",
    )
    args = parser.parse_args()
    res = set_profile(args.profile, env)
    res.env.state.store()
    return res


@create_command
def show_version(*, env: ExecutionEnvironment) -> ExecutionResult:
    log(INFO, f"llm-context version {pkg_ver('llm-context')}")
    return ExecutionResult(None, env)


@create_clipboard_cmd
def get_fs_diagram(*, env: ExecutionEnvironment) -> ExecutionResult:
    return ExecutionResult(get_fsd(), ExecutionEnvironment.current())


@create_command
def select_full_files(env: ExecutionEnvironment):
    profile_feedback(env)
    selector = ContextSelector.create(env.config)
    file_selection = selector.select_full_files(env.state.file_selection)
    nxt_env = env.with_state(env.state.with_selection(file_selection))
    nxt_env.state.store()
    log(INFO, f"Selected {len(file_selection.full_files)} full files.")
    return ExecutionResult(None, nxt_env)


@create_command
def select_outline_files(env: ExecutionEnvironment) -> ExecutionResult:
    profile_feedback(env)
    selector = ContextSelector.create(env.config)
    file_selection = selector.select_outline_files(env.state.file_selection)
    nxt_env = env.with_state(env.state.with_selection(file_selection))
    nxt_env.state.store()
    log(INFO, f"Selected {len(file_selection.outline_files)} outline files.")
    return ExecutionResult(None, nxt_env)


def select_all_files(env: ExecutionEnvironment) -> ExecutionResult:
    profile_feedback(env)
    selector = ContextSelector.create(env.config)
    file_sel_full = selector.select_full_files(env.state.file_selection)
    file_sel_out = selector.select_outline_files(file_sel_full)
    nxt_env = env.with_state(env.state.with_selection(file_sel_out))
    nxt_env.state.store()
    return ExecutionResult(None, nxt_env)


@create_clipboard_cmd
def files_from_scratch(env: ExecutionEnvironment) -> ExecutionResult:
    profile_feedback(env)
    return ExecutionResult(
        ContextGenerator.create(env.config, env.state.file_selection).files([]), env
    )


@create_clipboard_cmd
def files_from_clip(in_files: list[str] = [], *, env: ExecutionEnvironment):
    return ExecutionResult(
        ContextGenerator.create(env.config, env.state.file_selection).files(
            pyperclip.paste().strip().split("\n")
        ),
        env,
    )


@create_clipboard_cmd
def context(env: ExecutionEnvironment) -> ExecutionResult:
    profile_feedback(env)
    return ExecutionResult(
        ContextGenerator.create(env.config, env.state.file_selection).context(), env
    )