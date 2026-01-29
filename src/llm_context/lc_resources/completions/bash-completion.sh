#!/bin/bash
# Bash completion for llm-context commands

_lc_find_rules() {
    # Walk up to find .llm-context/rules directory
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.llm-context/rules" ]]; then
            find "$dir/.llm-context/rules" -name '*.md' 2>/dev/null | \
                sed "s|$dir/.llm-context/rules/||" | \
                sed 's/\.md$//' | \
                grep 'prm'
            return
        fi
        dir=$(dirname "$dir")
    done
}

_lc_complete_rules() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Complete after -r flag
    if [[ "$prev" == "-r" ]]; then
        COMPREPLY=($(compgen -W "$(_lc_find_rules)" -- "$cur"))
        return
    fi

    # Complete positional arg for lc-set-rule
    if [[ "${COMP_WORDS[0]}" == "lc-set-rule" ]] && [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$(_lc_find_rules)" -- "$cur"))
        return
    fi
}

# Register for all lc-* commands that need rule completion
complete -F _lc_complete_rules lc-context
complete -F _lc_complete_rules lc-outlines
complete -F _lc_complete_rules lc-preview
complete -F _lc_complete_rules lc-set-rule
