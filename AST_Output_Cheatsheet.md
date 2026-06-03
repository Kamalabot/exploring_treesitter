# Tree-sitter AST & Grammar Cheat Sheet

## 1. Node Types & Structure
* **Named Nodes:** Explicit structural components of the code (e.g., `identifier`, `function_definition`, `block`). These represent the core logic.
* **Anonymous Nodes:** Literal keywords, operators, and punctuation (e.g., `"def"`, `"+"`, `":"`, `","`). These are strictly structural and often omitted from high-level analysis.
* **Fields:** Labels that define the relationship between a parent and a child node (e.g., `name:`, `parameters:`, `body:`). Fields make precise extraction easy.

## 2. Query Language Syntax (S-expressions)
Used to search and extract specific patterns from the AST.

* **Basic Match:** `(identifier)` -> Matches any identifier node.
* **Nested Match:** `(expression_statement (call))` -> Matches a call inside an expression statement.
* **Field Match:** `(function_definition name: (identifier))` -> Matches a function definition specifically targeting its `name` field.
* **Captures (`@`):** `(identifier) @target_name` -> Extracts the matched node and tags it as `target_name` in the results.
* **Wildcards (`_`):** `(call function: (_))` -> Matches any node acting as a function in a call expression.
* **Alternation (`[]`):** `[ (string) (integer) ]` -> Matches either a string or an integer node.
* **Quantifiers:**
  * `( ... )*` -> Zero or more occurrences.
  * `( ... )+` -> One or more occurrences.
  * `( ... )?` -> Optional (zero or one occurrence).
* **Predicates (Filtering):** `(#eq? @target_name "main")` -> Filters results to only match where the captured node text equals "main".

## 3. Grammar DSL Basics (`grammar.js`)
If you look into a language's `grammar.js` file, you will see these core functions used to build the syntax rules:

* `seq(a, b)`: A sequence that must appear in exact order (a then b).
* `choice(a, b)`: Matches either rule a or rule b.
* `repeat(rule)`: Matches the rule zero or more times.
* `repeat1(rule)`: Matches the rule one or more times.
* `optional(rule)`: The rule can appear zero or one time.
* `field("label", rule)`: Assigns a field label to the matched child node (this creates the `label:` you see in S-expressions).
* `token(regex)`: Defines a terminal token (leaf node) using regular expressions.

## 4. Core Python API Methods
When manipulating a parsed `Node` object in Python:

* **Identification:**
  * `node.type` -> Returns the string name of the node (e.g., `"identifier"`).
  * `node.is_named` -> Returns `True` if it is a named node (not a literal/operator).
* **Location:**
  * `node.start_byte` / `node.end_byte` -> Byte offsets in the source string.
  * `node.start_point` / `node.end_point` -> Tuple of `(row, column)` for line numbers.
  * `node.text` -> Returns the raw bytes of the code within this node.
* **Traversal:**
  * `node.parent` -> Gets the parent node.
  * `node.children` -> List of all child nodes (named and anonymous).
  * `node.named_children` -> List of only named child nodes.
  * `node.child_by_field_name('body')` -> Retrieves a specific child using its field label.
* **Cursor (Performance):**
  * `tree.walk()` -> Returns a `TreeCursor`. Use this for highly optimized, low-memory tree traversal (`cursor.goto_first_child()`, `cursor.goto_next_sibling()`).