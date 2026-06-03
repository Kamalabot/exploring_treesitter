import tree_sitter_python as tspython
import tree_sitter_rust as tsrust
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

def get_ast(source_code: bytes, lang_name: str):
    # 1. Select the correct language grammar
    if lang_name == "python":
        lang = Language(tspython.language())
    elif lang_name == "rust":
        lang = Language(tsrust.language())
    elif lang_name == "javascript":
        lang = Language(tsjavascript.language())
    elif lang_name == "java":
        lang = Language(tsjava.language())
    else:
        raise ValueError("Unsupported language")

    # 2. Initialize and set language
    parser = Parser()
    parser.set_language(lang)

    # 3. Parse the code
    tree = parser.parse(source_code)
    return tree

# Example Usage
python_code = b"def greet(): print('Hello')"
tree = get_ast(python_code, "python")
print(tree.root_node.sexp())