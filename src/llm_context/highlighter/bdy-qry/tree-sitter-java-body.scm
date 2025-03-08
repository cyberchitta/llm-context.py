(class_declaration
  name: (identifier) @name
  body: (class_body)) @definition.class

(method_declaration
  name: (identifier) @name
  body: (block)) @definition.method

(interface_declaration
  name: (identifier) @name
  body: (interface_body)) @definition.interface