import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

def distill_code_architecture(source_code: str) -> str:
    """
    Parses Python code using Tree-sitter, queries functional entities, 
    and outputs a structured, human-readable architecture map.
    """
    # 1. Initialize the parser with the modern Python grammar bindings
    py_lang = Language(tspython.language())
    parser = Parser(py_lang)
    
    # 2. Convert source string to bytes and parse into an AST
    source_bytes = source_code.encode("utf-8")
    tree = parser.parse(source_bytes)
    
    # 3. Define the structural query matching patterns
    # We query classes, functions, and assignment blocks simultaneously
    query_text = """
    (class_definition
      name: (identifier) @class.name
      body: (block) @class.body) @class.def

    (function_definition
      name: (identifier) @func.name
      parameters: (parameters) @func.params
      body: (block) @func.body) @func.def

    (assignment
      left: (identifier) @assign.target
      right: (_) @assign.value) @assign.def
    """
    
    query = py_lang.query(query_text)
    captures = query.captures(tree.root_node)
    
    output_blocks = []
    
    # Track nodes we've already printed to avoid duplicate output from nested captures
    processed_nodes = set()
    
    # 4. Iterate through tree captures and build the target text structure
    for node, tag in captures:
        node_id = node.id
        if node_id in processed_nodes:
            continue
            
        if tag == "class.def":
            # Extract names and bodies using child fields directly for structural precision
            name_node = node.child_by_field_name("name")
            body_node = node.child_by_field_name("body")
            
            class_name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")
            class_body = source_bytes[body_node.start_byte:body_node.end_byte].decode("utf-8")
            
            block = [
                "[ENTITY: CLASS]",
                f"NAME: {class_name}",
                "BODY:",
                class_body.strip()
            ]
            output_blocks.append("\n".join(block))
            processed_nodes.add(node_id)
            
        elif tag == "func.def":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            body_node = node.child_by_field_name("body")
            
            func_name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")
            # Strip the structural outer parentheses off the parameter list string
            params = source_bytes[params_node.start_byte:params_node.end_byte].decode("utf-8").strip("()")
            func_body = source_bytes[body_node.start_byte:body_node.end_byte].decode("utf-8")
            
            block = [
                "[ENTITY: FUNCTION]",
                f"NAME: {func_name}",
                f"PARAMETERS: {params if params else 'None'}",
                "BODY:",
                func_body.strip()
            ]
            output_blocks.append("\n".join(block))
            processed_nodes.add(node_id)
            
        elif tag == "assign.def":
            target_node = node.child_by_field_name("left")
            value_node = node.child_by_field_name("right")
            
            # Ensure we have valid nodes before slicing bytes
            if target_node and value_node:
                target_name = source_bytes[target_node.start_byte:target_node.end_byte].decode("utf-8")
                value_content = source_bytes[value_node.start_byte:value_node.end_byte].decode("utf-8")
                
                block = [
                    "[ENTITY: ASSIGNMENT]",
                    f"TARGET: {target_name}",
                    f"VALUE_EXPRESSION: {value_content.strip()}"
                ]
                output_blocks.append("\n".join(block))
                processed_nodes.add(node_id)

    # Combine all structural blocks separated by clean line partitions
    return "\n\n" + "\n\n".join(output_blocks) + "\n"


# --- Local Verification Engine ---
if __name__ == "__main__":
    # Sample target python code to analyze
    target_python_script = """
class DataProcessor:
    def __init__(self, threshold):
        self.threshold = threshold

def greet(name):
    print(f"Hello, {name}!")

base_modifier = fetch_scalar_metric(config_id)
"""

    print("--- Distilling Target Code Architecture ---")
    result_structure = distill_code_architecture(target_python_script)
    print(result_structure)