(method_definition
  name: (property_identifier) @name
  body: (statement_block)) @definition.method

(class_declaration
  name: (identifier) @name
  body: (class_body)) @definition.class

(function_declaration
  name: (identifier) @name
  body: (statement_block)) @definition.function