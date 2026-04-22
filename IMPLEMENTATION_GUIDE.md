# PixelLang Implementation Guide for Beginners

> **Complete walkthrough of how the compiler works, explained in simple terms**

## Table of Contents
1. [What is a Compiler?](#what-is-a-compiler)
2. [Project Structure](#project-structure)
3. [Phase 1: Lexical Analysis (Tokenizer)](#phase-1-lexical-analysis-tokenizer)
4. [Phase 2: Syntax Analysis (Parser)](#phase-2-syntax-analysis-parser)
5. [Phase 3: Semantic Analysis](#phase-3-semantic-analysis)
6. [Phase 4: Code Generation](#phase-4-code-generation)
7. [The Grammar Explained](#the-grammar-explained)
8. [How Data Flows Through the Compiler](#how-data-flows-through-the-compiler)

---

## What is a Compiler?

A **compiler** is a program that translates code from one language (source code) to another language (target code). PixelLang is a special compiler that:

- **Input**: `.px` text files (PixelLang code)
- **Output**: `.png` image files (pixel art!)

Think of it like a translator: it takes human-readable drawing instructions and converts them into actual images.

### The 4 Phases of Compilation

```
Source Code (.px)  →  [Lexer]  →  [Parser]  →  [Semantic Analyzer]  →  [Code Generator]  →  Output (.png)
     ↓                  ↓           ↓              ↓                      ↓
   Text          Token List    AST Tree      Validated AST            PNG Image
```

---

## Project Structure

```
PixelLang/
├── compiler/                    # The compiler package
│   ├── __init__.py             # Package initialization with compile() function
│   ├── tokens.py                 # Token definitions (TokenType enum, Token class)
│   ├── lexer.py                  # Phase 1: Lexical analyzer (tokenizer)
│   ├── parser.py                 # Phase 2: Syntax analyzer (builds AST)
│   ├── ast_nodes.py              # AST node classes (data structures)
│   ├── semantic.py               # Phase 3: Semantic analyzer (validation)
│   ├── symbol_table.py           # Variable storage during compilation
│   ├── codegen.py                # Phase 4: Code generator (creates PNG)
│   ├── errors.py                 # Error classes (LexError, ParseError, etc.)
│   └── gui/                      # IDE GUI application
│       ├── ide.py                # Main IDE window
│       └── editor.py             # Code editor with syntax highlighting
├── examples/                     # Example .px programs
├── tests/                        # Unit tests
├── README.md                     # User documentation
├── DOCUMENTATION.md              # Technical documentation
└── main.py                       # CLI entry point
```

---

## Phase 1: Lexical Analysis (Tokenizer)

**File**: `compiler/tokens.py` and `compiler/lexer.py`

### What is Tokenization?

Tokenization is breaking text into "tokens" - the smallest meaningful units. Think of it like breaking a sentence into words.

**Example**:
```python
# Source code:
CANVAS 100 100;
PIXEL 10 10 #FF0000;

# After tokenization:
[Token(CANVAS, "CANVAS"), Token(NUMBER, "100"), Token(NUMBER, "100"), Token(SEMICOLON, ";"),
 Token(PIXEL, "PIXEL"), Token(NUMBER, "10"), Token(NUMBER, "10"), Token(COLOR, "#FF0000"), Token(SEMICOLON, ";")]
```

### Token Types (`tokens.py`)

```python
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    """All possible token types in PixelLang."""
    
    # Keywords (drawing commands)
    CANVAS = auto()     # Creates image canvas
    PIXEL = auto()      # Draws single pixel
    RECT = auto()       # Draws rectangle
    LINE = auto()       # Draws line
    CIRCLE = auto()     # Draws circle
    FILL = auto()       # Flood fill
    # ... 30+ more keywords
    
    # Literals
    NUMBER = auto()     # e.g., 100, 42
    COLOR = auto()      # e.g., #FF0000
    STRING = auto()     # e.g., "hello"
    
    # Identifiers
    IDENT = auto()      # Variable names
    
    # Punctuation
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    SEMICOLON = auto()  # ;
    
    # End of file
    EOF = auto()

# Reserved words dictionary - maps strings to token types
RESERVED_WORDS = {
    "CANVAS": TokenType.CANVAS,
    "PIXEL": TokenType.PIXEL,
    "RECT": TokenType.RECT,
    # ... all uppercase keywords
}

@dataclass
class Token:
    """A token stores type, value (the text), and position."""
    type: TokenType     # What kind of token
    value: str          # The actual text
    line: int           # Line number (for error reporting)
    col: int            # Column number (for error reporting)
```

### The Lexer - DFA Explained (`lexer.py`)

**DFA** = Deterministic Finite Automaton. It's a fancy term for a "state machine" - a program that reads one character at a time and changes state based on what it sees.

```python
class Lexer:
    """
    The lexer scans through source code character by character,
    recognizing patterns and creating tokens.
    """
    
    def __init__(self, source: str):
        self.source = source    # The entire source code as string
        self.pos = 0            # Current position in source
        self.line = 1           # Current line number
        self.col = 1            # Current column number
    
    def peek(self) -> str:
        """Look at current character without consuming it."""
        if self.pos >= len(self.source):
            return ''  # End of file
        return self.source[self.pos]
    
    def advance(self) -> str:
        """Consume current character and move to next."""
        char = self.source[self.pos]
        self.pos += 1
        
        # Track line/column for error reporting
        if char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        
        return char
```

### How Token Recognition Works

The main tokenization loop in `tokenize()`:

```python
def tokenize(self) -> list[Token]:
    """Main tokenization loop - the heart of the lexer."""
    self.tokens = []
    
    while True:
        self.skip_whitespace()  # Skip spaces, tabs, newlines
        char = self.peek()
        
        # Check what character we have and dispatch to appropriate handler
        if char == '':
            # EOF - add end token and stop
            self.tokens.append(Token(TokenType.EOF, '', self.line, self.col))
            break
        
        elif char == '{':
            self.advance()
            self.tokens.append(Token(TokenType.LBRACE, '{', self.line, self.col))
        
        elif char == '#':
            # Start of color - let read_color() handle it
            self.tokens.append(self.read_color())
        
        elif char.isdigit():
            # Start of number - let read_number() handle it
            self.tokens.append(self.read_number())
        
        elif char.isalpha() or char == '_':
            # Start of word (keyword or identifier)
            self.tokens.append(self.read_word())
        
        # ... more cases for each token type
    
    return self.tokens
```

### DFA for Numbers

```python
def read_number(self) -> Token:
    """
    DFA for NUMBER token.
    Pattern: [0-9]+ (one or more digits)
    
    State diagram:
    q0 --[digit]--> q1 --[digit]--> q1 (accept)
    
    We start in state q0. When we see a digit, move to q1.
    In q1, keep reading digits until we see non-digit.
    """
    start_line = self.line
    start_col = self.col
    num_str = ''
    
    # q1 loop: read all consecutive digits
    while self.peek().isdigit():
        num_str += self.advance()
    
    return Token(TokenType.NUMBER, num_str, start_line, start_col)
```

### DFA for Colors

```python
def read_color(self) -> Token:
    """
    DFA for COLOR token.
    Pattern: #[0-9A-Fa-f]{6} (hash + exactly 6 hex digits)
    
    State diagram:
    q0 --[#]--> q1 --[hex]--> q2 --> q3 --> q4 --> q5 --> q6 --> q7 (accept)
    
    Must have exactly 6 hex digits after the #
    """
    start_line = self.line
    start_col = self.col
    
    color = self.advance()  # consume # (q0 -> q1)
    
    # Must have exactly 6 hex digits
    for _ in range(6):
        char = self.peek()
        if char in '0123456789ABCDEFabcdef':
            color += self.advance()
        else:
            self.error(f"Invalid color: expected 6 hex digits after #")
    
    return Token(TokenType.COLOR, color, start_line, start_col)
```

### DFA for Keywords vs Identifiers

```python
def read_word(self) -> Token:
    """
    DFA for words (keywords or identifiers).
    Pattern: [a-zA-Z_][a-zA-Z0-9_]*
    
    - Must start with letter or underscore
    - Can contain letters, digits, underscores after
    """
    start_line = self.line
    start_col = self.col
    word = ''
    
    # Read first character (must be letter or _)
    word += self.advance()
    
    # Continue reading alphanumeric characters
    while self.peek().isalnum() or self.peek() == '_':
        word += self.advance()
    
    # Check if it's a keyword (uppercase match)
    token_type = RESERVED_WORDS.get(word, TokenType.IDENT)
    
    return Token(token_type, word, start_line, start_col)
```

**Key Insight**: Keywords are case-sensitive! `CANVAS` is a keyword, but `canvas` is an identifier.

---

## Phase 2: Syntax Analysis (Parser)

**File**: `compiler/parser.py`

### What is Parsing?

Parsing takes the flat list of tokens and builds a **tree structure** (AST - Abstract Syntax Tree) that represents the program's structure and meaning.

**Example**:
```
Tokens: [CANVAS, 100, 100, ;, RECT, 10, 10, 50, 50, #FF0000, ;]

AST:
ProgramNode
├── CanvasNode (width=100, height=100)
└── RectNode (x=10, y=10, w=50, h=50, color=#FF0000)
```

### The Grammar (BNF Notation)

**BNF** (Backus-Naur Form) is a way to describe the syntax rules of a language:

```
<program>       ::= <statement>* EOF
                  # A program is zero or more statements, then EOF

<statement>     ::= <canvas_stmt> | <draw_stmt> | <transform_stmt> | <control_stmt>
                  # A statement is one of these types

<canvas_stmt>   ::= CANVAS NUMBER NUMBER SEMICOLON
                  # CANVAS keyword, width number, height number, semicolon

<draw_stmt>     ::= <pixel_stmt> | <rect_stmt> | <circle_stmt> | ...

<pixel_stmt>    ::= PIXEL NUMBER NUMBER COLOR SEMICOLON
                  # PIXEL keyword, x, y, color, semicolon

<rect_stmt>     ::= RECT NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
                  # RECT keyword, x, y, width, height, color, semicolon

<loop_stmt>     ::= LOOP NUMBER LBRACE <statement>* RBRACE
                  # LOOP keyword, count, {, statements, }
```

The `::=` means "is defined as". The `|` means "or".

### LL(1) Recursive Descent Parser

**LL(1)** means:
- **L**eft-to-right scan
- **L**eftmost derivation
- **(1)** one token of lookahead

**Recursive Descent** means:
- Each grammar rule becomes a function
- Functions call each other recursively
- Easy to read and debug!

### Parser Structure

```python
class Parser:
    """LL(1) Recursive Descent Parser for PixelLang."""
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens    # List from lexer
        self.pos = 0            # Current position in token list
    
    def current(self) -> Token:
        """Get current token without consuming."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def advance(self) -> Token:
        """Consume and return current token."""
        tok = self.current()
        self.pos += 1
        return tok
    
    def expect(self, expected_type: TokenType) -> Token:
        """
        Expect a specific token type.
        Raises error if we get something else.
        """
        tok = self.current()
        if tok.type != expected_type:
            raise ParseError(
                f"Expected {expected_type.name}, got '{tok.value}'",
                tok.line, tok.col
            )
        return self.advance()
```

### The Main Parse Method

```python
def parse(self) -> ProgramNode:
    """
    Entry point: <program> ::= <statement>* EOF
    
    Parse all statements until we hit EOF.
    """
    statements = []
    
    while self.current().type != TokenType.EOF:
        statements.append(self.parse_statement())
    
    return ProgramNode(statements)
```

### LL(1) Parse Table (Dispatch)

```python
def parse_statement(self) -> ASTNode:
    """
    Parse a single statement using LL(1) dispatch.
    We look at the FIRST token to decide which rule to use.
    """
    tok = self.current()
    
    # This is the "parse table" - one if statement per keyword
    if tok.type == TokenType.CANVAS:
        return self.parse_canvas()
    elif tok.type == TokenType.PIXEL:
        return self.parse_pixel()
    elif tok.type == TokenType.RECT:
        return self.parse_rect()
    elif tok.type == TokenType.LOOP:
        return self.parse_loop()
    # ... more cases
    else:
        raise ParseError(f"Unexpected token: {tok.value}", tok.line, tok.col)
```

### Parsing Individual Statements

**CANVAS statement**:
```python
def parse_canvas(self) -> CanvasNode:
    """
    Grammar: CANVAS NUMBER NUMBER SEMICOLON
    
    Example: CANVAS 100 100;
    """
    line_num = self.current().line  # Save line for error reporting
    
    self.expect(TokenType.CANVAS)   # Must see CANVAS keyword
    width = self.expect_number()    # Must see number (width)
    height = self.expect_number()   # Must see number (height)
    self.expect(TokenType.SEMICOLON) # Must see semicolon
    
    return CanvasNode(width, height, line_num)
```

**PIXEL statement**:
```python
def parse_pixel(self) -> PixelNode:
    """
    Grammar: PIXEL NUMBER NUMBER COLOR SEMICOLON
    
    Example: PIXEL 10 10 #FF0000;
    """
    line_num = self.current().line
    
    self.expect(TokenType.PIXEL)    # PIXEL keyword
    x = self.expect_number()        # x coordinate
    y = self.expect_number()        # y coordinate
    color = self.expect_color()     # color value
    self.expect(TokenType.SEMICOLON)
    
    return PixelNode(x, y, color, line_num)
```

**LOOP statement** (handles nested statements!):
```python
def parse_loop(self) -> LoopNode:
    """
    Grammar: LOOP NUMBER LBRACE <statement>* RBRACE
    
    Example:
        LOOP 4 {
            PIXEL 10 10 #FF0000;
            RECT 20 20 10 10 #00FF00;
        }
    """
    line_num = self.current().line
    
    self.expect(TokenType.LOOP)
    count = self.expect_number()
    self.expect(TokenType.LBRACE)   # Opening brace
    
    # Parse statements inside the loop
    body = []
    while self.current().type != TokenType.RBRACE:
        body.append(self.parse_statement())
    
    self.expect(TokenType.RBRACE)   # Closing brace
    
    return LoopNode(count, body, line_num)
```

### Why This is Recursive Descent

Notice how `parse_loop()` calls `parse_statement()`, which might call `parse_loop()` again - this handles nested loops! The function calls go "down" into nested structures, then return back up.

```
parse_program()
  └── parse_statement()  // sees LOOP
       └── parse_loop()
            └── parse_statement()  // inside loop body
                 └── parse_pixel()
            └── parse_statement()  // another statement in loop
                 └── parse_rect()
```

---

## Phase 3: Semantic Analysis

**File**: `compiler/semantic.py`

### What is Semantic Analysis?

Syntax says "is this grammatically correct?" (e.g., "COLOR 10 10 #FF0000" - wrong keyword)

Semantics says "does this make sense?" (e.g., "CANVAS -100 100" - negative size doesn't make sense)

### The Semantic Rules

PixelLang has **37 semantic rules** that check for logical errors:

```
SEM-01: CANVAS must be first statement
SEM-02: CANVAS declared at most once  
SEM-03: Canvas dimensions positive
SEM-04: PIXEL x within bounds
SEM-05: PIXEL y within bounds
SEM-06: Color format valid #RRGGBB
SEM-07: Rectangle dimensions positive
SEM-08: Rectangle within bounds
...
SEM-37: Variable assignment exists
```

### Visitor Pattern

The semantic analyzer uses the **Visitor Pattern** - a design pattern where we separate operations from the data structure we operate on.

```python
class SemanticAnalyzer(NodeVisitor):
    """
    Walks through the AST and checks semantic rules.
    Collects ALL errors (doesn't stop at first).
    """
    
    def __init__(self):
        self.sym_table = SymbolTable()  # Track variables
        self.canvas_w = None            # Canvas width
        self.canvas_h = None            # Canvas height
        self.errors = []                # Collected errors
        self.canvas_seen = False
    
    def error(self, msg: str, line: int):
        """Record an error for later reporting."""
        self.errors.append(SemanticError(msg, line))
    
    def analyze(self, prog: ProgramNode) -> list[SemanticError]:
        """Entry point - returns list of all errors."""
        self.errors = []
        self.visit(prog)  # Start visiting from root
        return self.errors
```

### The Base Visitor Class

```python
class NodeVisitor:
    """
    Base visitor class. Automatically dispatches to visit_{NodeName} methods.
    """
    
    def visit(self, node: ASTNode):
        """Dynamically find and call the right visit method."""
        method_name = f"visit_{type(node).__name__}"
        visitor_fn = getattr(self, method_name, self.generic_visit)
        return visitor_fn(node)
```

### Example: Checking CANVAS Rules

```python
def visit_ProgramNode(self, node: ProgramNode):
    """SEM-01: CANVAS must be first statement."""
    if node.statements:
        first_stmt = node.statements[0]
        if not isinstance(first_stmt, CanvasNode):
            self.error(
                "CANVAS must be declared before any drawing command",
                first_stmt.line
            )
    
    # Visit all statements
    for stmt in node.statements:
        self.visit(stmt)

def visit_CanvasNode(self, node: CanvasNode):
    """
    SEM-02: CANVAS declared at most once.
    SEM-03: Canvas dimensions must be positive.
    """
    if self.canvas_seen:
        self.error(f"Duplicate CANVAS declaration", node.line)
    
    if node.width <= 0 or node.height <= 0:
        self.error("Canvas dimensions must be positive", node.line)
    
    self.canvas_w = node.width
    self.canvas_h = node.height
    self.canvas_seen = True
```

### Example: Checking Bounds

```python
def visit_PixelNode(self, node: PixelNode):
    """
    SEM-04: PIXEL x within bounds.
    SEM-05: PIXEL y within bounds.
    """
    if not self.canvas_seen:
        return  # Already reported by ProgramNode
    
    # Check x coordinate
    if not (0 <= node.x < self.canvas_w):
        self.error(
            f"PIXEL x={node.x} out of bounds (canvas width={self.canvas_w})",
            node.line
        )
    
    # Check y coordinate  
    if not (0 <= node.y < self.canvas_h):
        self.error(
            f"PIXEL y={node.y} out of bounds (canvas height={self.canvas_h})",
            node.line
        )
```

### Symbol Table

**File**: `compiler/symbol_table.py`

The symbol table tracks variables during compilation:

```python
class SymbolTable:
    """Tracks variable definitions."""
    
    def __init__(self):
        self.symbols = {}  # name -> {type, value, line}
    
    def define(self, name: str, kind: str, value, type_name: str, line: int):
        """Define a new symbol."""
        if name in self.symbols:
            raise SemanticError(f"Variable '{name}' already defined", line)
        
        self.symbols[name] = {
            'kind': kind,
            'value': value,
            'type': type_name,
            'line': line
        }
    
    def lookup(self, name: str):
        """Find a symbol by name."""
        return self.symbols.get(name)
```

---

## Phase 4: Code Generation

**File**: `compiler/codegen.py`

### What is Code Generation?

Code generation takes the validated AST and produces the final output - in PixelLang's case, a PNG image using the Pillow (PIL) library.

### The Code Generator

```python
from PIL import Image, ImageDraw

class CodeGenerator(NodeVisitor):
    """
    Walks the AST and draws to a PIL Image.
    """
    
    def __init__(self):
        self.image = None   # PIL Image object
        self.draw = None     # ImageDraw object
        
        # Transform state (for TRANSLATE, ROTATE, etc.)
        self.tx = 0         # Translation X
        self.ty = 0         # Translation Y
        self.angle = 0      # Rotation angle
    
    def generate(self, program: ProgramNode) -> Image.Image:
        """Generate image from AST."""
        self.visit(program)
        return self.image
```

### Drawing Commands

**CANVAS** - creates the image:
```python
def visit_CanvasNode(self, node: CanvasNode):
    """Create the image canvas."""
    self.image = Image.new("RGB", (node.width, node.height), "white")
    self.draw = ImageDraw.Draw(self.image)
```

**PIXEL** - draws a single point:
```python
def visit_PixelNode(self, node: PixelNode):
    """Draw a single pixel."""
    # Apply translation transform
    x, y = self.transform_point(node.x, node.y)
    self.draw.point((x, y), fill=node.color)

def transform_point(self, x: int, y: int) -> tuple:
    """Apply current translation to a point."""
    return (x + self.tx, y + self.ty)
```

**RECT** - draws a rectangle:
```python
def visit_RectNode(self, node: RectNode):
    """Draw a filled rectangle."""
    # Transform top-left corner
    x0, y0 = self.transform_point(node.x, node.y)
    # Calculate bottom-right
    x1, y1 = x0 + node.w, y0 + node.h
    # Draw
    self.draw.rectangle([x0, y0, x1, y1], fill=node.color)
```

**CIRCLE** - uses ellipse with equal radii:
```python
def visit_CircleNode(self, node: CircleNode):
    """Draw a filled circle."""
    cx, cy = self.transform_point(node.cx, node.cy)
    r = node.radius
    # Bounding box for circle
    bbox = [cx - r, cy - r, cx + r, cy + r]
    self.draw.ellipse(bbox, fill=node.color)
```

**FILL** - flood fill algorithm:
```python
def visit_FillNode(self, node: FillNode):
    """
    Flood fill using BFS (Breadth-First Search).
    Fills connected area of same color with new color.
    """
    x, y = self.transform_point(node.x, node.y)
    target_color = node.color
    
    # Get color at starting position
    seed_color = self.image.getpixel((x, y))
    
    # Convert colors to RGB tuples for comparison
    target_rgb = hex_to_rgb(target_color)
    seed_rgb = pixel_to_rgb(seed_color)
    
    # BFS flood fill
    from collections import deque
    queue = deque([(x, y)])
    visited = set([(x, y)])
    
    while queue:
        cx, cy = queue.popleft()
        
        # Color this pixel
        self.image.putpixel((cx, cy), target_rgb)
        
        # Check 4 neighbors (up, down, left, right)
        for nx, ny in [(cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1)]:
            if (nx, ny) not in visited:
                if 0 <= nx < width and 0 <= ny < height:
                    if self.image.getpixel((nx, ny)) == seed_rgb:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
```

### Handling LOOP (Transform Stack)

The key insight: `TRANSLATE` values accumulate inside loops!

```python
def visit_LoopNode(self, node: LoopNode):
    """
    Execute loop body 'count' times.
    TRANSLATE accumulates within the loop.
    """
    # Save transform state before loop
    saved_tx, saved_ty = self.tx, self.ty
    
    for _ in range(node.count):
        # Execute each statement in loop body
        for stmt in node.body:
            self.visit(stmt)
        # Note: tx, ty are NOT reset here - they accumulate!
    
    # Restore transform state after loop
    self.tx, self.ty = saved_tx, saved_ty
```

**Example of how this works**:
```pixel
CANVAS 100 100;
LOOP 4 {
    RECT 0 0 10 10 #FF0000;
    TRANSLATE 10 0;
}
```
This draws 4 rectangles at x=0, x=10, x=20, x=30 because `tx` accumulates!

---

## The Grammar Explained

### What is a Grammar?

A grammar defines the valid structure of programs. It's like the rules of a language.

### PixelLang's Full Grammar

```bnf
<program>       ::= <statement>* EOF

<statement>     ::= <canvas_stmt>
                  | <draw_stmt>
                  | <transform_stmt>
                  | <control_stmt>
                  | <advanced_stmt>
                  | <variable_stmt>

<canvas_stmt>   ::= CANVAS NUMBER NUMBER SEMICOLON

<draw_stmt>     ::= <pixel_stmt>
                  | <rect_stmt>
                  | <line_stmt>
                  | <circle_stmt>
                  | <ellipse_stmt>
                  | <triangle_stmt>
                  | <arc_stmt>
                  | <polygon_stmt>
                  | <border_stmt>
                  | <fill_stmt>
                  | <clear_stmt>
                  | <text_stmt>
                  | <star_stmt>
                  | <heart_stmt>
                  | <arrow_stmt>
                  | <roundrect_stmt>
                  | <bezier_stmt>
                  | <sprite_stmt>

<pixel_stmt>    ::= PIXEL NUMBER NUMBER COLOR SEMICOLON
<rect_stmt>     ::= RECT NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<line_stmt>     ::= LINE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<circle_stmt>   ::= CIRCLE NUMBER NUMBER NUMBER COLOR SEMICOLON
<ellipse_stmt>  ::= ELLIPSE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<triangle_stmt> ::= TRIANGLE NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<arc_stmt>      ::= ARC NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<polygon_stmt>  ::= POLYGON NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<border_stmt>   ::= BORDER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<fill_stmt>     ::= FILL NUMBER NUMBER COLOR SEMICOLON
<clear_stmt>    ::= CLEAR COLOR SEMICOLON
<text_stmt>     ::= TEXT NUMBER NUMBER (STRING | IDENT) COLOR SEMICOLON
<star_stmt>     ::= STAR NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<heart_stmt>    ::= HEART NUMBER NUMBER NUMBER COLOR SEMICOLON
<arrow_stmt>    ::= ARROW NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<roundrect_stmt>::= ROUNDRECT NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<bezier_stmt>   ::= BEZIER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<sprite_stmt>   ::= SPRITE NUMBER NUMBER IDENT COLOR SEMICOLON

<transform_stmt>::= <translate_stmt>
                  | <rotate_stmt>
                  | <scale_stmt>
                  | <mirror_stmt>

<translate_stmt>::= TRANSLATE NUMBER NUMBER SEMICOLON
<rotate_stmt>   ::= ROTATE NUMBER SEMICOLON
<scale_stmt>    ::= SCALE NUMBER SEMICOLON
<mirror_stmt>   ::= MIRROR NUMBER SEMICOLON

<control_stmt>  ::= <loop_stmt>
                  | <palette_stmt>
                  | <setpalette_stmt>
                  | <random_stmt>

<loop_stmt>     ::= LOOP NUMBER LBRACE <statement>* RBRACE
<palette_stmt>  ::= PALETTE NUMBER COLOR SEMICOLON
<setpalette_stmt>::= SETPALETTE NUMBER SEMICOLON
<random_stmt>   ::= RANDOM NUMBER NUMBER SEMICOLON

<variable_stmt> ::= <var_stmt>
                  | <set_stmt>

<var_stmt>      ::= VAR IDENT NUMBER SEMICOLON
<set_stmt>      ::= SET IDENT NUMBER SEMICOLON
```

### Grammar Notation Explained

| Symbol | Meaning | Example |
|--------|---------|---------|
| `<name>` | Non-terminal (rule name) | `<program>` |
| `::=` | "Is defined as" | `<a> ::= b` means "a is b" |
| `\|` | "Or" (alternative) | `a \| b` means "a or b" |
| `"text"` | Terminal (literal text) | `"CANVAS"` means the word CANVAS |
| `*` | Zero or more | `<stmt>*` means any number of statements |
| `()` | Grouping | `(a \| b) c` means "a or b, then c" |

---

## How Data Flows Through the Compiler

### Example: Compiling a Simple Program

**Source code**:
```pixel
CANVAS 50 50;
PIXEL 10 10 #FF0000;
RECT 20 20 10 10 #00FF00;
```

**Step 1: Lexical Analysis** (Lexer)
```
Input: "CANVAS 50 50;\nPIXEL 10 10 #FF0000;\nRECT 20 20 10 10 #00FF00;"

Output (Token List):
[
    Token(CANVAS, "CANVAS", line=1, col=1),
    Token(NUMBER, "50", line=1, col=8),
    Token(NUMBER, "50", line=1, col=11),
    Token(SEMICOLON, ";", line=1, col=13),
    Token(PIXEL, "PIXEL", line=2, col=1),
    Token(NUMBER, "10", line=2, col=7),
    Token(NUMBER, "10", line=2, col=10),
    Token(COLOR, "#FF0000", line=2, col=13),
    Token(SEMICOLON, ";", line=2, col=20),
    Token(RECT, "RECT", line=3, col=1),
    Token(NUMBER, "20", line=3, col=6),
    Token(NUMBER, "20", line=3, col=9),
    Token(NUMBER, "10", line=3, col=12),
    Token(NUMBER, "10", line=3, col=15),
    Token(COLOR, "#00FF00", line=3, col=18),
    Token(SEMICOLON, ";", line=3, col=25),
    Token(EOF, "", line=3, col=26)
]
```

**Step 2: Syntax Analysis** (Parser)
```
Input: Token List from Step 1

Output (AST):
ProgramNode
├── CanvasNode
│   ├── width: 50
│   ├── height: 50
│   └── line: 1
├── PixelNode
│   ├── x: 10
│   ├── y: 10
│   ├── color: "#FF0000"
│   └── line: 2
└── RectNode
    ├── x: 20
    ├── y: 20
    ├── w: 10
    ├── h: 10
    ├── color: "#00FF00"
    └── line: 3
```

**Step 3: Semantic Analysis** (SemanticAnalyzer)
```
Input: AST from Step 2

Checks:
✓ SEM-01: CANVAS is first statement
✓ SEM-02: Only one CANVAS
✓ SEM-03: Canvas dimensions positive (50 > 0)
✓ SEM-04: PIXEL x within bounds (10 < 50)
✓ SEM-05: PIXEL y within bounds (10 < 50)
✓ SEM-06: Color format valid (#FF0000)
✓ SEM-07: Rect dimensions positive (10 > 0)
✓ SEM-08: Rect within bounds (20+10=30 < 50)

Output: []  (Empty list = no errors!)
```

**Step 4: Code Generation** (CodeGenerator)
```
Input: Validated AST from Step 3

Execution:
1. visit_CanvasNode: Create 50x50 white image
2. visit_PixelNode: Draw red pixel at (10,10)
3. visit_RectNode: Draw green rectangle from (20,20) to (30,30)

Output: 50x50 PNG image with red pixel and green rectangle!
```

### Complete Compilation Flow Diagram

```
┌─────────────────┐
│   Source Code   │  .px file (text)
│  CANVAS 50 50;  │
│  PIXEL 10...    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      Lexer      │  DFA-based tokenizer
│                 │  • Reads char by char
│  ┌───────────┐  │  • Matches patterns
│  │ read_word │  │  • Creates tokens
│  │read_number│  │
│  │read_color │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Token List    │  [CANVAS, 50, 50, ;, PIXEL, 10...]
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Parser      │  LL(1) Recursive Descent
│                 │  • LL(1) dispatch
│  ┌───────────┐  │  • Builds AST nodes
│  │parse_canvas│  │  • Grammar validation
│  │parse_pixel│  │
│  │ parse_rect│  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│       AST       │  Tree structure
│                 │  ProgramNode
│   ProgramNode   │  ├── CanvasNode
│   ├─ Canvas     │  ├── PixelNode
│   ├─ Pixel      │  └── RectNode
│   └─ Rect       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│SemanticAnalyzer │  Visitor pattern
│                 │  • 37 validation rules
│  ┌───────────┐  │  • Bounds checking
│  │visit_canvas│  │  • Type checking
│  │visit_pixel │  │  • Symbol table
│  │ visit_rect │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validated AST  │  Same structure, now verified
│   (or errors)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CodeGenerator  │  Visitor pattern
│                 │  • PIL/Pillow drawing
│  ┌───────────┐  │  • Transform stack
│  │visit_canvas│  │  • Loop handling
│  │visit_pixel │  │
│  │ visit_rect │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PNG Image     │  Output file!
│   50x50 pixels  │
└─────────────────┘
```

---

## Key Concepts Summary

| Concept | Explanation | File |
|---------|-------------|------|
| **Token** | Smallest meaningful unit (keyword, number, color) | `tokens.py` |
| **DFA** | State machine that recognizes token patterns | `lexer.py` |
| **AST** | Tree structure representing program structure | `ast_nodes.py` |
| **BNF** | Grammar notation defining valid syntax | `parser.py` (comments) |
| **LL(1)** | Parsing technique: Left-to-right, Leftmost, 1 lookahead | `parser.py` |
| **Visitor Pattern** | Separates operations from data structure | `semantic.py`, `codegen.py` |
| **Symbol Table** | Tracks variables during compilation | `symbol_table.py` |
| **Semantic Rules** | Logical validation (bounds, types, etc.) | `semantic.py` |
| **Transform Stack** | Saves/restores state for loops | `codegen.py` |

---

## Tips for Understanding the Code

1. **Start with `examples/`** - Look at .px files to see what the language does
2. **Read `tokens.py` first** - Understand what tokens exist
3. **Trace through `lexer.py`** - See how text becomes tokens
4. **Study the grammar in `parser.py`** - Understand the syntax rules
5. **Look at `ast_nodes.py`** - See the data structures
6. **Understand `semantic.py`** - See how validation works
7. **Finally, `codegen.py`** - See how images are created

---

*Happy learning! PixelLang is a complete compiler implementing all classical phases, making it a great learning resource for compiler construction.*
