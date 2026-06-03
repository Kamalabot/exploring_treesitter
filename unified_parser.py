import tree_sitter_python as tspython
import tree_sitter_rust as tsrust
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

def get_ast(source_code: bytes, lang_name: str):
    # 1. Select the correct language grammar instance
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

    # 2. Pass the language directly into the Parser constructor (v0.22+ API)
    parser = Parser(lang)

    # 3. Parse the code
    tree = parser.parse(source_code)
    return tree

# Example Usage
python_code = b"def greet(): print('Hello')"
tree = get_ast(python_code, "python")

# 4. Use str() instead of .sexp() to get the S-expression output (v0.22+ API)
print(str(tree.root_node))