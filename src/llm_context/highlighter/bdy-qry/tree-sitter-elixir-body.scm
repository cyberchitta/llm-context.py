(call
  target: (identifier) @ignore
  (arguments (alias) @name)
  (do_block) @body) @definition.module
  (#any-of? @ignore "defmodule" "defprotocol")

(call
  target: (identifier) @ignore
  (arguments
    [
      (identifier) @name
      (call target: (identifier) @name)
      (binary_operator
        left: (call target: (identifier) @name)
        operator: "when")
    ])
  (_) @body) @definition.function
  (#any-of? @ignore "def" "defp" "defdelegate" "defguard" "defguardp" "defmacro" "defmacrop" "defn" "defnp")