(function_declaration name: (identifier) @name body: (statement_block) @body) @definition.function
(method_definition name: (property_identifier) @name body: (statement_block) @body) @definition.method
(class_declaration name: (identifier) @name body: (class_body) @body) @definition.class
(interface_declaration name: (identifier) @name body: (object_type) @body) @definition.interface
(type alias_declaration name: (identifier) @name type: (type) @body) @definition.type
(enum_declaration name: (identifier) @name body: (enum_body) @body) @definition.enum