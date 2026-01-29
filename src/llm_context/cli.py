import argparse
import ast
from importlib.metadata import version as pkg_ver
from logging import INFO
from pathlib import Path

from llm_context import commands
from llm_context.cmd_pipeline import (
    ExecutionResult,
    create_clipboard_cmd,
    create_command,
    create_init_command,
)
from llm_context.context_generator import ContextSettings
from llm_context.context_spec import ContextSpec
from llm_context.exec_env import ExecutionEnvironment
from llm_context.utils import log


def rule_feedback(env: ExecutionEnvironment, rule_name: str):
    log(INFO, f"Active rule: {rule_name}")


@create_init_command
def init_project(env: ExecutionEnvironment):
    log(INFO, f"LLM Context initialized for project: {env.state.project_layout.root_path}")
    log(
        INFO,
        "See the user guide for setup and customization: https://github.com/cyberchitta/llm-context.py/blob/main/docs/user-guide.md",
    )
    return ExecutionResult(None, env)


@create_command
def set_rule(env: ExecutionEnvironment) -> ExecutionResult:
    parser = argparse.ArgumentParser(description="Set active rule for LLM context")
    parser.add_argument("rule", type=str, help="Rule to set as active")
    args = parser.parse_args()
    config = ContextSpec.create(env.state.project_layout.root_path, args.rule, env.constants)
    if not config.has_rule(args.rule):
        raise ValueError(f"Rule '{args.rule}' does not exist.")
    nxt_state = env.state.with_current_rule(args.rule)
    nxt_env = env.with_state(nxt_state)
    nxt_env.state.store()
    log(INFO, f"Active rule set to '{args.rule}'.")
    return ExecutionResult(None, nxt_env)


@create_init_command
def version(*, env: ExecutionEnvironment) -> ExecutionResult:
    log(INFO, f"llm-context version {pkg_ver('llm-context')}")
    return ExecutionResult(None, env)


@create_command
def select(env: ExecutionEnvironment) -> ExecutionResult:
    rule_name = env.state.current_rule
    rule_feedback(env, rule_name)
    file_selection = commands.select_all_files(env, rule_name)
    nxt_env = env.with_state(env.state.with_selection(file_selection))
    nxt_env.state.store()
    log(
        INFO,
        f"Selected {len(file_selection.full_files)} full files and {len(file_selection.excerpted_files)} excerpted files.",
    )
    return ExecutionResult(None, nxt_env)


@create_clipboard_cmd
def rule_instructions(env: ExecutionEnvironment) -> ExecutionResult:
    content = commands.get_focus_help(env)
    return ExecutionResult(content, env)


@create_clipboard_cmd
def prompt(env: ExecutionEnvironment) -> ExecutionResult:
    rule_name = env.state.current_rule
    rule_feedback(env, rule_name)
    content = commands.get_prompt(env, rule_name)
    return ExecutionResult(content, env)


@create_clipboard_cmd
def context(env: ExecutionEnvironment) -> ExecutionResult:
    rule_name = env.state.current_rule
    rule_feedback(env, rule_name)
    parser = argparse.ArgumentParser(description="Generate context for LLM")
    parser.add_argument("-p", action="store_true", help="Include prompt in context")
    parser.add_argument("-nt", action="store_true", help="Assume no MCP/tools")
    parser.add_argument("-u", action="store_true", help="Include user notes in context")
    parser.add_argument("-f", type=str, help="Write context to file")
    parser.add_argument("-m", action="store_true", help="Send context as separate message")
    args, _ = parser.parse_known_args()
    settings = ContextSettings.create(args.p, args.u, not args.nt, args.m)
    content, context_timestamp = commands.generate_context(env, rule_name, settings)
    updated_selection = env.state.get_selection(rule_name).with_timestamp(context_timestamp)
    nxt_env = env.with_state(env.state.with_selection(updated_selection))
    nxt_env.state.store()
    if args.f:
        Path(args.f).write_text(content)
        log(INFO, f"Wrote context to {args.f}")
    return ExecutionResult(content, env)


@create_clipboard_cmd
def outlines(env: ExecutionEnvironment) -> ExecutionResult:
    rule_name = env.state.current_rule
    rule_feedback(env, rule_name)
    content = commands.get_outlines(env, rule_name)
    return ExecutionResult(content, env)


@create_clipboard_cmd
def changed_files(env: ExecutionEnvironment) -> ExecutionResult:
    timestamp = env.state.get_selection(env.state.current_rule).timestamp
    return ExecutionResult(commands.list_modified_files(env, timestamp), env)


@create_clipboard_cmd
def missing(env: ExecutionEnvironment) -> ExecutionResult:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", type=str)
    parser.add_argument("-i", type=str)
    parser.add_argument("-e", type=str)
    parser.add_argument("-t", type=float, required=True)
    args = parser.parse_args()
    param_count = sum(1 for param in [args.f, args.i, args.e] if param)
    if param_count != 1:
        parser.error("Must specify exactly one of -f, -i, or -e")
    if args.f:
        file_list = ast.literal_eval(args.f)
        content = commands.get_missing_files(env, file_list, args.t)
    elif args.i:
        impl_list = ast.literal_eval(args.i)
        content = commands.get_implementations(env, impl_list, args.t)  # ← Pass timestamp
    else:
        file_list = ast.literal_eval(args.e)
        content = commands.get_excluded(env, file_list, args.t)
    return ExecutionResult(content, env)


@create_command
def preview(env: ExecutionEnvironment) -> ExecutionResult:
    parser = argparse.ArgumentParser(description="Preview rule file selection and sizes")
    parser.add_argument("rule", type=str, help="Rule to preview")
    args = parser.parse_args()
    result = commands.preview_rule(env, args.rule)
    log(INFO, result)
    return ExecutionResult(None, env)
