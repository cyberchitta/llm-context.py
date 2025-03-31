import argparse
from importlib.metadata import version as pkg_ver
from logging import INFO
from pathlib import Path

import pyperclip  # type: ignore

from llm_context.cmd_pipeline import ExecutionResult, create_clipboard_cmd, create_command
from llm_context.context_generator import ContextGenerator, ContextSettings
from llm_context.exec_env import ExecutionEnvironment
from llm_context.file_selector import ContextSelector
from llm_context.utils import log


def rule_feedback(env: ExecutionEnvironment):
    log(INFO, f"Active rule: {env.state.file_selection.rule_name}")


def set_rule(rule: str, env: ExecutionEnvironment) -> ExecutionResult:
    if not env.config.has_rule(rule):
        raise ValueError(f"Rule '{rule}' does not exist.")
    nxt_env = env.with_rule(rule)
    nxt_env.state.store()
    log(INFO, f"Active rule set to '{rule}'.")
    return ExecutionResult(None, nxt_env)


def select_all_files(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    selector = ContextSelector.create(env.config)
    file_sel_full = selector.select_full_files(env.state.file_selection)
    file_sel_out = selector.select_outline_files(file_sel_full)
    nxt_env = env.with_state(env.state.with_selection(file_sel_out))
    nxt_env.state.store()
    return ExecutionResult(None, nxt_env)


@create_command
def init_project(env: ExecutionEnvironment):
    log(INFO, f"LLM Context initialized for project: {env.config.project_root}")
    log(INFO, "You can now edit .llm-context/config.yaml to customize ignore patterns.")
    return ExecutionResult(None, env)


@create_command
def set_rule_with_args(env: ExecutionEnvironment) -> ExecutionResult:
    parser = argparse.ArgumentParser(description="Set active rule for LLM context")
    parser.add_argument(
        "rule",
        type=str,
        help="Rule to set as active",
    )
    args = parser.parse_args()
    res = set_rule(args.rule, env)
    res.env.state.store()
    return res


@create_command
def show_version(*, env: ExecutionEnvironment) -> ExecutionResult:
    log(INFO, f"llm-context version {pkg_ver('llm-context')}")
    return ExecutionResult(None, env)


@create_command
def select_full_files(env: ExecutionEnvironment):
    rule_feedback(env)
    selector = ContextSelector.create(env.config)
    file_selection = selector.select_full_files(env.state.file_selection)
    nxt_env = env.with_state(env.state.with_selection(file_selection))
    nxt_env.state.store()
    log(INFO, f"Selected {len(file_selection.full_files)} full files.")
    return ExecutionResult(None, nxt_env)


@create_command
def select_outline_files(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    selector = ContextSelector.create(env.config)
    file_selection = selector.select_outline_files(env.state.file_selection)
    nxt_env = env.with_state(env.state.with_selection(file_selection))
    nxt_env.state.store()
    log(INFO, f"Selected {len(file_selection.outline_files)} outline files.")
    return ExecutionResult(None, nxt_env)


@create_clipboard_cmd
def files_from_scratch(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    settings = ContextSettings.create(False, False)
    return ExecutionResult(
        ContextGenerator.create(env.config, env.state.file_selection, settings).files([]), env
    )


@create_clipboard_cmd
def files_from_clip(in_files: list[str] = [], *, env: ExecutionEnvironment):
    settings = ContextSettings.create(False, False)
    return ExecutionResult(
        ContextGenerator.create(env.config, env.state.file_selection, settings).files(
            pyperclip.paste().strip().split("\n")
        ),
        env,
    )


@create_clipboard_cmd
def prompt(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    settings = ContextSettings.create(False, False)
    content = ContextGenerator.create(env.config, env.state.file_selection, settings).prompt()
    nxt_env = env.with_state(env.state.with_selection(env.state.file_selection.with_now()))
    nxt_env.state.store()
    return ExecutionResult(content, env)


@create_clipboard_cmd
def context(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    parser = argparse.ArgumentParser(description="Generate context for LLM")
    parser.add_argument("-p", action="store_true", help="Include prompt in context")
    parser.add_argument("-u", action="store_true", help="Include user notes in context")
    parser.add_argument("-f", type=str, help="Write context to file")
    args, _ = parser.parse_known_args()
    settings = ContextSettings.create(args.p, args.u)
    generator = ContextGenerator.create(env.config, env.state.file_selection, settings, env.tagger)
    content = generator.context()
    nxt_env = env.with_state(env.state.with_selection(env.state.file_selection.with_now()))
    nxt_env.state.store()
    if args.f:
        Path(args.f).write_text(content)
        log(INFO, f"Wrote context to {args.f}")
    return ExecutionResult(content, env)


@create_clipboard_cmd
def outlines(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    settings = ContextSettings.create(False, False)
    selector = ContextSelector.create(env.config)
    file_sel_out = selector.select_outline_only(env.state.file_selection)
    content = ContextGenerator.create(env.config, file_sel_out, settings, env.tagger).outlines()
    return ExecutionResult(content, env)


@create_clipboard_cmd
def changed_files(env: ExecutionEnvironment) -> ExecutionResult:
    timestamp = env.state.file_selection.timestamp
    selector = ContextSelector.create(env.config, timestamp)
    file_sel_full = selector.select_full_files(env.state.file_selection)
    file_sel_out = selector.select_outline_files(file_sel_full)
    return ExecutionResult("\n".join(file_sel_out.files), env)


@create_clipboard_cmd
def implementations_from_clip(env: ExecutionEnvironment) -> ExecutionResult:
    settings = ContextSettings.create(False, False)
    clip = pyperclip.paste().strip()
    requests = [(w[0], w[1]) for line in clip.splitlines() if len(w := line.split(":", 1)) == 2]
    content = ContextGenerator.create(
        env.config, env.state.file_selection, settings, env.tagger
    ).definitions(requests)
    return ExecutionResult(content, env)
