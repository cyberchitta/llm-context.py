(struct_specifier
  name: (type_identifier) @name
  body: (field_declaration_list)) @definition.class

(union_specifier
  name: (type_identifier) @name
  body: (field_declaration_list)) @definition.class

(function_definition
  declarator: (function_declarator
    declarator: (identifier) @name)
  body: (compound_statement)) @definition.function

(function_definition
  declarator: (function_declarator
    declarator: (field_identifier) @name)
  body: (compound_statement)) @definition.method

(type_definition
  declarator: (type_identifier) @name) @definition.type

(enum_specifier
  name: (type_identifier) @name
  body: (enumerator_list)) @definition.type

(class_specifier
  name: (type_identifier) @name
  body: (field_declaration_list)) @definition.class