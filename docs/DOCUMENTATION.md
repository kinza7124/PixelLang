# PixelLang — Complete Technical Documentation

**Version:** 2.0  
**Date:** May 2026  
**Language:** PixelLang Compiler & DSL  
**Author:** Kinza

---

## Table of Contents

1. [Software Requirements Specification (SRS)](#srs)
2. [System Overview](#overview)
3. [Compiler Architecture](#architecture)
4. [Lexical Analysis (Lexer)](#lexer)
5. [Syntax Analysis (Parser)](#parser)
6. [Semantic Analysis](#semantic)
7. [Code Generation](#codegen)
8. [AST Optimization](#optimization)
9. [Viva Questions & Answers](#viva)

---

## 1. Software Requirements Specification (SRS) — IEEE Format

### 1.1 Introduction

#### 1.1.1 Purpose
PixelLang is a domain-specific language (DSL) designed for creating pixel art images programmatically. The compiler translates `.px` source files into PNG images through a four-phase pipeline: lexical analysis, syntax analysis, semantic analysis, and code generation. This document specifies all technical requirements for implementing and understanding the compiler.

#### 1.1.2 Scope
The PixelLang compiler targets:
- **Input:** Text files containing PixelLang source code (`.px`)
- **Output:** PNG images (using Pillow/PIL)
- **Phases:** Lexing → Parsing → Semantic Analysis → Code Generation → AST Optimization
- **Supported Commands:** 30+ drawing and transformation statements
- **Canvas Size:** User-defined (1 to 4096 pixels in each dimension)

#### 1.1.3 Definitions
- **Lexeme:** The raw text from source code (e.g., "CANVAS", "32", "#FF0000")
- **Token:** A structured representation of a lexeme with type, value, line, and column
- **AST (Abstract Syntax Tree):** A tree representation of the program structure, omitting syntax details
- **Symbol Table:** A data structure mapping variable and canvas names to their values and types
- **Scope:** A context level (global = 0, loop = 1, nested loop = 2, etc.)

### 1.2 Overall Description

#### 1.2.1 System Context
```
┌─────────────────┐
│   Source File   │
│    (*.px)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Lexer       │  Phase 1: Tokenize
├─────────────────┤
│ - DFA-based     │
│ - 30+ keywords  │
│ - Colors, nums  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Parser      │  Phase 2: Parse
├─────────────────┤
│ - LL(1) grammar │
│ - Recursive desc│
│ - Builds AST    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Semantic     │  Phase 3: Analyze
│    Analyzer     ├────────SymbolTable
├─────────────────┤
│ - 37 rules      │
│ - Bounds checks │
│ - Type checking │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Optimizer    │  Phase 3.5: Optimize
├─────────────────┤
│ - Transform     │
│   folding       │
│ - DCE           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Code Generator │  Phase 4: Generate
├─────────────────┤
│ - PIL/Pillow    │
│ - Render shapes │
│ - Output PNG    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Output PNG    │
│    Image File   │
└─────────────────┘
```

#### 1.2.2 Key Features
| Feature | Description |
|---------|-------------|
| **Keywords** | 30+ reserved words (CANVAS, PIXEL, LOOP, TRANSLATE, ROTATE, etc.) |
| **Data Types** | INT (numbers), COLOR (#RRGGBB), TUPLE (canvas dimensions) |
| **Variables** | Limited support: VAR and SET (not yet used in code generation) |
| **Control Flow** | LOOP with automatic scope management |
| **Error Handling** | 37 semantic rules, comprehensive error messages with line/col info |
| **Optimization** | Dead code elimination, transform chain folding, no-op removal |

### 1.3 Specific Requirements

#### 1.3.1 Functional Requirements

**FR1: Lexical Analysis**
- Recognize and tokenize all 30+ keywords
- Recognize numbers (integers) and colors (#RRGGBB hex format)
- Skip comments (// and /* */)
- Provide accurate line and column information for errors
- Emit EOF token when input ends

**FR2: Syntax Analysis**
- Implement LL(1) recursive descent parser
- Parse all 30+ statement types
- Detect missing semicolons, unmatched braces, unexpected tokens
- Build valid AST even with partial input recovery

**FR3: Semantic Analysis**
- Enforce SEM-01 to SEM-37 rules (CANVAS first, bounds checking, etc.)
- Maintain a symbol table with stack-based scopes
- Validate loop counts, rotation angles, scale factors
- Accumulate all errors before reporting (don't stop at first error)

**FR4: Code Generation**
- Produce valid 24-bit RGB PNG images using Pillow
- Handle transformations: TRANSLATE, ROTATE, SCALE, MIRROR
- Draw all shape types: PIXEL, RECT, CIRCLE, ELLIPSE, POLYGON, TRIANGLE, ARC, etc.
- Apply flood fill (FILL) using iterative BFS algorithm

**FR5: Optimization**
- Coalesce consecutive TRANSLATE, ROTATE, SCALE statements
- Remove no-op transforms (TRANSLATE 0 0, ROTATE 0, SCALE 1)
- Eliminate dead VAR and SET statements
- Recursively optimize LOOP bodies

#### 1.3.2 Non-Functional Requirements

| Requirement | Details |
|-------------|---------|
| **Performance** | Compile small programs (<1000 lines) in <1 second |
| **Memory** | Canvas size limited by available RAM (typically 4096×4096 max) |
| **Correctness** | 100% semantic rule coverage with no false negatives |
| **Maintainability** | Clear separation of phases; visitor pattern for AST traversal |
| **Documentation** | Full API documentation + examples for each feature |

### 1.4 Design Constraints
- **Language:** Python 3.9+
- **Image Library:** PIL/Pillow (must support 24-bit RGB)
- **Parser Type:** LL(1) recursive descent (no backtracking)
- **Scope Model:** Stack-based (lexical scoping)
- **Error Reporting:** Collect all errors, not just first error

---

## 2. System Overview

### 2.1 Architecture Principles

**Separation of Concerns:**
- **Lexer** only tokenizes; knows nothing about syntax
- **Parser** only builds AST; knows nothing about validity
- **Semantic Analyzer** checks rules; never draws
- **Code Generator** only draws; never checks rules
- **Optimizer** only transforms AST; never generates code

**Visitor Pattern:**
Each AST traversal phase (semantic analysis, code generation, optimization) is a separate `NodeVisitor` subclass. This allows independent evolution of each phase.

### 2.2 Compiler Invocation

```python
from compiler import compile_source, compile_file, pretty_print

# Compile from string
image, errors = compile_source(source_code)
if errors:
    for err in errors:
        print(f"Error: {err}")
else:
    image.save("output.png")

# Pretty-print AST for debugging
from compiler import lex, parse, optimize
ast = parse(lex(source_code))
print("Before optimization:")
print(pretty_print(ast))

optimized = optimize(ast)
print("\nAfter optimization:")
print(pretty_print(optimized))
```

---

## 3. Compiler Architecture

### 3.1 Module Structure

```
compiler/
├── __init__.py           # Public API (compile_source, compile_file, etc.)
├── lexer.py             # Tokenization (DFA-based)
├── tokens.py            # TokenType enum + Token class
├── parser.py            # LL(1) recursive descent parser
├── ast_nodes.py         # AST node classes + visitor pattern
├── ast_printer.py       # Pretty-printer for debugging
├── semantic.py          # Semantic analyzer (37 rules)
├── symbol_table.py      # Stack-based scope management
├── optimizer.py         # AST optimization passes
├── codegen.py           # Code generation (PIL-based)
├── errors.py            # Error classes
└── gui/                 # Optional GUI components
    ├── app.py
    └── __init__.py
```

### 3.2 Data Flow

```
source_code (string)
    ↓ [Lexer.tokenize()]
tokens (list of Token objects)
    ↓ [Parser.parse()]
ast (ProgramNode with child nodes)
    ↓ [SemanticAnalyzer.analyze()]
errors (list of SemanticError) + symbol_table
    ↓ (if no errors, continue)
    ↓ [Optimizer.optimize()]
optimized_ast
    ↓ [CodeGenerator.generate()]
image (PIL.Image)
```

---

## 4. Lexical Analysis (Lexer)

### 4.1 Overview

The lexer reads source code character-by-character and produces a stream of tokens. It uses a **Deterministic Finite Automaton (DFA)** to recognize:
- Keywords (30+)
- Numbers (integers)
- Colors (#RRGGBB)
- Strings (quoted text)
- Identifiers (variable names)
- Punctuation ({, }, ;)
- Comments (// and /* */)

### 4.2 DFA Design

A DFA is a state machine with:
- **States:** Represent the position in recognizing a token
- **Transitions:** Rules for moving between states based on input characters
- **Accepting States:** Emit a token when reached

#### 4.2.1 DFA for Numbers

```
State Diagram:

    [start]
       |
       | [0-9]
       ↓
    [reading digits] ⟵ [0-9]
       |
       | [non-digit]
       ↓
    [accept] → emit NUMBER token
```

**Example Trace: "321"**
```
Char '3': start → reading_digits
Char '2': reading_digits → reading_digits
Char '1': reading_digits → reading_digits
Char ';': reading_digits → [accept]
Emit: Token(NUMBER, "321", line=1, col=1)
```

#### 4.2.2 DFA for Colors

```
State Diagram:

    [start]
       |
       | [#]
       ↓
    [seen #]
       |
       | [0-9A-Fa-f]
       ↓
    [hex_1] → [hex_2] → [hex_3] → [hex_4] → [hex_5] → [hex_6]
       ↓
    [accept] → emit COLOR token
```

**Example Trace: "#FF00AA"**
```
Char '#': start → seen_hash
Char 'F': seen_hash → hex_1
Char 'F': hex_1 → hex_2
Char '0': hex_2 → hex_3
Char '0': hex_3 → hex_4
Char 'A': hex_4 → hex_5
Char 'A': hex_5 → hex_6
Char ';': hex_6 → [accept]
Emit: Token(COLOR, "#FF00AA", line=1, col=1)
Valid: Matches [0-9A-Fa-f]{6}
```

#### 4.2.3 DFA for Keywords/Identifiers

```
State Diagram:

    [start]
       |
       | [a-zA-Z_]
       ↓
    [reading word] ⟵ [a-zA-Z0-9_]
       |
       | [non-alnum]
       ↓
    [accept]
       |
       ↓ lookup RESERVED_WORDS dict
       |
    ├─ If found → emit KEYWORD token (e.g., CANVAS)
    └─ If not found → emit IDENT token (e.g., myVar)
```

**Example 1: "CANVAS"**
```
Char 'C': start → reading_word
Char 'A': reading_word → reading_word
Char 'N': reading_word → reading_word
Char 'V': reading_word → reading_word
Char 'A': reading_word → reading_word
Char 'S': reading_word → reading_word
Char ' ': reading_word → [accept, word="CANVAS"]
Lookup: RESERVED_WORDS["CANVAS"] = TokenType.CANVAS
Emit: Token(CANVAS, "CANVAS", line=1, col=1)
```

**Example 2: "myVar"**
```
Char 'm': start → reading_word
Char 'y': reading_word → reading_word
Char 'V': reading_word → reading_word
Char 'a': reading_word → reading_word
Char 'r': reading_word → reading_word
Char ' ': reading_word → [accept, word="myVar"]
Lookup: "myVar" not in RESERVED_WORDS
Emit: Token(IDENT, "myVar", line=1, col=1)
```

### 4.3 Implementation Details

#### 4.3.1 Main Lexer Loop

```python
def tokenize(self) -> list[Token]:
    tokens = []
    while self.pos < len(self.source):
        char = self.current()
        
        if char.isalpha() or char == '_':
            tokens.append(self.read_word())
        elif char.isdigit():
            tokens.append(self.read_number())
        elif char == '#':
            tokens.append(self.read_color())
        elif char in '{}':;':
            tokens.append(self.emit_punctuation(char))
        elif char in ' \t\n\r':
            self.skip_whitespace()
        elif char == '/' and self.peek() == '/':
            self.skip_line_comment()
        elif char == '/' and self.peek() == '*':
            self.skip_block_comment()
        else:
            raise LexError(f"Unknown character '{char}'", self.line, self.col)
    
    tokens.append(Token(TokenType.EOF, "", self.line, self.col))
    return tokens
```

#### 4.3.2 Token Recognition Examples

| Input | Token Type | Value | Notes |
|-------|-----------|-------|-------|
| `CANVAS` | KEYWORD | "CANVAS" | Keyword lookup |
| `32` | NUMBER | "32" | Decimal integer |
| `#FF0000` | COLOR | "#FF0000" | Valid hex: F, F, 0, 0, 0, 0 |
| `myVar` | IDENT | "myVar" | Not a keyword |
| `{` | LBRACE | "{" | Punctuation |
| `}` | RBRACE | "}" | Punctuation |
| `;` | SEMICOLON | ";" | Punctuation |

### 4.4 Error Handling in Lexer

| Error Type | Example | Message |
|-----------|---------|---------|
| **Unknown Character** | `@` in code | `[LexError] line 1, col 5: Unknown character '@'` |
| **Invalid Color** | `#GGGGGG` | `[LexError] line 2, col 10: Invalid color format` |
| **Unclosed Comment** | `/* no end` | `[LexError] line 3: Unclosed block comment` |

---

## 5. Syntax Analysis (Parser)

### 5.1 Overview

The parser reads tokens and builds an **Abstract Syntax Tree (AST)**. It uses an **LL(1) recursive descent grammar**, meaning:
- **LL:** Left-to-right input, Leftmost derivation
- **1:** Single token of lookahead
- **Recursive Descent:** Implement grammar rules as recursive functions

### 5.2 PixelLang Formal Grammar (BNF)

```ebnf
<program>       ::= <statement>* EOF

<statement>     ::= <canvas_stmt>
                |   <draw_stmt>
                |   <transform_stmt>
                |   <loop_stmt>
                |   <variable_stmt>

<canvas_stmt>   ::= CANVAS NUMBER NUMBER SEMICOLON

<draw_stmt>     ::= <pixel_stmt>
                |   <rect_stmt>
                |   <line_stmt>
                |   <circle_stmt>
                |   <ellipse_stmt>
                |   <triangle_stmt>
                |   <arc_stmt>
                |   <polygon_stmt>
                |   <border_stmt>
                |   <fill_stmt>
                |   <clear_stmt>
                |   <text_stmt>
                |   ... (16 more shape types in v2.0)

<pixel_stmt>    ::= PIXEL NUMBER NUMBER COLOR SEMICOLON
<rect_stmt>     ::= RECT NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<line_stmt>     ::= LINE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<circle_stmt>   ::= CIRCLE NUMBER NUMBER NUMBER COLOR SEMICOLON
<ellipse_stmt>  ::= ELLIPSE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<triangle_stmt> ::= TRIANGLE NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<arc_stmt>      ::= ARC NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<polygon_stmt>  ::= POLYGON (NUMBER NUMBER){4} COLOR SEMICOLON
<border_stmt>   ::= BORDER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<fill_stmt>     ::= FILL NUMBER NUMBER COLOR SEMICOLON
<clear_stmt>    ::= CLEAR COLOR SEMICOLON
<text_stmt>     ::= TEXT NUMBER NUMBER (STRING | IDENT) COLOR SEMICOLON

<transform_stmt> ::= <translate_stmt>
                |    <rotate_stmt>
                |    <scale_stmt>
                |    <mirror_stmt>

<translate_stmt> ::= TRANSLATE NUMBER NUMBER SEMICOLON
<rotate_stmt>    ::= ROTATE NUMBER SEMICOLON
<scale_stmt>     ::= SCALE NUMBER SEMICOLON
<mirror_stmt>    ::= MIRROR NUMBER SEMICOLON

<loop_stmt>      ::= LOOP NUMBER LBRACE <statement>* RBRACE

<variable_stmt>  ::= <var_stmt>
                |    <set_stmt>

<var_stmt>       ::= VAR IDENT NUMBER SEMICOLON
<set_stmt>       ::= SET IDENT NUMBER SEMICOLON
```

### 5.3 Why LL(1)?

**LL(1) Property:** Each non-terminal can be uniquely determined by looking ahead 1 token.

**Example Analysis:**

```
<statement> has alternatives:
  - CANVAS    → <canvas_stmt>
  - PIXEL     → <pixel_stmt>
  - RECT      → <rect_stmt>
  - ...

Lookahead token: CANVAS
  → FIRST(CANVAS) = {CANVAS}
  → Unique choice: <canvas_stmt>
  → Parse: expect NUMBER NUMBER SEMICOLON
```

All statement alternatives start with distinct keywords, so LL(1) is achievable.

### 5.4 LL(1) Parse Table

A simplified view:

| Current Token | Action |
|---------------|--------|
| `CANVAS` | Call `parse_canvas()` → expect NUMBER, NUMBER, SEMICOLON |
| `PIXEL` | Call `parse_pixel()` → expect NUMBER, NUMBER, COLOR, SEMICOLON |
| `RECT` | Call `parse_rect()` → expect NUMBER×4, COLOR, SEMICOLON |
| `LOOP` | Call `parse_loop()` → expect NUMBER, LBRACE, stmts, RBRACE |
| `TRANSLATE` | Call `parse_translate()` → expect NUMBER, NUMBER, SEMICOLON |
| `EOF` | Accept (end of program) |
| Other | Parse error |

### 5.5 Recursive Descent Implementation

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self):
        statements = []
        while self.current().type != TokenType.EOF:
            statements.append(self.parse_statement())
        return ProgramNode(statements)
    
    def parse_statement(self):
        tok = self.current()
        
        if tok.type == TokenType.CANVAS:
            return self.parse_canvas()
        elif tok.type == TokenType.PIXEL:
            return self.parse_pixel()
        elif tok.type == TokenType.RECT:
            return self.parse_rect()
        # ... more cases ...
        else:
            raise ParseError(f"Unexpected token {tok.type}")
    
    def parse_canvas(self):
        self.expect(TokenType.CANVAS)
        width = self.expect_number()
        height = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return CanvasNode(width, height, line=self.tokens[self.pos-1].line)
```

### 5.6 Example Parse Trace

**Input:** `CANVAS 10 10; PIXEL 5 5 #FF0000;`

```
Tokens:
  [0] Token(CANVAS, "CANVAS", 1, 1)
  [1] Token(NUMBER, "10", 1, 8)
  [2] Token(NUMBER, "10", 1, 11)
  [3] Token(SEMICOLON, ";", 1, 13)
  [4] Token(PIXEL, "PIXEL", 2, 1)
  [5] Token(NUMBER, "5", 2, 7)
  [6] Token(NUMBER, "5", 2, 9)
  [7] Token(COLOR, "#FF0000", 2, 11)
  [8] Token(SEMICOLON, ";", 2, 18)
  [9] Token(EOF, "", 2, 19)

Parse:
  pos=0, tok=CANVAS
    → Call parse_canvas()
    → Consume CANVAS (pos=1)
    → Consume 10 (pos=2)
    → Consume 10 (pos=3)
    → Consume ; (pos=4)
    → Return CanvasNode(10, 10)
  
  pos=4, tok=PIXEL
    → Call parse_pixel()
    → Consume PIXEL (pos=5)
    → Consume 5 (pos=6)
    → Consume 5 (pos=7)
    → Consume #FF0000 (pos=8)
    → Consume ; (pos=9)
    → Return PixelNode(5, 5, "#FF0000")
  
  pos=9, tok=EOF
    → Exit loop
    → Return ProgramNode([CanvasNode, PixelNode])

AST:
  ProgramNode
  ├── CanvasNode(width=10, height=10)
  └── PixelNode(x=5, y=5, color="#FF0000")
```

### 5.7 Error Recovery

Parser errors are thrown immediately:

```python
def expect(self, expected_type):
    tok = self.current()
    if tok.type != expected_type:
        raise ParseError(
            f"Expected {expected_type.name}, got '{tok.value}'",
            tok.line, tok.col
        )
    return self.advance()
```

**Example:**
```
Input: CANVAS 10 10  PIXEL 0 0 #FF0000;
                  ↑ Missing semicolon

Error:
  [ParseError] line 1, col 14: Expected SEMICOLON, got 'PIXEL'
```

---

## 6. Semantic Analysis

### 6.1 Overview

The semantic analyzer validates:
1. **Scope rules:** CANVAS must be first; LOOP must have positive count
2. **Type rules:** Colors must match #RRGGBB; coordinates must be integers
3. **Bounds rules:** All coordinates and radii must be within canvas limits
4. **Symbol table:** Track variable definitions and loop scope nesting

### 6.2 The 37 Semantic Rules

#### Core Rules (SEM-01 to SEM-13)

| Rule | Condition | Example Violation |
|------|-----------|-------------------|
| SEM-01 | CANVAS must be first statement | `PIXEL 0 0 #FF0000; CANVAS 10 10;` |
| SEM-02 | CANVAS declared at most once | Two `CANVAS` statements |
| SEM-03 | Canvas dimensions must be positive | `CANVAS 0 10;` or `CANVAS -5 20;` |
| SEM-04 | PIXEL x within bounds (0 ≤ x < width) | `CANVAS 10 10; PIXEL 15 5 #FF0000;` |
| SEM-05 | PIXEL y within bounds (0 ≤ y < height) | `CANVAS 10 10; PIXEL 5 15 #FF0000;` |
| SEM-06 | Color format valid (#RRGGBB) | `PIXEL 0 0 #GGGGGG;` (invalid hex) |
| SEM-07 | RECT dimensions must be positive | `RECT 0 0 0 10 #FF0000;` (w=0) |
| SEM-08 | RECT within bounds | `CANVAS 10 10; RECT 5 5 10 10 #FF0000;` (extends beyond) |
| SEM-09 | LINE endpoints within bounds | `CANVAS 10 10; LINE 0 0 20 20 #FF0000;` |
| SEM-10 | CIRCLE radius must be positive | `CIRCLE 5 5 0 #FF0000;` |
| SEM-11 | CIRCLE must be within bounds | `CANVAS 10 10; CIRCLE 5 5 10 #FF0000;` (radius too large) |
| SEM-12 | LOOP count must be positive | `LOOP 0 { PIXEL 0 0 #FF0000; }` |
| SEM-13 | ROTATE angle must be 0-360 | `ROTATE 450;` |

#### Extended Rules (SEM-14 to SEM-26)

| Rule | Condition |
|------|-----------|
| SEM-14 | FILL position within bounds |
| SEM-15 | ELLIPSE radii must be positive |
| SEM-16 | ELLIPSE within bounds |
| SEM-17 | BORDER dimensions must be positive |
| SEM-18 | BORDER within bounds |
| SEM-19 | TRIANGLE vertices within bounds |
| SEM-20 | ARC radius must be positive |
| SEM-21 | ARC center within bounds |
| SEM-22 | ARC angles 0-360 |
| SEM-23 | POLYGON points within bounds |
| SEM-24 | TEXT position within bounds |
| SEM-25 | MIRROR axis 0 or 1 |
| SEM-26 | SCALE factor 1-10 |

#### v2.0 Rules (SEM-27 to SEM-37)

| Rule | Condition |
|------|-----------|
| SEM-27 | BEZIER points within bounds |
| SEM-28 | STAR parameters valid |
| SEM-29 | ROUNDRECT within bounds |
| SEM-30 | HEART within bounds |
| SEM-31 | ARROW endpoints within bounds |
| SEM-32 | PALETTE index 0-15 |
| SEM-33 | SETPALETTE index 0-15 |
| SEM-34 | SPRITE pattern valid (0/1 only) |
| SEM-35 | RANDOM range valid (min < max) |
| SEM-36 | VAR definition (variable declared) |
| SEM-37 | SET uses defined variable |

### 6.3 Symbol Table Implementation

Stack-based scope management:

```python
class Symbol:
    name: str          # "canvas", "loop_i", "myVar"
    kind: str          # "canvas", "variable", "loop_counter"
    value: any         # 100, (50, 50), 5
    value_type: str    # "int", "tuple", "color"
    defined_at: int    # source line number
    scope_depth: int   # 0 = global, 1 = loop, 2 = nested loop

class SymbolTable:
    scopes: list       # Stack of {name → Symbol} dicts
    
    def enter_scope(): scopes.append({})       # LOOP entry
    def exit_scope():  scopes.pop()            # LOOP exit
    def define(name, kind, value, type, line): scopes[-1][name] = Symbol(...)
    def lookup(name): search scopes from innermost to outermost
```

**Example Trace:**

```
CANVAS 20 20;
LOOP 3 {
    PIXEL 0 0 #FF0000;
    TRANSLATE 1 1;
}

Semantic Analysis:

  Visit CanvasNode:
    → enter global scope (depth 0)
    → define "canvas" → Symbol(name="canvas", value=(20,20), depth=0)
    → symbol table: {0: {"canvas": Symbol}}
  
  Visit LoopNode:
    → enter loop scope (depth 1)
    → define "loop_count" → Symbol(name="loop_count", value=3, depth=1)
    → define "loop_iter" → Symbol(name="loop_iter", value=0, depth=1)
    → symbol table: {0: {"canvas": ...}, 1: {"loop_count": ..., "loop_iter": ...}}
    → visit loop body
      → check PIXEL bounds against canvas (20, 20) ✓
      → check TRANSLATE (always valid)
    → exit loop scope
    → symbol table: {0: {"canvas": ...}}
```

### 6.4 Semantic Analyzer Structure

```python
class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.sym_table = SymbolTable()
        self.canvas_w = None
        self.canvas_h = None
        self.errors = []
    
    def analyze(self, program):
        self.errors = []
        self.visit(program)
        return self.errors
    
    def visit_CanvasNode(self, node):
        # SEM-01, SEM-02, SEM-03
        if not first_stmt: error("CANVAS must be first")
        if already_seen: error("Duplicate CANVAS")
        if node.width <= 0 or node.height <= 0: error("Dimensions must be positive")
        
        self.canvas_w = node.width
        self.canvas_h = node.height
        self.sym_table.define("canvas", "canvas", (node.width, node.height), "tuple", node.line)
    
    def visit_PixelNode(self, node):
        # SEM-04, SEM-05, SEM-06
        if not (0 <= node.x < self.canvas_w): error("x out of bounds")
        if not (0 <= node.y < self.canvas_h): error("y out of bounds")
        if not valid_color(node.color): error("Invalid color format")
    
    def visit_LoopNode(self, node):
        # SEM-12
        if node.count <= 0: error("Loop count must be positive")
        
        self.sym_table.enter_scope()
        self.sym_table.define("loop_count", "loop_counter", node.count, "int", node.line)
        self.sym_table.define("loop_iter", "loop_counter", 0, "int", node.line)
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.sym_table.exit_scope()
```

---

## 7. Code Generation

### 7.1 Overview

The code generator converts a validated AST into a PNG image using Pillow (PIL). It:
1. Creates a canvas (white background)
2. Walks the AST, executing drawing commands
3. Maintains transform state (translation, rotation, scale, mirror)
4. Outputs to PIL Image object

### 7.2 Transform State

```python
class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.image = None
        self.draw = None
        
        # Transform accumulation
        self.tx = 0      # translation x
        self.ty = 0      # translation y
        self.angle = 0   # rotation (degrees)
        self.scale = 1   # scale factor
```

### 7.3 Drawing Pipeline

```
AST Node (e.g., PixelNode)
  ↓
visit_PixelNode(node)
  ├ Apply transform: (x, y) → (x + tx, y + ty)
  ├ Convert color: "#FF0000" → (255, 0, 0)
  ├ Call PIL draw.point((x, y), fill=(255, 0, 0))
  └ Return (no explicit value)
```

### 7.4 Key Drawing Methods

```python
def visit_PixelNode(self, node):
    x, y = self.transform_point(node.x, node.y)
    self.draw.point((x, y), fill=node.color)

def visit_RectNode(self, node):
    x0, y0 = self.transform_point(node.x, node.y)
    x1, y1 = x0 + node.w, y0 + node.h
    self.draw.rectangle([x0, y0, x1, y1], fill=node.color)

def visit_CircleNode(self, node):
    cx, cy = self.transform_point(node.cx, node.cy)
    r = node.radius
    bbox = [cx - r, cy - r, cx + r, cy + r]
    self.draw.ellipse(bbox, fill=node.color)

def visit_LoopNode(self, node):
    self.tx_stack.append(self.tx)
    self.ty_stack.append(self.ty)
    
    for i in range(node.count):
        for stmt in node.body:
            self.visit(stmt)
    
    self.tx = self.tx_stack.pop()
    self.ty = self.ty_stack.pop()

def visit_TranslateNode(self, node):
    self.tx += node.dx
    self.ty += node.dy

def visit_FillNode(self, node):
    # Iterative flood fill using queue (BFS)
    x, y = self.transform_point(node.x, node.y)
    seed_color = self.image.getpixel((x, y))
    target_rgb = self.parse_color(node.color)
    
    if seed_color == target_rgb:
        return  # Already target color
    
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) out of bounds: continue
        if image[cx, cy] != seed_color: continue
        
        image[cx, cy] = target_rgb
        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
```

---

## 8. AST Optimization

### 8.1 Overview

The optimizer applies semantics-preserving transformations to the AST **after** semantic analysis and **before** code generation. This reduces redundancy and improves execution efficiency.

### 8.2 Optimization Passes

#### Pass 1: Dead Variable Elimination (DCE)

Remove `VAR` and `SET` statements since current code generation doesn't read variables.

**Before:**
```
CANVAS 10 10;
VAR temp 5;
SET temp 10;
PIXEL 0 0 #FF0000;
```

**After:**
```
CANVAS 10 10;
PIXEL 0 0 #FF0000;
```

**Implementation:**
```python
def _optimize_statement_list(statements):
    optimized = []
    for node in statements:
        if isinstance(node, (VarNode, SetNode)):
            continue  # Skip
        if isinstance(node, LoopNode):
            optimized.append(LoopNode(node.count, _optimize_statement_list(node.body), node.line))
        else:
            optimized.append(node)
    return optimized
```

#### Pass 2: Transform Chain Folding

Coalesce adjacent TRANSLATE, ROTATE, SCALE, MIRROR sequences into single canonical statements.

**Before:**
```
TRANSLATE 1 0;
TRANSLATE 2 3;
ROTATE 90;
ROTATE 270;
SCALE 2;
SCALE 1;
MIRROR 0;
MIRROR 0;
PIXEL 0 0 #FF0000;
```

**After:**
```
TRANSLATE 3 3;
SCALE 2;
PIXEL 0 0 #FF0000;
```

**Folding Rules:**
- `TRANSLATE a b` + `TRANSLATE c d` → `TRANSLATE (a+c) (b+d)`
- `ROTATE a` + `ROTATE b` → `ROTATE ((a+b) mod 360)`
- `SCALE a` + `SCALE b` → `SCALE (a*b)`
- `MIRROR 0` + `MIRROR 0` → (cancel, no-op)
- `MIRROR 1` + `MIRROR 1` → (cancel, no-op)

**Implementation:**
```python
def _fold_transform_chain(statements, start_index):
    chain = []
    i = start_index
    while i < len(statements) and isinstance(statements[i], (TranslateNode, RotateNode, ScaleNode, MirrorNode)):
        chain.append(statements[i])
        i += 1
    
    # Accumulate transform values
    total_dx, total_dy = 0, 0
    total_angle = 0
    total_scale = 1
    mirror_x, mirror_y = False, False
    
    for node in chain:
        if isinstance(node, TranslateNode):
            total_dx += node.dx
            total_dy += node.dy
        elif isinstance(node, RotateNode):
            total_angle = (total_angle + node.angle) % 360
        elif isinstance(node, ScaleNode):
            total_scale *= node.factor
        elif isinstance(node, MirrorNode):
            if node.axis == 0:
                mirror_y = not mirror_y
            else:
                mirror_x = not mirror_x
    
    # Emit only non-trivial transforms
    folded = []
    if total_dx != 0 or total_dy != 0:
        folded.append(TranslateNode(total_dx, total_dy, chain[0].line))
    if total_angle != 0:
        folded.append(RotateNode(total_angle, chain[0].line))
    if total_scale != 1:
        folded.append(ScaleNode(total_scale, chain[0].line))
    if mirror_y:
        folded.append(MirrorNode(0, chain[0].line))
    if mirror_x:
        folded.append(MirrorNode(1, chain[0].line))
    
    return folded, i
```

#### Pass 3: No-op Removal (Single Nodes)

Remove single transforms that have no effect.

**Before:**
```
CANVAS 8 8;
TRANSLATE 0 0;
ROTATE 0;
SCALE 1;
PIXEL 4 4 #00FF00;
```

**After:**
```
CANVAS 8 8;
PIXEL 4 4 #00FF00;
```

### 8.3 Comparison: Before vs After Optimization

Run the pretty-printer to visualize:

```python
from compiler import lex, parse, optimize, pretty_print

source = """
CANVAS 10 10;
VAR temp 1;
TRANSLATE 1 0;
TRANSLATE 2 0;
ROTATE 0;
LOOP 2 {
    VAR i 5;
    TRANSLATE 1 1;
    TRANSLATE 1 1;
}
PIXEL 0 0 #FF0000;
"""

ast = parse(lex(source))
print("=== BEFORE OPTIMIZATION ===")
print(pretty_print(ast))

optimized = optimize(ast)
print("\n=== AFTER OPTIMIZATION ===")
print(pretty_print(optimized))
```

**Output:**
```
=== BEFORE OPTIMIZATION ===
CANVAS 10 10;
VAR temp 1;
TRANSLATE 1 0;
TRANSLATE 2 0;
ROTATE 0;
LOOP 2 {
  VAR i 5;
  TRANSLATE 1 1;
  TRANSLATE 1 1;
}
PIXEL 0 0 #FF0000;

=== AFTER OPTIMIZATION ===
CANVAS 10 10;
TRANSLATE 3 0;
LOOP 2 {
  TRANSLATE 2 2;
}
PIXEL 0 0 #FF0000;
```

---

## 9. Viva Questions & Answers

### 9.1 Lexical Analysis (Lexer & DFA)

**Q1: What is a DFA? Explain with a simple example.**

**A1:** A DFA (Deterministic Finite Automaton) is a state machine with:
- **States:** Configurations of the machine (e.g., "start", "reading digits", "accept")
- **Transitions:** Rules that move between states (e.g., "if input is a digit, go to reading_digits")
- **Accepting states:** Where we emit a token (e.g., "emit NUMBER")

Example: Recognizing the number "42"
```
"42"
 ↓ '4' is a digit: start → reading_digits
 ↓ '2' is a digit: reading_digits → reading_digits
 ↓ ' ' is not a digit: reading_digits → [accept]
   Emit: Token(NUMBER, "42")
```

**Q2: Why is DFA used in the lexer instead of regex?**

**A2:** DFAs give us:
- **Control:** We can manually design state transitions for each token type
- **Error reporting:** We know exactly line/column when an error occurs
- **Efficiency:** DFA is O(n) where n is input length
- **Learning:** Understanding DFAs teaches compiler fundamentals

Regex would be simpler but less educational and harder to integrate with position tracking.

**Q3: What happens if you enter an invalid color like `#GGGGGG`?**

**A3:** The lexer's color DFA:
```
Start at '##'
'G' is not in [0-9A-Fa-f]
Trigger LexError: "Invalid color format #GGGGGG at line X, col Y"
```

**Q4: Explain token lookahead. How does the lexer know when a number ends?**

**A4:** The lexer reads characters until it hits a non-digit:
```python
def read_number(self):
    start = self.pos
    while self.pos < len(source) and source[self.pos].isdigit():
        self.pos += 1
    
    num_str = source[start:self.pos]
    return Token(NUMBER, num_str, line, col)
```

When it encounters `;` or space, it stops and emits the NUMBER token. This is 1-character lookahead.

**Q5: What's the difference between a keyword and an identifier?**

**A5:** Both follow the same lexical pattern `[a-zA-Z_][a-zA-Z0-9_]*`. But:
- **Keyword:** Word is in `RESERVED_WORDS` dict (e.g., "CANVAS" → TokenType.CANVAS)
- **Identifier:** Word is NOT in dict (e.g., "myVar" → TokenType.IDENT)

```python
RESERVED_WORDS = {
    "CANVAS": TokenType.CANVAS,
    "PIXEL": TokenType.PIXEL,
    "LOOP": TokenType.LOOP,
    ...
}

word = "CANVAS"
token_type = RESERVED_WORDS.get(word, TokenType.IDENT)  # TokenType.CANVAS

word = "myVar"
token_type = RESERVED_WORDS.get(word, TokenType.IDENT)  # TokenType.IDENT
```

---

### 9.2 Syntax Analysis (Parser & Grammar)

**Q6: What is LL(1)? Why is PixelLang LL(1)?**

**A6:** LL(1) means:
- **L:** Left-to-right scanning of input
- **L:** Leftmost derivation (expand leftmost non-terminal first)
- **1:** Only 1 token of lookahead needed

PixelLang is LL(1) because all statement alternatives start with **distinct** keywords:

```
<statement> → CANVAS ... | PIXEL ... | RECT ... | LOOP ... | TRANSLATE ... | ROTATE ...

Lookahead token → Unique choice
  CANVAS       → parse_canvas()
  PIXEL        → parse_pixel()
  RECT         → parse_rect()
  etc.
```

Each keyword uniquely identifies which statement type follows. No backtracking needed.

**Q7: What is recursive descent parsing?**

**A7:** Recursive descent means each grammar rule becomes a function:

```
Grammar:
  <statement> ::= CANVAS NUMBER NUMBER SEMICOLON
               |  PIXEL NUMBER NUMBER COLOR SEMICOLON
               |  ...

Code:
  def parse_statement(self):
      tok = self.current()
      if tok.type == TokenType.CANVAS:
          return self.parse_canvas()
      elif tok.type == TokenType.PIXEL:
          return self.parse_pixel()

  def parse_canvas(self):
      self.expect(TokenType.CANVAS)
      w = self.expect_number()
      h = self.expect_number()
      self.expect(TokenType.SEMICOLON)
      return CanvasNode(w, h)
```

Each rule calls other rules (recursion) or expects terminals (base case).

**Q8: What happens if you forget a semicolon? Example: `CANVAS 10 10`**

**A8:** Parser trace:
```
Tokens: [CANVAS, NUMBER(10), NUMBER(10), PIXEL, NUMBER(0), NUMBER(0), COLOR(#FF0000), SEMICOLON, EOF]
                                          ↑ Expected SEMICOLON here, got PIXEL

parse_canvas():
  expect(CANVAS) ✓
  expect_number() → 10 ✓
  expect_number() → 10 ✓
  expect(SEMICOLON) ✗ Current token is PIXEL
  
Raise: ParseError("Expected SEMICOLON, got 'PIXEL'", line=1, col=14)
```

**Q9: What is the AST? Draw the AST for `LOOP 2 { PIXEL 0 0 #FF0000; }`**

**A9:** AST is a **tree** that represents program structure without syntax details.

```
ProgramNode
└── LoopNode
    ├── count = 2
    ├── line = 1
    └── body = [
          PixelNode
          ├── x = 0
          ├── y = 0
          ├── color = "#FF0000"
          └── line = 1
        ]
```

Notice: No tokens for `{`, `}` in the tree (they're syntax; AST is semantic).

**Q10: Why does the parser build an AST instead of directly generating code?**

**A10:**
1. **Separation of concerns:** Parser handles syntax; later phases handle semantics
2. **Optimization:** Can optimize the AST before code generation
3. **Multiple backends:** Could generate C code, bytecode, etc. from same AST
4. **Error recovery:** Semantic analyzer can collect all errors, not just first

---

### 9.3 Semantic Analysis & Symbol Table

**Q11: What is a symbol table? Why do we need it?**

**A11:** A symbol table is a **data structure mapping names to information:**

```python
{
  "canvas": Symbol(name="canvas", value=(20, 20), kind="canvas", scope_depth=0),
  "temp": Symbol(name="temp", value=5, kind="variable", scope_depth=0)
}
```

We need it to:
- **Verify scope:** Check that variables are defined before use
- **Track state:** Remember canvas dimensions for bounds checking
- **Nest scopes:** Support LOOPs with their own `loop_count`, `loop_iter`

**Q12: What is scope depth? Give an example of a program with scope_depth=2.**

**A12:** Scope depth is how deeply nested we are:
- **depth=0:** Global scope
- **depth=1:** Inside LOOP
- **depth=2:** Inside nested LOOP

```
CANVAS 10 10;              ← depth=0
LOOP 3 {                   ← depth=1 (enter_scope)
  PIXEL 0 0 #FF0000;         scope_depth=1
  LOOP 2 {                 ← depth=2 (enter_scope)
    PIXEL 1 1 #00FF00;       scope_depth=2
  }                        ← depth=1 (exit_scope)
}                          ← depth=0 (exit_scope)
```

**Q13: What does `enter_scope()` and `exit_scope()` do?**

**A13:**
```python
def enter_scope(self):
    self.scopes.append({})  # Push new empty dict onto stack
    
def exit_scope(self):
    self.scopes.pop()  # Pop the top scope

# Example:
scopes = [{"canvas": ...}]                               # depth=0
enter_scope()
scopes = [{"canvas": ...}, {"loop_count": ...}]          # depth=1
exit_scope()
scopes = [{"canvas": ...}]                               # depth=0
```

Symbol table is a **stack** of scopes. When entering a LOOP, push a new scope. When exiting, pop it.

**Q14: What are the 37 semantic rules about?**

**A14:** Grouped by category:

| Category | Rules | Example |
|----------|-------|---------|
| Scope | SEM-01, SEM-02 | CANVAS first, at most once |
| Type | SEM-03, SEM-06 | Positive dimensions, valid colors |
| Bounds | SEM-04, SEM-05, ..., SEM-24 | All coordinates within canvas |
| Range | SEM-12, SEM-13, SEM-25, SEM-26 | Loop count > 0, angle 0-360, mirror 0/1, scale 1-10 |
| Variables | SEM-36, SEM-37 | VAR defines; SET uses defined variable |

**Q15: What happens if a PIXEL is out of bounds? Example: `CANVAS 10 10; PIXEL 20 5 #FF0000;`**

**A15:**
```
visit_PixelNode(PixelNode(x=20, y=5)):
  canvas_w = 10, canvas_h = 10
  Check: 0 <= 20 < 10?  NO ✗
  error("PIXEL x=20 out of bounds (canvas width=10)", line=2)
  
Return: errors = [SemanticError(...)]
Result: Image generation doesn't happen; errors reported to user
```

---

### 9.4 Code Generation & Transformations

**Q16: What is "transform state"? Give an example where TRANSLATE matters.**

**A16:** Transform state tracks cumulative transformations:
```python
self.tx = 0          # total x translation
self.ty = 0          # total y translation
self.angle = 0       # rotation angle
self.scale = 1       # scale factor
```

**Example:**
```
LOOP 3 {
  PIXEL 0 0 #FF0000;
  TRANSLATE 5 0;
}
```

Execution:
```
Iteration 1:
  PIXEL 0 0 → draw at (0 + 0, 0 + 0) = (0, 0)
  TRANSLATE 5 0 → tx = 5, ty = 0

Iteration 2:
  PIXEL 0 0 → draw at (0 + 5, 0 + 0) = (5, 0)
  TRANSLATE 5 0 → tx = 10, ty = 0

Iteration 3:
  PIXEL 0 0 → draw at (0 + 10, 0 + 0) = (10, 0)
  TRANSLATE 5 0 → tx = 15, ty = 0

Result: 3 pixels in a horizontal line
```

**Q17: Why does LOOP save and restore transform state?**

**A17:** So that transforms inside the loop don't leak outside.

```python
def visit_LoopNode(self, node):
    self.tx_stack.append(self.tx)  # Save
    self.ty_stack.append(self.ty)
    
    for i in range(node.count):
        for stmt in node.body:
            self.visit(stmt)
    
    self.tx = self.tx_stack.pop()  # Restore
    self.ty = self.ty_stack.pop()
```

**Example:**
```
TRANSLATE 10 0;
LOOP 2 {
  TRANSLATE 5 0;
  PIXEL 0 0 #FF0000;
}
PIXEL 0 0 #0000FF;

Execution:
  TRANSLATE 10 0: tx=10
  LOOP:
    Save: tx_stack = [10]
    Iter1: TRANSLATE 5 0 (tx=15), PIXEL at (15, 0)
    Iter2: TRANSLATE 5 0 (tx=20), PIXEL at (20, 0)
    Restore: tx=10
  PIXEL 0 0 #0000FF: draw at (10, 0) [OUTSIDE loop, tx is still 10]
```

**Q18: What is flood fill? Explain with an example.**

**A18:** Flood fill is like the "paint bucket" tool in image editors. It fills a region with one color.

```
Algorithm (iterative BFS):
  1. Get starting pixel color (seed color)
  2. If seed == target color, do nothing (already filled)
  3. Create stack: [starting position]
  4. While stack not empty:
     a. Pop position (x, y)
     b. If (x, y) is out of bounds, continue
     c. If pixel at (x, y) != seed color, continue
     d. Paint pixel at (x, y) with target color
     e. Add neighbors (x±1, y), (x, y±1) to stack

Example:
  Before:     After (FILL 1 1 #FF0000):
  ....        .###
  .###        ###0
  ####        ####
  ####        ####
  
  Seed color at (1,1) = white
  Target color = red
  Fill spreads to all adjacent white pixels
```

**Q19: Draw the PIL code for drawing a RECT.**

**A19:**
```python
def visit_RectNode(self, node):
    # Apply transform
    x0, y0 = self.transform_point(node.x, node.y)
    x1, y1 = x0 + node.w, y0 + node.h
    
    # Draw filled rectangle using PIL
    self.draw.rectangle([x0, y0, x1, y1], fill=node.color)
    
# Example: RECT 10 10 20 20 #00FF00
# Creates green rectangle from (10, 10) to (30, 30)
```

---

### 9.5 Optimizations

**Q20: What is dead code? Give an example from PixelLang.**

**A20:** Dead code is a statement that has no effect on the final result.

In PixelLang, `VAR` and `SET` are dead code because code generation doesn't read variables (no expression evaluation yet):

```
CANVAS 10 10;
VAR temp 5;         ← Dead: defines temp but never reads it
SET temp 10;        ← Dead: modifies temp but code gen ignores it
PIXEL 5 5 #FF0000;  ← NOT dead: affects output
```

**Optimization:** Remove these statements.

**Q21: What is transform chain folding? Give an example.**

**A21:** Folding means combining adjacent transform statements into simpler forms.

**Before:**
```
TRANSLATE 1 0;
TRANSLATE 2 3;
ROTATE 90;
ROTATE 270;
SCALE 2;
SCALE 1;
```

**Rules:**
- `TRANSLATE a b + TRANSLATE c d` → `TRANSLATE (a+c) (b+d)` = `TRANSLATE 3 3`
- `ROTATE 90 + ROTATE 270` → `ROTATE ((90+270) mod 360)` = `ROTATE 0` → removed (no-op)
- `SCALE 2 + SCALE 1` → `SCALE 2*1` = `SCALE 2`

**After:**
```
TRANSLATE 3 3;
SCALE 2;
```

**Why?** Fewer AST nodes = faster execution, cleaner code.

**Q22: What is no-op removal?**

**A22:** No-ops are transforms that have zero effect. Remove them.

| Transform | Meaning | No-op Test |
|-----------|---------|-----------|
| `TRANSLATE dx dy` | Shift pixels | No-op if dx=0 AND dy=0 |
| `ROTATE angle` | Rotate (visual only) | No-op if angle=0 |
| `SCALE factor` | Scale up | No-op if factor=1 |
| `MIRROR axis` | Flip | No-op if applied twice (parity) |

Example:
```
BEFORE: ROTATE 0; PIXEL 0 0 #FF0000;
AFTER: PIXEL 0 0 #FF0000;
```

---

### 9.6 Complete Workflow

**Q23: Walk through the entire compilation process for `CANVAS 10 10; PIXEL 5 5 #FF0000;`**

**A23:**

```
INPUT: "CANVAS 10 10; PIXEL 5 5 #FF0000;"

PHASE 1: LEXER
  Input stream: "CANVAS 10 10; PIXEL 5 5 #FF0000;"
  Tokens:
    Token(CANVAS, "CANVAS", 1, 1)
    Token(NUMBER, "10", 1, 8)
    Token(NUMBER, "10", 1, 11)
    Token(SEMICOLON, ";", 1, 13)
    Token(PIXEL, "PIXEL", 1, 15)
    Token(NUMBER, "5", 1, 21)
    Token(NUMBER, "5", 1, 23)
    Token(COLOR, "#FF0000", 1, 25)
    Token(SEMICOLON, ";", 1, 32)
    Token(EOF, "", 1, 33)

PHASE 2: PARSER
  Input: tokens (list)
  Parse <program>: expect <statement>* EOF
  Parse <statement>1: lookahead = CANVAS → parse_canvas()
    Consume CANVAS, 10, 10, ;
    Return CanvasNode(10, 10, line=1)
  Parse <statement>2: lookahead = PIXEL → parse_pixel()
    Consume PIXEL, 5, 5, #FF0000, ;
    Return PixelNode(5, 5, "#FF0000", line=1)
  Lookahead = EOF → exit loop
  Return ProgramNode([CanvasNode, PixelNode])

PHASE 3: SEMANTIC ANALYSIS
  Input: ProgramNode
  Visit CanvasNode:
    Check SEM-01: Is CANVAS first? YES ✓
    Check SEM-02: Is it duplicate? NO ✓
    Check SEM-03: Dimensions positive? YES (10, 10) ✓
    Define: symbol_table["canvas"] = Symbol(value=(10,10), depth=0)
  Visit PixelNode:
    Check canvas exists: YES ✓
    Check SEM-04: 0 <= 5 < 10? YES ✓
    Check SEM-05: 0 <= 5 < 10? YES ✓
    Check SEM-06: Color valid? YES (#FF0000 is valid hex) ✓
  Return: errors = [] (no errors)

PHASE 3.5: OPTIMIZATION
  Input: ProgramNode
  No adjacent transform chains, no dead code
  Return: ProgramNode (unchanged)

PHASE 4: CODE GENERATION
  Input: ProgramNode
  Visit CanvasNode:
    Create image: PIL.Image.new("RGB", (10, 10), "white")
  Visit PixelNode:
    Transform: (5, 5) + (tx=0, ty=0) = (5, 5)
    Draw: image.putpixel((5, 5), (255, 0, 0))
  Return: PIL.Image (10x10 image with one red pixel at (5, 5))

OUTPUT: PNG image file
```

**Q24: What if the semantic analyzer finds an error?**

**A24:** Example: `CANVAS 10 10; PIXEL 15 5 #FF0000;`

```
PHASE 3: SEMANTIC ANALYSIS
  Visit CanvasNode:
    All checks pass ✓
    canvas_w = 10, canvas_h = 10
  Visit PixelNode:
    Check SEM-04: 0 <= 15 < 10? NO ✗
    error("PIXEL x=15 out of bounds (canvas width=10)", line=1)
  Return: errors = [SemanticError(...)]

PHASE 3.5: OPTIMIZATION
  Skipped (errors exist)

PHASE 4: CODE GENERATION
  Skipped (errors exist)

OUTPUT: errors = [SemanticError(...)]
        image = None
        No PNG file generated
```

---

## Summary

PixelLang is a complete compiler demonstrating all phases:
1. **Lexer** (DFA-based tokenization)
2. **Parser** (LL(1) recursive descent)
3. **Semantic Analyzer** (37 rules, symbol table)
4. **Optimizer** (DCE, transform folding)
5. **Code Generator** (PIL-based drawing)

Each phase is independent, testable, and well-documented.

---

**References:**
- [lexer.py](compiler/lexer.py) — Tokenization
- [parser.py](compiler/parser.py) — Syntax analysis
- [semantic.py](compiler/semantic.py) — Semantic rules + symbol table
- [optimizer.py](compiler/optimizer.py) — AST optimizations
- [codegen.py](compiler/codegen.py) — PNG generation
- [tests/test_compiler.py](tests/test_compiler.py) — Integration tests
- [tests/test_optimizer.py](tests/test_optimizer.py) — Optimization tests
