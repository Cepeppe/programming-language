# SPL Grammar (EBNF-style)

This document describes the grammar of SPL using an EBNF-style notation.
Lexical structure is given informally; the grammar focuses on syntax.

---

## 1. Lexical structure (informal)

```ebnf
letter        = "A".."Z" | "a".."z" | "_" ;
digit         = "0".."9" ;

identifier    = letter , { letter | digit } ;

number_lit    = digit , { digit } , [ "." , digit , { digit } ] ;

string_lit    = '"' , { string_char } , '"' ;
string_char   = /* any char except " and newline, or escape */ ;
escape_seq    = "\" , ( '"' | "\" | "n" | "t" ) ;

bool_lit      = "true" | "false" ;

EOL           = /* end-of-line token (newline) */ ;
EOF           = /* end-of-file token */ ;
```

**Keywords (reserved words):**

```text
var, const, func, if, else, loop, import,
number, string, bool,
true, false,
and, or, not
```

**Operators and punctuation:**

```text
+  -  *  /  %  #  ^
== != < <= > >= =
( ) { } , ;
```

---

## 2. Program and top level

```ebnf
program       = { top_level } EOF ;

top_level     = func_decl | statement ;
```

The entry point is the executed file. Top-level statements are executed from top to bottom.

---

## 3. Declarations and statements

```ebnf
statement     = var_decl
              | const_decl
              | if_stmt
              | loop_stmt
              | import_stmt
              | expr_or_assign_stmt
              ;

line_end      = ";" | EOL ;
```

### 3.1 Variable and constant declarations

```ebnf
var_decl      = "var" , type_spec , identifier ,
                [ "=" , expression ] , line_end ;

const_decl    = "const" , type_spec , identifier ,
                "=" , expression , line_end ;

type_spec     = "number" | "string" | "bool" ;
```

### 3.2 Import

```ebnf
import_stmt   = "import" , string_lit , line_end ;
```

Each file is imported at most once.

### 3.3 If / else if / else

```ebnf
if_stmt       = "if" , "(" , expression , ")" , block ,
                { "else" , "if" , "(" , expression , ")" , block } ,
                [ "else" , block ] ;
```

### 3.4 Loop

```ebnf
loop_stmt     = "loop" , "(" , expression , ")" , block ;
```

### 3.5 Block

```ebnf
block         = "{" , { statement } , "}" ;
```

### 3.6 Expression or assignment statement

```ebnf
expr_or_assign_stmt
             = ( assignment | expression ) , line_end ;

assignment    = identifier , "=" , expression ;
```

Assignments assign to previously declared variables.

---

## 4. Function declarations and calls

```ebnf
func_decl     = "func" , identifier ,
                "(" , [ param_list ] , ")" ,
                block ;

param_list    = param , { "," , param } ;

param         = type_spec , identifier ;
```

Functions can only be declared at top level.

### 4.1 Function calls

```ebnf
call_expr     = primary , "(" ,
                [ arg_list ] ,
                ")" ;

arg_list      = expression , { "," , expression } ;
```

In practice, calls are parsed as a postfix on primary expressions.

---

## 5. Expressions and operator precedence

```ebnf
expression    = or_expr ;
```

Precedence from lowest to highest:

1. `or`
2. `and`
3. `== !=`
4. `< <= > >=`
5. `+ -`
6. `* / %`
7. unary `not`, unary `-`
8. `#`
9. `^`
10. primary / call

### 5.1 Layered non-terminals

```ebnf
or_expr       = and_expr , { "or" , and_expr } ;

and_expr      = equality_expr , { "and" , equality_expr } ;

equality_expr = relational_expr ,
                { ( "==" | "!=" ) , relational_expr } ;

relational_expr
             = add_expr ,
               { ( "<" | "<=" | ">" | ">=" ) , add_expr } ;

add_expr      = mul_expr ,
                { ( "+" | "-" ) , mul_expr } ;

mul_expr      = unary_expr ,
                { ( "*" | "/" | "%" ) , unary_expr } ;

unary_expr    = ( "not" | "-" ) , unary_expr
              | concat_expr ;

concat_expr   = power_expr , { "#" , power_expr } ;

power_expr    = primary ,
                [ "^" , unary_expr ] ;
```

- All binary operators except `^` are left-associative.
- `^` is right-associative.
- Unary operators (`not`, unary `-`) are prefix.

---

## 6. Primary expressions

```ebnf
primary       = literal
              | identifier
              | grouped
              | call ;

literal       = number_lit
              | string_lit
              | bool_lit ;

grouped       = "(" , expression , ")" ;

call          = identifier , "(" ,
                [ arg_list ] ,
                ")" ;
```

In a typical implementation, `primary` is parsed first and then possible call postfixes `(...)` are parsed in a loop.

---

## 7. Semantic notes (informal, not in grammar)

The grammar does not encode these rules, but the implementation must enforce:

- **Scope and variables**
  - Block scope for variables.
  - A variable declared in an outer block is visible in inner blocks.
  - A variable declared in an inner block is not visible outside it.
  - Redeclaring a variable name that exists in an enclosing scope is a compile-time error.
  - Using a variable before its declaration is a compile-time error.
  - Each uninitialized variable assumes a default value: `0`, `""`, or `false`.

- **Functions**
  - Functions are only allowed at top level.
  - A function that does not execute a `return` statement does not return a value.
  - Using the result of such a function in an expression is a compile-time error.

- **Types and operators**
  - Arithmetic operators (`+`, `-`, `*`, `/`, `%`, `^`) operate only on `number`.
  - Logical operators (`and`, `or`, `not`) operate only on `bool`.
  - Comparison operators (`<`, `<=`, `>`, `>=`) operate on `number` or `string`, with operands of the same type.
  - `==` and `!=` operate on `number`, `string`, or `bool` with operands of the same type.
  - `#` concatenates strings and requires both operands to be `string`.
  - String comparisons use lexicographical, case-sensitive order.

- **Control flow**
  - Conditions in `if` and `loop` must be boolean expressions.

- **Imports**
  - `import "file.spl"` reads and interprets the file as if pasted at that position.
  - Each file is imported at most once.

- **Errors**
  - Any type mismatch or casting/parsing error is a runtime error and aborts program execution.
