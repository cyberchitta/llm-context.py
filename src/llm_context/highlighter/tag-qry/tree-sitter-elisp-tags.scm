;; defun/defsubst
(function_definition name: (symbol) @name) @definition.function

;; Treat macros as function definitions for the sake of TAGS.
(macro_definition name: (symbol) @name) @definition.function

;; Match function calls
(list (symbol) @name) @reference.function
