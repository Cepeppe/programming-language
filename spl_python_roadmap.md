# Roadmap for Implementing the SPL Interpreter in Python

This document outlines the main steps and considerations for implementing the SPL language in Python. The tone is intentionally impersonal and focused on the technical workflow.

---

## 1. Project structure and tooling

1. Choose a simple project layout, for example:

   ```text
   spl/
     __init__.py
     lexer.py
     tokens.py
     parser.py
     ast_nodes.py
     semantics.py   # optional separate semantic checks
     interpreter.py
     builtins.py
     errors.py
   main.py
   ```

2. Use a virtual environment and pin dependencies if any (e.g. `pytest` for tests, `mypy` for type hints).

3. Decide early whether the implementation will be:
   - a single-pass interpreter (parse + execute on the fly), or
   - a multi-phase pipeline (parse to AST, then analyze, then interpret).

   For this language, using an explicit AST with a separate interpreter phase is recommended, because it simplifies testing and future extensions.

---

## 2. Lexical analysis (lexer / tokenizer)

The lexer converts raw source text into a sequence of tokens.

1. Define the token kinds in `tokens.py`, for example as an `Enum` or simple constants:
   - Identifiers: `IDENT`
   - Literals: `NUMBER`, `STRING`, `BOOL_LITERAL`
   - Keywords: `VAR`, `CONST`, `FUNC`, `IF`, `ELSE`, `LOOP`, `IMPORT`, `TRUE`, `FALSE`, `AND`, `OR`, `NOT`
   - Type names: `TYPE_NUMBER`, `TYPE_STRING`, `TYPE_BOOL` (or treat them as keywords)
   - Operators: `PLUS`, `MINUS`, `STAR`, `SLASH`, `PERCENT`, `CARET`, `HASH`, `EQUAL_EQUAL`, `BANG_EQUAL`, `LESS`, `LESS_EQUAL`, `GREATER`, `GREATER_EQUAL`, `EQUAL`
   - Punctuation: `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `COMMA`
   - Line terminators: `EOL` (used as statement terminator)
   - Special: `EOF`

2. Implement the lexer in `lexer.py`:
   - Iterate over characters with current index and track `line` and `column` positions.
   - Skip whitespace except newlines. Each newline should emit an `EOL` token.
   - Implement `//` comments: from `//` up to, but not including, the newline.
   - Recognize number literals:
     - Digits with optional fractional part (e.g. `42`, `3.14`).
     - Do not include the sign; unary `-` is handled in the parser as an operator.
   - Recognize string literals:
     - Start and end with `"`. 
     - Support the escape sequences `"`, `\`, `
`, `	`.
     - Disallow newlines inside string literals.
   - Recognize identifiers and keywords:
     - Identifiers start with letter or `_`, followed by letters, digits, or `_`.
     - Map specific strings to keywords and type names based on the language spec.
   - Emit `EOF` at the end of input.

3. Add basic lexer tests to ensure handling of:
   - comments,
   - numeric and string literals,
   - keywords vs identifiers,
   - EOL tokens.

---

## 3. Abstract Syntax Tree (AST) design

Define AST node classes in `ast_nodes.py` using Python `dataclasses` for clarity. Suggested node types include:

- Program and top-level:
  - `Program(declarations_and_statements: list[Node])`

- Declarations:
  - `VarDecl(type, name, initializer)`
  - `ConstDecl(type, name, initializer)`
  - `FuncDecl(name, params, param_types, body)`

- Statements:
  - `Block(statements)`
  - `IfStmt(condition, then_branch, elif_branches, else_branch)`
  - `LoopStmt(condition, body)`
  - `ExprStmt(expression)`
  - `AssignStmt(name, expression)`
  - `ImportStmt(filename)`

- Expressions:
  - `BinaryExpr(left, operator, right)`
  - `UnaryExpr(operator, operand)`
  - `LiteralNumber(value)`
  - `LiteralString(value)`
  - `LiteralBool(value)`
  - `VariableExpr(name)`
  - `CallExpr(callee, arguments)`

The exact set of node types can be adjusted during implementation as needed.

---

## 4. Parsing (syntax analysis)

Use a recursive-descent parser in `parser.py`, driven by the grammar.

1. Implement a `Parser` class with methods like:
   - `parse_program()`
   - `parse_top_level()`
   - `parse_statement()`
   - `parse_block()`
   - `parse_declaration()`
   - `parse_expression()` and sub-levels for operator precedence.

2. Respect statement termination:
   - After parsing a statement, require either `EOL` or `;`.
   - Allow multiple statements on the same line separated by `;` by looping until no more `;` before EOL.

3. Implement non-terminals following the precedence structure:
   - `expression` → `or_expr`
   - `or_expr` → `and_expr ("or" and_expr)*`
   - `and_expr` → `equality_expr ("and" equality_expr)*`
   - `equality_expr` → `relational_expr (("==" | "!=") relational_expr)*`
   - `relational_expr` → `add_expr (("<" | "<=" | ">" | ">=") add_expr)*`
   - `add_expr` → `mul_expr (("+" | "-") mul_expr)*`
   - `mul_expr` → `unary_expr (("*" | "/" | "%") unary_expr)*`
   - `unary_expr` → `("not" | "-") unary_expr | concat_expr`
   - `concat_expr` → `power_expr ("#" power_expr)*`
   - `power_expr` → `primary_expr ("^" unary_expr)?` (or use right recursion for left operand)

4. Implement primary expressions:
   - literals (`NUMBER`, `STRING`, `TRUE`, `FALSE`),
   - variables (`IDENT`),
   - grouped expressions `( expression )`,
   - function calls: after an `IDENT` or other callable expression, if `(` is found, parse argument list.

5. Implement declarations and statements according to the spec:
   - `var` and `const` declarations with type:
     - `var number a = expression`
     - `const number pi = expression`
   - `func` declarations at top level only.
   - `if` / `else if` / `else` with boolean expressions.
   - `loop(expression) { ... }`.
   - `import "file.spl"`.

6. Implement descriptive parse errors including file name, line, and column.

---

## 5. Semantic checks (optional separate phase)

A separate semantic analysis step in `semantics.py` is recommended, although some checks can also be integrated in the interpreter.

Key checks include:

1. Scope and symbol tables:
   - Maintain symbol tables for each block scope.
   - Ensure variables and constants follow the rules:
     - no redefinition in inner scopes if the name already exists in an outer scope,
     - no use before declaration,
     - block-scope visibility rules.

2. Function declarations:
   - Enforce that functions are only declared at top level.
   - Check that parameter types are valid (`number`, `string`, `bool`).
   - Optionally ensure consistency of `return` statements within a function.

3. Type checking for expressions:
   - Verify operator operand types match the specification:
     - arithmetic operators only on `number`,
     - boolean operators only on `bool`,
     - comparison operators on equal types (`number` or `string`),
     - `#` only on `string` operands,
     - function arguments matching parameter types.
   - Ensure that expressions in `if` and `loop` are boolean.

4. Imports:
   - Maintain a registry of imported files to enforce “each file is imported at most once”.
   - Optionally detect cycles or report them clearly.

Semantic errors should include the source position and a clear message.

---

## 6. Runtime representation and environment model

Implement the interpreter in `interpreter.py` using an environment model.

1. Represent SPL values:
   - Map `number` to Python `float` or `Decimal`.
   - Map `string` to Python `str`.
   - Map `bool` to Python `bool`.
   - Optionally wrap them in small classes if stricter type control is desired.

2. Implement environments:
   - Use a stack of environment frames or a linked `Environment` class with `parent` reference.
   - Each frame is a mapping from variable name to value, plus metadata for constants.
   - Enforce constant non-reassignment at runtime.

3. Execution of statements:
   - `Program`: execute top-level statements in order.
   - `Block`: create a new environment frame linked to the parent; execute statements; discard frame.
   - `VarDecl` / `ConstDecl`: allocate a variable or constant in the current environment, set it to its default value or initializer.
   - `AssignStmt`: evaluate expression and store result in an existing variable (checking constants).
   - `IfStmt`, `LoopStmt`: evaluate conditions and execute branches according to the specification.
   - `ImportStmt`: load, parse, and execute another file if it has not been imported yet.

4. Execution of expressions:
   - Evaluate recursively according to operator semantics and precedence.
   - Implement binary and unary operators in a central place, including runtime type checks.
   - Implement function calls by:
     - resolving the callee (user-defined or built-in),
     - creating a new environment for parameters,
     - executing the function body until `return` is encountered or the end is reached.

5. Represent `return`:
   - Use a dedicated exception or a special object to unwind the call stack when encountering a `return` statement.

---

## 7. Import system

Implement imports in a way consistent with the specification:

1. Maintain a global or interpreter-level set/dictionary of imported file paths.

2. When executing an `ImportStmt("file.spl")`:
   - Resolve the path (relative to the current file or a search path).
   - If already imported, do nothing.
   - Otherwise:
     - read the file source,
     - lex and parse it into an AST,
     - optionally run semantic checks,
     - execute its top-level declarations and statements in the same global environment as the main file.

3. Ensure that errors in imported files include the correct file names and positions.

---

## 8. Built-in functions and casting

Implement built-ins in `builtins.py` and register them in the global environment before executing the program.

1. Define Python functions or classes to represent built-ins:

   - `exit(code: number)`: terminate execution with a given exit code (use `SystemExit` or a custom exception).
   - `echo(expr)`: convert `expr` to string using SPL `string()` semantics, then print.
   - `strlen(s: string) -> number`: return the length of the string.

2. Casting functions:
   - `string(x)`:
     - convert SPL values (`number`, `bool`, `string`) to string according to consistent rules.
   - `number(x)`:
     - parse a `string` as a decimal number or raise a runtime parsing error.
   - `bool(x: string)`:
     - accept only `"true"` or `"false"` (case-insensitive) and return the corresponding boolean,
     - raise a boolean parsing error for any other string,
     - receive non-string arguments as a static type error or runtime type error as per the specification.

3. Expose these built-ins in the initial global environment as if they were normal SPL functions.

---

## 9. Error handling and reporting

Introduce a small hierarchy of exception classes in `errors.py`, for example:

- `LexError`
- `ParseError`
- `SemanticError`
- `RuntimeError`
- `TypeError` (can be a subtype of `RuntimeError` or separate)

Each error should carry:

- file name,
- line and column,
- an explanatory message.

The top-level `main.py` should catch errors, display a human-readable message, and set an appropriate exit code.

---

## 10. Testing strategy

1. Unit tests for each layer:
   - Lexer tests for tokenization, comments, literals, and EOL handling.
   - Parser tests on small snippets, especially operator precedence and error cases.
   - Semantic tests (if implemented separately) for scope, shadowing rules, and type errors.
   - Interpreter tests for expression evaluation, control flow, functions, imports, and built-ins.

2. End-to-end tests:
   - Prepare small `.spl` programs that exercise:
     - arithmetic and boolean expressions,
     - variables and constants,
     - `if` / `loop` constructs,
     - user-defined functions,
     - imports,
     - built-in functions and casting.

3. Automate tests using `pytest` to allow fast iteration while evolving the language and interpreter.

---

## 11. Possible future extensions

Once the basic interpreter is stable, possible extensions include:

1. Adding new data types (arrays, maps).
2. Introducing a module system with explicit exported symbols instead of simple textual imports.
3. Adding a proper static type checker (separate from runtime interpreter).
4. Compiling to bytecode and implementing a virtual machine for better performance.
5. Improving diagnostics with richer error messages and hints.

These extensions can be layered on top of the current design if the AST and interpreter are kept modular and well-tested.
