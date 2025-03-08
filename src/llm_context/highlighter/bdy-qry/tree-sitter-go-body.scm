(function_declaration
  name: (identifier) @name
  body: (block) @body) @definition.function

(method_declaration
  name: (field_identifier) @name
  body: (block) @body) @definition.method

(type_spec
  name: (type_identifier) @name
  type: (struct_type
    (field_declaration_list) @body)) @definition.type

(type_spec
  name: (type_identifier) @name
  type: (interface_type) @body) @definition.type