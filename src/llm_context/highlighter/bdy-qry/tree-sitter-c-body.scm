(struct_specifier name: (type_identifier) @name (field_declaration_list) @body) @definition.class
(union_specifier name: (type_identifier) @name (field_declaration_list) @body) @definition.class
(function_definition (function_declarator declarator: (identifier) @name) (compound_statement) @body) @definition.function
(type_definition declarator: (type_identifier) @name (type_descriptor) @body) @definition.type
(enum_specifier name: (type_identifier) @name (enumerator_list) @body) @definition.type