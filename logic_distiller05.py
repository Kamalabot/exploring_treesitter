import sys
import tree_sitter_python as tspython
import tree_sitter_rust as tsrust
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser, Query
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QLabel, QComboBox, QSplitter
)

class AdvancedPolyglotDistiller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Tree-sitter Explorer & Query Engine")
        self.resize(1300, 850)
        
        # Core Grammar Collections
        self.languages = {
            "Python": Language(tspython.language()),
            "Rust": Language(tsrust.language()),
            "JavaScript": Language(tsjavascript.language()),
            "Java": Language(tsjava.language())
        }
        self.ts_parser = Parser()
        self.current_tree = None
        
        # Track node click regions mapped to text strings: (start_byte, end_byte)
        self.node_coordinate_map = {}
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        mono_font = QFont("Consolas", 10)

        # --- TOP TOOLBAR ---
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Target Language:"))
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(list(self.languages.keys()))
        self.lang_selector.currentTextChanged.connect(self.handle_language_swap)
        toolbar.addWidget(self.lang_selector)
        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        # Horizontal Workspace Splitter
        workspace_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(workspace_splitter)

        # --- LEFT WORKSPACE: Input Code & Custom Query Editors ---
        left_workspace = QSplitter(Qt.Orientation.Vertical)
        
        # Source Code Area
        code_box = QWidget()
        code_layout = QVBoxLayout(code_box)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_layout.addWidget(QLabel("Source Code Target Input:"))
        self.code_input = QPlainTextEdit()
        self.code_input.setFont(mono_font)
        code_layout.addWidget(self.code_input)
        left_workspace.addWidget(code_box)
        
        # Custom S-Expression Query Area (Feature 1)
        query_box = QWidget()
        query_layout = QVBoxLayout(query_box)
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_layout.addWidget(QLabel("Live S-Expression DSL Query Selector:"))
        self.query_input = QPlainTextEdit()
        self.query_input.setFont(mono_font)
        self.query_input.setPlainText("(function_definition name: (identifier) @cap.name)")
        query_layout.addWidget(self.query_input)
        
        self.parse_button = QPushButton("Execute Advanced Tree Analysis")
        self.parse_button.setMinimumHeight(40)
        self.parse_button.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; border-radius: 4px;")
        self.parse_button.clicked.connect(self.process_source_code)
        query_layout.addWidget(self.parse_button)
        
        left_workspace.addWidget(query_box)
        workspace_splitter.addWidget(left_workspace)

        # --- RIGHT WORKSPACE: Interactive Output Terminals ---
        right_workspace = QSplitter(Qt.Orientation.Vertical)
        
        # AST S-Expression Viewport
        ast_box = QWidget()
        ast_layout = QVBoxLayout(ast_box)
        ast_layout.setContentsMargins(0, 0, 0, 0)
        ast_layout.addWidget(QLabel("Interactive Structural Layout Map:"))
        self.ast_output = QPlainTextEdit()
        self.ast_output.setFont(mono_font)
        self.ast_output.setReadOnly(True)
        ast_layout.addWidget(self.ast_output)
        right_workspace.addWidget(ast_box)
        
        # Execution Query Captures Panel & Diagnostics (Feature 5)
        captures_box = QWidget()
        captures_layout = QVBoxLayout(captures_box)
        captures_layout.setContentsMargins(0, 0, 0, 0)
        captures_layout.addWidget(QLabel("Query Captures & Compiler Diagnostic Logs:"))
        self.captures_output = QPlainTextEdit()
        self.captures_output.setFont(mono_font)
        self.captures_output.setReadOnly(True)
        captures_layout.addWidget(self.captures_output)
        right_workspace.addWidget(captures_box)
        
        workspace_splitter.addWidget(right_workspace)
        workspace_splitter.setSizes([600, 600])
        left_workspace.setSizes([500, 250])
        
        self.handle_language_swap(self.lang_selector.currentText())

    def handle_language_swap(self, selected_lang):
        samples = {
            "Python": "def greet(name):\n    print(f'Hello, {name}!')\n\ndef calculate(x):\n    return x * 2\n\nbase = broken_syntax[",
            "Rust": "fn greet(name: &str) {\n    println!(\"Hello, {}!\", name);\n}\n\nlet base_modifier = 100;",
            "JavaScript": "function greet(name) {\n    console.log(`Hello, ${name}!`);\n}",
            "Java": "public class Main {\n    public void greet(String name) {\n    }\n}"
        }
        queries = {
            "Python": "(function_definition name: (identifier) @cap.name)",
            "Rust": "(function_item name: (identifier) @cap.name)",
            "JavaScript": "(function_declaration name: (identifier) @cap.name)",
            "Java": "(method_declaration name: (identifier) @cap.name)"
        }
        self.code_input.setPlainText(samples.get(selected_lang, ""))
        self.query_input.setPlainText(queries.get(selected_lang, ""))
        self.process_source_code()

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
        lang_name = self.lang_selector.currentText()
        lang_obj = self.languages[lang_name]
        self.ts_parser.language = lang_obj
        
        source_text = self.code_input.toPlainText() + "\n"
        source_bytes = source_text.encode("utf-8")
        
        # 1. Parse active code block
        self.current_tree = self.ts_parser.parse(source_bytes)
        self.ast_output.setPlainText(self.format_sexp(str(self.current_tree.root_node)))
        
        log_outputs = []
        
        # 2. Scanning for Compilation Diagnostics (Feature 5)
        def scan_errors(node):
            if node.type == "ERROR" or node.is_missing:
                log_outputs.append(f"[SYNTAX DIAGNOSTIC] Found compilation error token range: Line {node.start_point[0] + 1}, Col {node.start_point[1]}")
            for child in node.children:
                scan_errors(child)
        scan_errors(self.current_tree.root_node)
        
        # 3. Dynamic DSL S-Expression Runtime Processing (Feature 1)
        query_text = self.query_input.toPlainText()
        if query_text.strip():
            try:
                # Compile matching query format using modern constructor bindings
                ts_query = Query(lang_obj, query_text)
                captures = ts_query.captures(self.current_tree.root_node)
                
                if captures:
                    log_outputs.append(f"\n=== Active Query Match Captures ({len(captures)}) ===")
                    for node, tag in captures:
                        captured_string = source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
                        log_outputs.append(f"-> Captured Tag [@{tag}]: '{captured_string}'")
                        log_outputs.append(f"   Position Coordinates: Bytes [{node.start_byte} - {node.end_byte}] | Rows {node.start_point} - {node.end_point}")
                else:
                    log_outputs.append("\n[QUERY INFO] Active query schema successfully evaluated but matched no targets.")
            except Exception as query_err:
                log_outputs.append(f"\n[QUERY COMPILER ERROR] Failed parsing DSL structural query rules:\n{str(query_err)}")

        self.captures_output.setPlainText("\n".join(log_outputs))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedPolyglotDistiller()
    window.show()
    sys.exit(app.exec())