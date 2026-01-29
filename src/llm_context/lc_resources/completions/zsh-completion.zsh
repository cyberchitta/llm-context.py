#compdef lc-context lc-outlines lc-preview lc-set-rule

_lc_find_rules() {
    local dir=$PWD
    while [[ $dir != "/" ]]; do
        if [[ -d "$dir/.llm-context/rules" ]]; then
            find "$dir/.llm-context/rules" -name '*.md' 2>/dev/null | \
                sed "s|$dir/.llm-context/rules/||" | \
                sed 's/\.md$//' | \
                grep 'prm'
            return
        fi
        dir=${dir:h}
    done
}

_lc_complete() {
    local -a rules
    rules=(${(f)"$(_lc_find_rules)"})

    _arguments \
        '-r[Use specified rule]:rule:($rules)' \
        '*::arg:->args'

    case $state in
        args)
            if [[ $words[1] == "lc-set-rule" ]]; then
                _arguments '1:rule:($rules)'
            fi
            ;;
    esac
}

_lc_complete "$@"
