import tree_sitter_python as tspython
from tree_sitter import Language, Parser

def get_node_text(node, source_bytes: bytes) -> str:
    """Helper to safely extract string text from a node's byte range."""
    if not node:
        return ""
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

def distill_code_architecture(source_code: str) -> str:
    """
    Arbitrarily parses Python source code using modern Tree-sitter APIs,
    recursively extracting functions, classes, and assignments into a structured log.
    """
    # 1. Initialize modern parser structure
    py_lang = Language(tspython.language())
    parser = Parser(py_lang)
    
    # 2. Parse source string as bytes
    source_bytes = source_code.encode("utf-8")
    tree = parser.parse(source_bytes)
    
    output_blocks = []
    
    # 3. Arbitrary Recursive Tree Walker
    def walk_tree(node):
        # Handle Functions
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            body_node = node.child_by_field_name("body")
            
            func_name = get_node_text(name_node, source_bytes)
            # Clean up parameters text striping outer parenthesis
            params_text = get_node_text(params_node, source_bytes).strip("()")
            body_text = get_node_text(body_node, source_bytes).strip()
            
            block = [
                "[ENTITY: FUNCTION]",
                f"NAME: {func_name}",
                f"PARAMETERS: {params_text if params_text else 'None'}",
                "BODY:",
                body_text
            ]
            output_blocks.append("\n".join(block))
            
        # Handle Classes
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            body_node = node.child_by_field_name("body")
            
            class_name = get_node_text(name_node, source_bytes)
            body_text = get_node_text(body_node, source_bytes).strip()
            
            block = [
                "[ENTITY: CLASS]",
                f"NAME: {class_name}",
                "BODY:",
                body_text
            ]
            output_blocks.append("\n".join(block))
            
        # Handle Variable Assignments
        elif node.type == "assignment":
            left_node = node.child_by_field_name("left")
            right_node = node.child_by_field_name("right")
            
            target_name = get_node_text(left_node, source_bytes)
            value_expression = get_node_text(right_node, source_bytes).strip()
            
            block = [
                "[ENTITY: ASSIGNMENT]",
                f"TARGET: {target_name}",
                f"VALUE_EXPRESSION: {value_expression}"
            ]
            output_blocks.append("\n".join(block))

        # Arbitrarily traverse all children deeper down the tree hierarchy
        for child in node.children:
            walk_tree(child)

    # Begin the arbitrary sweep from the root node
    walk_tree(tree.root_node)
    
    return "\n\n" + "\n\n".join(output_blocks) + "\n"


# --- Local Execution Verification ---
if __name__ == "__main__":
    # Test script with arbitrary complex nested items
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