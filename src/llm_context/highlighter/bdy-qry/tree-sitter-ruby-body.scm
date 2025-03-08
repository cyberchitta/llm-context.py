(method
  name: (identifier) @name
  body: (body_statement)) @definition.method

(singleton_method
  name: (identifier) @name
  body: (body_statement)) @definition.method

(class
  name: (constant) @name
  body: (body_statement)) @definition.class

(module
  name: (constant) @name
  body: (body_statement)) @definition.module