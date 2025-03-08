(struct_item name: (type_identifier) @name (field_declaration_list) @body) @definition.class
(enum_item name: (type_identifier) @name (enum_variant_list) @body) @definition.class
(union_item name: (type_identifier) @name (field_declaration_list) @body) @definition.class
(type_item name: (type_identifier) @name (_) @body) @definition.type
(function_item name: (identifier) @name (block) @body) @definition.function
(trait_item name: (type_identifier) @name (block) @body) @definition.interface
(mod_item name: (identifier) @name (block) @body) @definition.module