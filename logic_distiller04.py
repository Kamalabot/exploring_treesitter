import sys
import tree_sitter_python as tspython
import tree_sitter_rust as tsrust
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QSplitter
)

class PolyglotDistillerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tree-sitter Polyglot Logic Distiller")
        self.resize(1200, 800)
        
        # 1. Initialize and cache language Grammars (Modern v0.22+ API)
        self.languages = {
            "Python": Language(tspython.language()),
            "Rust": Language(tsrust.language()),
            "JavaScript": Language(tsjavascript.language()),
            "Java": Language(tsjava.language())
        }
        
        # Initialize core runtime parser
        self.ts_parser = Parser()
        
        # 2. Define Language-Specific Node Mappings
        # Tracks structural identifiers across different language grammars
        self.language_maps = {
            "Python": {
                "function": ["function_definition"],
                "class": ["class_definition"],
                "assignment": ["assignment"],
                "name_field": "name",
                "param_field": "parameters",
                "body_field": "body"
            },
            "Rust": {
                "function": ["function_item"],
                "class": ["struct_item", "impl_item", "trait_item"],
                "assignment": ["let_declaration", "assignment_expression"],
                "name_field": "name",
                "param_field": "parameters",
                "body_field": "body"
            },
            "JavaScript": {
                "function": ["function_declaration", "arrow_function", "method_definition"],
                "class": ["class_declaration"],
                "assignment": ["variable_declarator", "assignment_expression"],
                "name_field": "name",
                "param_field": "parameters",
                "body_field": "body"
            },
            "Java": {
                "function": ["method_declaration", "constructor_declaration"],
                "class": ["class_declaration", "interface_declaration"],
                "assignment": ["variable_declarator", "assignment_expression"],
                "name_field": "name",
                "param_field": "parameters",
                "body_field": "body"
            }
        }
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        mono_font = QFont("Consolas", 10)

        # --- TOP PANEL: Configuration Toolbar ---
        toolbar_layout = QHBoxLayout()
        
        lang_label = QLabel("Select Target Language:")
        lang_label.setStyleSheet("font-weight: bold;")
        
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(list(self.languages.keys()))
        self.lang_selector.currentTextChanged.connect(self.handle_language_swap)
        
        toolbar_layout.addWidget(lang_label)
        toolbar_layout.addWidget(self.lang_selector)
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # Splitting Container view
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # --- LEFT PANEL: Input Section ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        input_label = QLabel("Source Code Target Input:")
        input_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        
        self.code_input = QPlainTextEdit()
        self.code_input.setFont(mono_font)
        
        self.parse_button = QPushButton("Parse Code Architecture")
        self.parse_button.setMinimumHeight(40)
        self.parse_button.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; border-radius: 4px;"
        )
        self.parse_button.clicked.connect(self.process_source_code)
        
        left_layout.addWidget(input_label)
        left_layout.addWidget(self.code_input)
        left_layout.addWidget(self.parse_button)
        main_splitter.addWidget(left_container)

        # --- RIGHT PANEL: Dual Viewports ---
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # AST Output Terminal View
        ast_container = QWidget()
        ast_layout = QVBoxLayout(ast_container)
        ast_layout.setContentsMargins(0, 0, 0, 0)
        ast_label = QLabel("Generated Concrete AST (S-expression View):")
        ast_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.ast_output = QPlainTextEdit()
        self.ast_output.setFont(mono_font)
        self.ast_output.setReadOnly(True)
        ast_layout.addWidget(ast_label)
        ast_layout.addWidget(self.ast_output)
        right_splitter.addWidget(ast_container)
        
        # Distilled Structures Log View
        struct_container = QWidget()
        struct_layout = QVBoxLayout(struct_container)
        struct_layout.setContentsMargins(0, 0, 0, 0)
        struct_label = QLabel("Distilled Structural Entity Output Profile:")
        struct_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.struct_output = QPlainTextEdit()
        self.struct_output.setFont(mono_font)
        self.struct_output.setReadOnly(True)
        struct_layout.addWidget(struct_label)
        struct_layout.addWidget(self.struct_output)
        right_splitter.addWidget(struct_container)
        
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([550, 550])
        
        # Trigger default view injection
        self.handle_language_swap(self.lang_selector.currentText())

    def handle_language_swap(self, selected_lang):
        """Loads a boilerplate code snippet when switching between interface languages."""
        samples = {
            "Python": "def greet(name):\n    print(f'Hello, {name}!')\n\nbase_modifier = 100",
            "Rust": "fn greet(name: &str) {\n    println!(\"Hello, {}!\", name);\n}\n\nlet base_modifier = 100;",
            "JavaScript": "function greet(name) {\n    console.log(`Hello, ${name}!`);\n}\n\nconst base_modifier = 100;",
            "Java": "public class Main {\n    public void greet(String name) {\n        System.out.println(\"Hello, \" + name);\n    }\n}"
        }
        self.code_input.setPlainText(samples.get(selected_lang, ""))
        self.process_source_code()

    def get_node_text(self, node, source_bytes: bytes) -> str:
        if not node:
            return "None"
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def format_sexp(self, sexp: str) -> str:
        indent = 0
        result = []
        for char in sexp:
            if char == '(':
                result.append('\n' + '  ' * indent + '(')
                indent += 1
            elif char == ')':
                indent -= 1
                result.append(')')
            else:
                result.append(char)
        return "".join(result).strip()

    def process_source_code(self):
        current_lang_name = self.lang_selector.currentText()
        lang_obj = self.languages[current_lang_name]
        lang_map = self.language_maps[current_lang_name]
        
        # Bind selected language grammar target into parser context
        self.ts_parser.language = lang_obj
        
        source_text = self.code_input.toPlainText() + "\n"
        source_bytes = source_text.encode("utf-8")
        
        tree = self.ts_parser.parse(source_bytes)
        self.ast_output.setPlainText(self.format_sexp(str(tree.root_node)))
        
        output_blocks = []
        
        # Generalized polyglot tree walker function
        def walk_tree(node):
            # Check for functions/methods match across language dialect configurations
            if node.type in lang_map["function"]:
                name_node = node.child_by_field_name(lang_map["name_field"])
                params_node = node.child_by_field_name(lang_map["param_field"])
                body_node = node.child_by_field_name(lang_map["body_field"])
                
                func_name = self.get_node_text(name_node, source_bytes)
                params_text = self.get_node_text(params_node, source_bytes).strip("()")
                body_text = self.get_node_text(body_node, source_bytes).strip()
                
                block = [
                    "[ENTITY: FUNCTION]",
                    f"NAME: {func_name}",
                    f"PARAMETERS: {params_text if params_text else 'None'}",
                    "BODY:",
                    body_text
                ]
                output_blocks.append("\n".join(block))
                
            # Check for classes/structs
            elif node.type in lang_map["class"]:
                name_node = node.child_by_field_name(lang_map["name_field"])
                body_node = node.child_by_field_name(lang_map["body_field"])
                
                class_name = self.get_node_text(name_node, source_bytes)
                body_text = self.get_node_text(body_node, source_bytes).strip()
                
                block = [
                    "[ENTITY: CLASS/STRUCT]",
                    f"NAME: {class_name}",
                    "BODY:",
                    body_text
                ]
                output_blocks.append("\n".join(block))
                
            # Check for assignments or variable initializations
            elif node.type in lang_map["assignment"]:
                # Polyglot variation handling for assignment architectures
                left_node = node.child_by_field_name("left") or node.child_by_field_name("name") or node.child_by_field_name("value")
                right_node = node.child_by_field_name("right") or node.child_by_field_name("value")
                
                # Alternate pattern mapping fallback if child nodes aren't found by explicit field names
                if not left_node and node.named_child_count >= 1:
                    left_node = node.named_child(0)
                if not right_node and node.named_child_count >= 2:
                    right_node = node.named_child(1)

                if left_node:
                    target_name = self.get_node_text(left_node, source_bytes)
                    value_expression = self.get_node_text(right_node, source_bytes).strip() if right_node else "Initialized"
                    
                    block = [
                        "[ENTITY: ASSIGNMENT/DECLARATION]",
                        f"TARGET: {target_name}",
                        f"VALUE_EXPRESSION: {value_expression}"
                    ]
                    output_blocks.append("\n".join(block))

            for child in node.children:
                walk_tree(child)

        walk_tree(tree.root_node)
        
        final_structure = "\n\n".join(output_blocks)
        self.struct_output.setPlainText(final_structure if final_structure else "No targeted entities matched in this profile.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PolyglotDistillerWindow()
    window.show()
    sys.exit(app.exec())