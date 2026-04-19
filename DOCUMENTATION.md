# PixelLang Compiler Documentation

## 1. Formal Grammar (BNF)

PixelLang uses a Context-Free Grammar (CFG) expressed in Backus-Naur Form.

```bnf
<program>       ::= <statement>* EOF

<statement>     ::= <canvas_stmt>
                 |  <pixel_stmt>
                 |  <rect_stmt>
                 |  <line_stmt>
                 |  <circle_stmt>
                 |  <loop_stmt>
                 |  <translate_stmt>
                 |  <rotate_stmt>

<canvas_stmt>   ::= CANVAS NUMBER NUMBER SEMICOLON
<pixel_stmt>    ::= PIXEL NUMBER NUMBER COLOR SEMICOLON
<rect_stmt>     ::= RECT NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<line_stmt>     ::= LINE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<circle_stmt>   ::= CIRCLE NUMBER NUMBER NUMBER COLOR SEMICOLON
<loop_stmt>     ::= LOOP NUMBER LBRACE <statement>* RBRACE
<translate_stmt>::= TRANSLATE NUMBER NUMBER SEMICOLON
<rotate_stmt>   ::= ROTATE NUMBER SEMICOLON
```

### Terminals
```bnf
NUMBER      ::= [0-9]+
COLOR       ::= '#' [0-9A-Fa-f]{6}
CANVAS      ::= "CANVAS"
PIXEL       ::= "PIXEL"
RECT        ::= "RECT"
LINE        ::= "LINE"
CIRCLE      ::= "CIRCLE"
LOOP        ::= "LOOP"
TRANSLATE   ::= "TRANSLATE"
ROTATE      ::= "ROTATE"
LBRACE      ::= '{'
RBRACE      ::= '}'
SEMICOLON   ::= ';'
EOF         ::= end-of-input
```

## 2. LL(1) Grammar Properties

| Property | Value |
|----------|-------|
| Grammar Type | Context-Free Grammar (CFG) - Type 2 |
| Parser Class | LL(1) - Top-down, left-to-right, 1-token lookahead |
| Ambiguous? | No - each statement starts with unique keyword |
| Left-Recursive? | No - safe for recursive descent |
| Productions | 10 (1 program + 1 statement + 8 stmt rules) |
| Non-terminals | 10 |
| Terminals | 15 (8 keywords + NUMBER + COLOR + { } ; EOF) |

## 3. FIRST and FOLLOW Sets

### FIRST Sets

| Non-terminal | FIRST Set |
|--------------|-----------|
| FIRST(program) | {CANVAS, PIXEL, RECT, LINE, CIRCLE, LOOP, TRANSLATE, ROTATE, EOF} |
| FIRST(statement) | {CANVAS, PIXEL, RECT, LINE, CIRCLE, LOOP, TRANSLATE, ROTATE} |
| FIRST(canvas_stmt) | {CANVAS} |
| FIRST(pixel_stmt) | {PIXEL} |
| FIRST(rect_stmt) | {RECT} |
| FIRST(line_stmt) | {LINE} |
| FIRST(circle_stmt) | {CIRCLE} |
| FIRST(loop_stmt) | {LOOP} |
| FIRST(translate_stmt) | {TRANSLATE} |
| FIRST(rotate_stmt) | {ROTATE} |

### FOLLOW Sets

| Non-terminal | FOLLOW Set |
|--------------|------------|
| FOLLOW(program) | {EOF} |
| FOLLOW(statement) | {CANVAS, PIXEL, RECT, LINE, CIRCLE, LOOP, TRANSLATE, ROTATE, RBRACE, EOF} |
| FOLLOW(canvas_stmt) | = FOLLOW(statement) |
| FOLLOW(pixel_stmt) | = FOLLOW(statement) |
| FOLLOW(rect_stmt) | = FOLLOW(statement) |
| FOLLOW(line_stmt) | = FOLLOW(statement) |
| FOLLOW(circle_stmt) | = FOLLOW(statement) |
| FOLLOW(loop_stmt) | = FOLLOW(statement) |
| FOLLOW(translate_stmt) | = FOLLOW(statement) |
| FOLLOW(rotate_stmt) | = FOLLOW(statement) |

### LL(1) Condition Verification

For every non-terminal A with multiple productions A → α | β:
- FIRST(α) ∩ FIRST(β) = ∅ (must be disjoint)

In PixelLang, every statement alternative begins with a distinct keyword,
so all FIRST sets are disjoint, confirming the grammar is LL(1).

## 4. LL(1) Parse Table

| Non-terminal | CANVAS | PIXEL | RECT | LINE | CIRCLE | LOOP | TRANSLATE | ROTATE | RBRACE | EOF |
|--------------|--------|-------|------|------|--------|------|-----------|--------|--------|-----|
| program | statement* | statement* | statement* | statement* | statement* | statement* | statement* | statement* | - | ε |
| statement | canvas_stmt | pixel_stmt | rect_stmt | line_stmt | circle_stmt | loop_stmt | translate_stmt | rotate_stmt | error | error |
| canvas_stmt | CANVAS N N ; | - | - | - | - | - | - | - | error | error |
| pixel_stmt | - | PIXEL N N C ; | - | - | - | - | - | - | error | error |
| rect_stmt | - | - | RECT N N N N C ; | - | - | - | - | - | error | error |
| line_stmt | - | - | - | LINE N N N N C ; | - | - | - | - | error | error |
| circle_stmt | - | - | - | - | CIRCLE N N N C ; | - | - | - | error | error |
| loop_stmt | - | - | - | - | - | LOOP N { S* } | - | - | error | error |
| translate_stmt | - | - | - | - | - | - | TRANSLATE N N ; | - | error | error |
| rotate_stmt | - | - | - | - | - | - | - | ROTATE N ; | error | error |

## 5. DFA Diagrams for Lexer

### Main Lexer DFA

```
                    [a-zA-Z_]
                       |
                       v
    q0 (start) ---> read_word() ---> TOKEN (keyword or IDENT)
         |
         | [0-9]
         v
      read_number() ---> NUMBER
         |
         | [#]
         v
      read_color() ---> COLOR
         |
         | [{]
         v
       emit LBRACE
         |
         | [}]
         v
       emit RBRACE
         |
         | [;]
         v
      emit SEMICOLON
         |
         | [/][/]
         v
      skip_comment() ---> q0 (restart)
         |
         | [ \t\n\r]
         v
      skip_whitespace() ---> q0 (restart)
         |
         | [EOF]
         v
       emit EOF
         |
         | [other]
         v
      LexError
```

### DFA for NUMBER Token

```
    [digit]          [digit]
   ┌──────┐          ┌──────┐
   |      v          |      ^
   |    ┌───┐        |    ┌───┐
   +--->| q0|--------+--->| q1|---+
        |   |             |   |   |
        +---+             +---+   |
                              [other]
                                 |
                                 v
                            ACCEPT (emit NUMBER)
```

### DFA for COLOR Token

```
    [#]    [hex]   [hex]   [hex]   [hex]   [hex]
   ┌──┐    ┌──┐    ┌──┐    ┌──┐    ┌──┐    ┌──┐
   |  v    |  v    |  v    |  v    |  v    |  v
   | q1--->| q2--->| q3--->| q4--->| q5--->| q6|
   |       |       |       |       |       |  |
   +       +       +       +       +       +  |
                                               | [hex]
                                               v
                                            ┌───┐
                                            | q7| ---> ACCEPT (emit COLOR)
                                            +---+
```

### DFA for WORD (Keyword/Identifier)

```
  [a-zA-Z_]        [letter|digit|_]
     |                     ^
     v                     |
   ┌───┐                   |
   | q0|--+--------------+
   +---+  |
          | [letter|digit|_]
          v
        ┌───┐
        | q1|-----------------> ACCEPT
        +---+    [other]         |
                     |           |
                     v           |
            ┌──────────┐        |
            | Check    |        |
            | RESERVED |--------+
            | _WORDS   |
            +----------+
                 |
           in dict?  Yes -> emit keyword
           No -> emit IDENT
```

## 6. Semantic Rules (13 Total)

| Rule ID | Statement | Condition Checked | Error Message |
|---------|-----------|-------------------|---------------|
| SEM-01 | program | CANVAS must be first statement | "CANVAS must be declared before any drawing command" |
| SEM-02 | CANVAS | CANVAS declared at most once | "Duplicate CANVAS declaration at line N" |
| SEM-03 | CANVAS | width > 0 AND height > 0 | "Canvas dimensions must be positive integers" |
| SEM-04 | PIXEL | 0 ≤ x ≤ canvas_width − 1 | "PIXEL x={x} out of bounds (canvas width={w})" |
| SEM-05 | PIXEL | 0 ≤ y ≤ canvas_height − 1 | "PIXEL y={y} out of bounds (canvas height={h})" |
| SEM-06 | PIXEL/RECT/LINE/CIRCLE | color matches ^#[0-9A-Fa-f]{6}$ | "Invalid color '{c}' — must be #RRGGBB format" |
| SEM-07 | RECT | w > 0 AND h > 0 | "Rectangle dimensions must be positive" |
| SEM-08 | RECT | x+w ≤ canvas_width AND y+h ≤ canvas_height | "Rectangle extends outside canvas bounds" |
| SEM-09 | LINE | 0 ≤ x1,x2 < width AND 0 ≤ y1,y2 < height | "LINE endpoint out of canvas bounds" |
| SEM-10 | CIRCLE | radius > 0 | "Circle radius must be a positive integer" |
| SEM-11 | CIRCLE | cx−r ≥ 0 AND cx+r < width AND cy−r ≥ 0 AND cy+r < height | "Circle extends outside canvas bounds" |
| SEM-12 | LOOP | count > 0 | "Loop count must be a positive integer (got {n})" |
| SEM-13 | ROTATE | 0 ≤ angle ≤ 360 | "ROTATE angle must be 0–360 (got {a})" |

## 7. Symbol Table Design

### Symbol Structure
```python
@dataclass
class Symbol:
    name: str        # "canvas", "tx", "ty", "angle", "loop_i"
    kind: str        # "canvas", "transform", "loop_counter"
    value: any       # Current value
    value_type: str  # "int", "tuple", "color"
    defined_at: int  # Source line number
    scope_depth: int # 0 = global, 1 = loop1, ...
```

### Scope Management
- Stack-based scoped symbol table
- New scope pushed on LOOP entry
- Scope popped on LOOP exit
- Lookup searches innermost to outermost

### Built-in Symbols
| Symbol | When Defined | When Updated | When Destroyed |
|--------|--------------|--------------|----------------|
| canvas | CANVAS statement | Never | End of program |
| tx, ty | Program start (init=0) | TRANSLATE accumulates | End of program |
| angle | Program start (init=0) | ROTATE statement | End of program |
| loop_count | LOOP entry | Never | LOOP exit |
| loop_iter | LOOP entry | Each iteration | LOOP exit |

## 8. Code Generation Strategy

### Transform Stack
```python
# On LOOP entry:
tx_stack.append(tx)
ty_stack.append(ty)

# During loop iterations:
tx += dx  # TRANSLATE accumulates

# On LOOP exit:
tx = tx_stack.pop()
ty = ty_stack.pop()
```

### PIL/Pillow Mapping
| PixelLang | PIL Operation |
|-----------|---------------|
| CANVAS w h | Image.new("RGB", (w,h), "white") |
| PIXEL x y #c | draw.point((x,y), fill=#c) |
| RECT x y w h #c | draw.rectangle([x,y,x+w,y+h], fill=#c) |
| LINE x1 y1 x2 y2 #c | draw.line([(x1,y1),(x2,y2)], fill=#c, width=1) |
| CIRCLE cx cy r #c | draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=#c) |

## 9. Compilation Pipeline

```
Source.px
    |
    v
+--------+
| Lexer  |  ---> DFA tokenization
+--------+
    |
    v
Tokens [CANVAS, NUMBER(32), NUMBER(32), SEMICOLON, ...]
    |
    v
+--------+
| Parser |  ---> LL(1) recursive descent
+--------+
    |
    v
AST (ProgramNode -> [CanvasNode, PixelNode, ...])
    |
    v
+----------+
| Semantic | ---> Visitor pattern, 13 rules
+----------+
    |
    v
[] or [SemanticError, ...]
    |
    v
+---------+
| CodeGen | ---> Visitor pattern, PIL backend
+---------+
    |
    v
PIL.Image ---> PNG output
```

## 10. Error Classes

```python
class LexError(PixelLangError):
    message: str
    line: int
    col: int

class ParseError(PixelLangError):
    message: str
    line: int
    col: int

class SemanticError(PixelLangError):
    message: str
    line: int

class CodeGenError(PixelLangError):
    message: str
```

All errors include line numbers for GUI highlighting.
