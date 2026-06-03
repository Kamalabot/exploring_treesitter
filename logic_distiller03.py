import sys
import tree_sitter_python as tspython
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
    QSplitter
)

class LogicDistillerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tree-sitter Code Logic Distiller")
        self.resize(1100, 700)
        
        # Initialize the Tree-sitter environment
        py_lang = Language(tspython.language())
        self.ts_parser = Parser(py_lang)
        
        self.init_ui()

    def init_ui(self):
        # Base container widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Monospace font configuration for code/data display
        mono_font = QFont("Consolas", 10)
        if sys.platform == "dark":  # fallback formatting
            mono_font.setStyleHint(QFont.StyleHint.Monospace)

        # Create interactive splitting view container
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # --- LEFT PANEL: Input Section ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        input_label = QLabel("Target Source Code Input:")
        input_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        self.code_input = QPlainTextEdit()
        self.code_input.setFont(mono_font)
        self.code_input.setPlaceholderText("# Paste your arbitrary target python code here...")
        # Populate initial default sample block
        self.code_input.setPlainText(
"class DataProcessor:\n"
"    def __init__(self, threshold):\n"
"        self.threshold = threshold\n\n"
"def greet(name):\n"
"    print(f'Hello, {name}!')\n\n"
"base_modifier = fetch_scalar_metric(config_id)"
        )
        
        self.parse_button = QPushButton("Parse Code Structure")
        self.parse_button.setMinimumHeight(40)
        self.parse_button.setStyleSheet(
            "background-color: #007acc; color: white; font-weight: bold; border-radius: 4px;"
        )
        self.parse_button.clicked.connect(self.process_target_source)
        
        left_layout.addWidget(input_label)
        left_layout.addWidget(self.code_input)
        left_layout.addWidget(self.parse_button)
        main_splitter.addWidget(left_container)

        # --- RIGHT PANEL: Dual Output Sections ---
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top Right: Raw S-expression View
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
        
        # Bottom Right: Custom Structured Entities View
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

        # Set initial layout proportions (50% left, 50% right)
        main_splitter.setSizes([550, 550])
        
        # Run an initial extraction scan on startup configuration
        self.process_target_source()

    def get_node_text(self, node, source_bytes: bytes) -> str:
        if not node:
            return ""
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def format_sexp(self, sexp: str) -> str:
        """Utility method to indent raw S-expressions for clean visual rendering."""
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

    def process_target_source(self):
        source_text = self.code_input.toPlainText() + "\n"
        source_bytes = source_text.encode("utf-8")
        
        # 1. Parse text into internal syntax tree
        tree = self.ts_parser.parse(source_bytes)
        
        # 2. Render pretty formatted S-expression representation
        pretty_ast = self.format_sexp(str(tree.root_node))
        self.ast_output.setPlainText(pretty_ast)
        
        # 3. Dynamic recursive block collection pass
        output_blocks = []
        
        def walk_tree(node):
            if node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                params_node = node.child_by_field_name("parameters")
                body_node = node.child_by_field_name("body")
                
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
                
            elif node.type == "class_definition":
                name_node = node.child_by_field_name("name")
                body_node = node.child_by_field_name("body")
                
                class_name = self.get_node_text(name_node, source_bytes)
                body_text = self.get_node_text(body_node, source_bytes).strip()
                
                block = [
                    "[ENTITY: CLASS]",
                    f"NAME: {class_name}",
                    "BODY:",
                    body_text
                ]
                output_blocks.append("\n".join(block))
                
            elif node.type == "assignment":
                left_node = node.child_by_field_name("left")
                right_node = node.child_by_field_name("right")
                
                target_name = self.get_node_text(left_node, source_bytes)
                value_expression = self.get_node_text(right_node, source_bytes).strip()
                
                block = [
                    "[ENTITY: ASSIGNMENT]",
                    f"TARGET: {target_name}",
                    f"VALUE_EXPRESSION: {value_expression}"
                ]
                output_blocks.append("\n".join(block))

            for child in node.children:
                walk_tree(child)

        # Traverse target configuration mapping from the tree root context
        walk_tree(tree.root_node)
        
        # Update output view field text
        final_structure = "\n\n".join(output_blocks)
        self.struct_output.setPlainText(final_structure if final_structure else "No targeted structural entities uncovered.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogicDistillerWindow()
    window.show()
    sys.exit(app.exec())