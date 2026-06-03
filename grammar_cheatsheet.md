# Tree-sitter Grammar DSL (grammar.js) Cheat Sheet

The `grammar.js` file exports a single function call to `grammar(options)` which defines the entire language structure using a JavaScript-based Domain Specific Language.

## Core Grammar Structure

```javascript
module.exports = grammar({
  name: 'my_language', // The name of the parser

  // Optional: Define whitespace and comments (defaults to standard whitespace)
  extras: $ => [
    /\s/,
    $.comment,
  ],

  // Optional: Resolve shift/reduce conflicts by specifying arrays of rules
  conflicts: $ => [
    [$._rule_a, $._rule_b]
  ],

  // Optional: Inline rules to improve the AST or performance
  inline: $ => [
    $._hidden_rule
  ],

  // Optional: Define an external scanner for complex tokens (like Python indentation)
  externals: $ => [
    $.indent,
    $.dedent,
  ],

  // Required: The actual syntax rules
  rules: {
    // The first rule is the root of the AST
    source_file: $ => repeat($.statement),
    
    // ... other rules
  }
});

```python
import urllib.request
import json
url = "https://raw.githubusercontent.com/tree-sitter/tree-sitter.github.io/master/docs/creating-parsers/2-the-grammar-dsl.md"
try:
    response = urllib.request.urlopen(url)
    print(response.read().decode('utf-8')[:2000])
except Exception as e:
    print("Error:", e)


```

```text
Error: <urlopen error [Errno -3] Temporary failure in name resolution>


```

```markdown
# Tree-sitter Grammar DSL (grammar.js) Cheat Sheet

The `grammar.js` file exports a single function call to `grammar(options)` which defines the entire language structure using a JavaScript-based Domain Specific Language.

## Core Grammar Structure

```javascript
module.exports = grammar({
  name: 'my_language', // The name of the parser

  // Optional: Define whitespace and comments (defaults to standard whitespace)
  extras: $ => [
    /\s/,
    $.comment,
  ],

  // Optional: Resolve shift/reduce conflicts by specifying arrays of rules
  conflicts: $ => [
    [$._rule_a, $._rule_b]
  ],

  // Optional: Inline rules to improve the AST or performance
  inline: $ => [
    $._hidden_rule
  ],

  // Optional: Define an external scanner for complex tokens (like Python indentation)
  externals: $ => [
    $.indent,
    $.dedent,
  ],

  // Required: The actual syntax rules
  rules: {
    // The first rule is the root of the AST
    source_file: $ => repeat($.statement),
    
    // ... other rules
  }
});

```

## Rule Combinators

Functions used inside the `rules` object to compose syntax patterns. The `$` parameter represents the grammar object, used to reference other rules (e.g., `$.expression`).

| Combinator | Description | Example |
| --- | --- | --- |
| `seq(rule1, rule2, ...)` | Matches rules in a specific sequence. | `seq('if', '(', $.expression, ')')` |
| `choice(rule1, rule2, ...)` | Matches any one of the provided rules. | `choice($.string, $.number)` |
| `repeat(rule)` | Matches zero or more occurrences of a rule. | `repeat($.statement)` |
| `repeat1(rule)` | Matches one or more occurrences of a rule. | `repeat1($.digit)` |
| `optional(rule)` | Matches zero or one occurrence of a rule. | `optional($.else_clause)` |
| `blank()` | Matches the empty string. | `blank()` |

## Terminals (Tokens)

Rules that match raw text.

| Syntax | Description | Example |
| --- | --- | --- |
| `"string"` | Matches an exact string literal. | `";"` or `"def"` |
| `/regex/` | Matches a regular expression. | `/[a-zA-Z_]\w*/` |
| `token(rule)` | Forces the enclosed rules to be treated as a single terminal token (no internal nodes). | `token(seq(/[1-9]/, repeat(/[0-9]/)))` |
| `token.immediate(rule)` | Matches a token only if there is no preceding whitespace. | `token.immediate('(')` |

## Tree Manipulation

Functions that change how the AST is structured and exposed.

| Function | Description | Example |
| --- | --- | --- |
| `field('name', rule)` | Assigns a field label to the matched child node for easy querying. | `field('operator', choice('+', '-'))` |
| `alias(rule, name)` | Renames a node in the output AST without changing parsing logic. | `alias($._binary_expr, $.expression)` |
| `$._rule_name` | Prefixing a rule name with `_` makes it **hidden** (anonymous). It guides parsing but won't appear in the final AST. | `_expression: $ => choice(...)` |

## Precedence and Associativity

Used to resolve ambiguities (like order of operations or the "dangling else" problem). Higher numbers bind tighter.

| Function | Description | Example |
| --- | --- | --- |
| `prec(number, rule)` | Assigns a numerical precedence to a rule. | `prec(1, seq($.expr, '*', $.expr))` |
| `prec.left([number], rule)` | Marks a rule as left-associative (e.g., `a - b - c`). | `prec.left(1, seq($.expr, '-', $.expr))` |
| `prec.right([number], rule)` | Marks a rule as right-associative (e.g., `a = b = c`). | `prec.right(1, seq($.var, '=', $.expr))` |
| `prec.dynamic(number, rule)` | Resolves conflicts at runtime (GLR parsing) based on the highest dynamic precedence when multiple parse paths succeed. | `prec.dynamic(1, $.complex_rule)` |

```

```