(class_declaration
  name: (identifier) @name
  body: (declaration_list)) @definition.class

(interface_declaration
  name: (identifier) @name
  body: (declaration_list)) @definition.interface

(method_declaration
  name: (identifier) @name
  body: (block)) @definition.method

(namespace_declaration
  name: (identifier) @name
  body: (declaration_list)) @definition.module