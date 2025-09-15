import argparse
import ast
from importlib.metadata import version as pkg_ver
from logging import INFO

from llm_context import commands
from llm_context.cmd_pipeline import (
    ExecutionResult,
    create_clipboard_cmd,
    create_command,
    create_init_command,
)
from llm_context.context_generator import ContextSettings
from llm_context.exec_env import ExecutionEnvironment
from llm_context.utils import log


def rule_feedback(env: ExecutionEnvironment):
    log(INFO, f"Active rule: {env.state.file_selection.rule_name}")


def _set_rule(rule: str, env: ExecutionEnvironment) -> ExecutionResult:
    if not env.config.has_rule(rule):
        raise ValueError(f"Rule '{rule}' does not exist.")
    nxt_env = env.with_rule(rule)
    nxt_env.state.store()
    log(INFO, f"Active rule set to '{rule}'.")
    return ExecutionResult(None, nxt_env)


@create_init_command
def init_project(env: ExecutionEnvironment):
    log(INFO, f"LLM Context initialized for project: {env.config.project_root}")
    log(
        INFO,
        "See the user guide for setup and customization: https://github.com/cyberchitta/llm-context.py/blob/main/docs/user-guide.md",
    )
    return ExecutionResult(None, env)


@create_command
def set_rule(env: ExecutionEnvironment) -> ExecutionResult:
    parser = argparse.ArgumentParser(description="Set active rule for LLM context")
    parser.add_argument(
        "rule",
        type=str,
        help="Rule to set as active",
    )
    args = parser.parse_args()
    res = _set_rule(args.rule, env)
    res.env.state.store()
    return res


@create_init_command
def version(*, env: ExecutionEnvironment) -> ExecutionResult:
    log(INFO, f"llm-context version {pkg_ver('llm-context')}")
    return ExecutionResult(None, env)


@create_command
def select(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    file_selection = commands.select_all_files(env)
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
    rule_feedback(env)
    content = commands.get_prompt(env)
    return ExecutionResult(content, env)


@create_clipboard_cmd
def context(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    parser = argparse.ArgumentParser(description="Generate context for LLM")
    parser.add_argument("-p", action="store_true", help="Include prompt in context")
    parser.add_argument("-nt", action="store_true", help="Assume no MCP/tools")
    parser.add_argument("-u", action="store_true", help="Include user notes in context")
    parser.add_argument("-f", type=str, help="Write context to file")
    args, _ = parser.parse_known_args()
    settings = ContextSettings.create(args.p, args.u, not args.nt)
    content, context_timestamp = commands.generate_context(env, settings)
    updated_selection = env.state.file_selection.with_timestamp(context_timestamp)
    nxt_env = env.with_state(env.state.with_selection(updated_selection))
    nxt_env.state.store()
    if args.f:
        log(INFO, f"Wrote context to {args.f}")
    return ExecutionResult(content, env)


@create_clipboard_cmd
def outlines(env: ExecutionEnvironment) -> ExecutionResult:
    rule_feedback(env)
    content = commands.get_outlines(env)
    return ExecutionResult(content, env)


@create_clipboard_cmd
def changed_files(env: ExecutionEnvironment) -> ExecutionResult:
    timestamp = env.state.file_selection.timestamp
    files = commands.list_modified_files(env, env.state.file_selection.rule_name, timestamp)
    return ExecutionResult("\n".join(files), env)


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
        content = commands.get_implementations(env, impl_list)
    elif args.e:
        file_list = ast.literal_eval(args.e)
        content = commands.get_excluded(env, file_list, args.t)
    return ExecutionResult(content, env)
