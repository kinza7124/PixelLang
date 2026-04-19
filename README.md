# PixelLang Compiler

A complete compiler construction course project implementing a domain-specific language for pixel art generation. Built for CS4031 Compiler Construction.

## Overview

PixelLang is a retro-inspired scripting language that compiles `.px` source files into PNG images. The compiler implements all classical phases of compilation with a full GUI IDE.

## Features

- **30+ Drawing Keywords**: CANVAS, PIXEL, RECT, LINE, CIRCLE, FILL, ELLIPSE, CLEAR, BORDER, TRIANGLE, ARC, POLYGON, TEXT, MIRROR, SCALE, LOOP, TRANSLATE, ROTATE
- **v2.0 Advanced Features**:
  - **BEZIER**: Cubic bezier curves for smooth lines
  - **STAR**: Multi-point star shapes with inner/outer radius
  - **ROUNDRECT**: Rectangles with rounded corners
  - **HEART**: Heart shapes for decorative art
  - **ARROW**: Lines with arrowheads
  - **PALETTE**: Color palette management (16 colors)
  - **SETPALETTE**: Switch active palette color
  - **SPRITE**: Binary pattern sprites for icons/pixel art
  - **RANDOM**: Random number generation for generative art
  - **VAR/SET**: Variable definition and assignment
- **Core Features**:
  - **FILL**: Flood fill from any position
  - **ELLIPSE**: Draw ellipses with different x/y radii
  - **CLEAR**: Fill entire canvas with color
  - **BORDER**: Draw hollow rectangle borders
  - **TRIANGLE**: Draw filled triangles
  - **ARC**: Draw circular arcs with start/end angles
  - **POLYGON**: Draw 4-point polygons (quads)
  - **TEXT**: Draw pixel-based text (uppercase A-Z, 0-9)
  - **MIRROR**: Flip/mirror drawing context
  - **SCALE**: Scale drawing context
  - **UNDO/REDO**: Editor history (Ctrl+Z/Ctrl+Y)
  - **Grid Overlay**: Toggle pixel grid in preview
- **Complete Compiler Pipeline**:
  1. Lexical Analysis (DFA-based tokenizer)
  2. Syntax Analysis (LL(1) recursive descent parser)
  3. **Semantic Analysis** (26 semantic rules)
  4. Code Generation (Pillow/PIL backend)
- **Tkinter GUI IDE** with:
  - Syntax highlighting
  - Line numbers
  - Error navigation
  - Live preview with zoom
  - Save/Load functionality

## Quick Start

### Running the GUI IDE
```bash
python main.py
```

### Compiling a .px file
```bash
python main.py program.px
```

### Running tests
```bash
python main.py --test
```

## Language Syntax

### Basic Program Structure
```pixel
CANVAS width height;
// drawing commands
```

### Drawing Commands
```pixel
PIXEL x y #COLOR;                      // Draw single pixel
RECT x y w h #COLOR;                   // Draw filled rectangle
LINE x1 y1 x2 y2 #COLOR;               // Draw line
CIRCLE cx cy r #COLOR;                 // Draw filled circle
FILL x y #COLOR;                       // Flood fill from position
ELLIPSE cx cy rx ry #COLOR;            // Draw filled ellipse
CLEAR #COLOR;                          // Fill entire canvas with color
BORDER x y w h t #COLOR;               // Draw hollow rectangle border (t=thickness)
TRIANGLE x1 y1 x2 y2 x3 y3 #C;        // Draw filled triangle
ARC cx cy r start end #COLOR;         // Draw circular arc (angles 0-360)
POLYGON x1 y1 x2 y2 x3 y3 x4 y4 #C;  // Draw 4-point polygon
TEXT x y string #COLOR;                // Draw text (uppercase, use IDENT)
MIRROR axis;                          // Flip: 0=horizontal, 1=vertical
SCALE factor;                         // Scale drawing (1-10)
TRANSLATE dx dy;                      // Shift drawing origin
ROTATE angle;                         // Rotate context (0-360)

// v2.0 Advanced Commands
BEZIER x1 y1 cx1 cy1 cx2 cy2 x2 y2 #C; // Cubic bezier curve
STAR cx cy outer inner points #COLOR;  // Star with n points
ROUNDRECT x y w h radius #COLOR;       // Rectangle with rounded corners
HEART cx cy size #COLOR;               // Heart shape
ARROW x1 y1 x2 y2 head_size #COLOR;  // Arrow with arrowhead
PALETTE idx #COLOR;                    // Define palette color (idx 0-15)
SETPALETTE idx;                        // Set active palette color
SPRITE x y pattern #COLOR;             // Draw binary pattern (e.g., 101010)
RANDOM min max;                        // Generate random number
VAR name value;                        // Define variable
SET name value;                        // Update variable
```

### Loops
```pixel
LOOP n {
    // statements to repeat n times
}
```

### Example Program
```pixel
// Rainbow pattern
CANVAS 64 64;

// Background
RECT 0 0 64 64 #1A1A2A;

// Diagonal rainbow dots
LOOP 8 {
    PIXEL 0 0 #FF0000;
    TRANSLATE 4 4;
}
```

## Project Structure

```
PixelLang/
├── compiler/
│   ├── __init__.py          # Main compiler API
│   ├── errors.py            # Error classes
│   ├── tokens.py            # Token definitions
│   ├── lexer.py             # Lexical analyzer (DFA)
│   ├── parser.py            # Syntax analyzer (LL(1))
│   ├── ast_nodes.py         # AST node classes
│   ├── symbol_table.py      # Scoped symbol table
│   ├── semantic.py          # Semantic analyzer
│   ├── codegen.py           # Code generator
│   └── gui/
│       ├── __init__.py
│       └── app.py           # Tkinter IDE
├── tests/
│   └── test_compiler.py     # Test suite
├── examples/
│   ├── checkerboard.px
│   ├── smiley.px
│   ├── diagonal_rainbow.px
│   ├── advanced_shapes_demo.px
│   ├── v2_features_demo.px      // New v2.0 features showcase
│   ├── generative_art.px        // Random and sprites demo
│   └── palette_demo.px          // Color palette demo
├── main.py                  # Entry point
└── README.md
```

## Compiler Phases

### 1. Lexical Analysis (lexer.py)
DFA-based tokenizer that recognizes:
- 30+ keywords including all drawing commands
- Numbers: `[0-9]+`
- Colors: `#[0-9A-Fa-f]{6}`
- Binary patterns for SPRITE: `[01]{4,16}`
- Identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`
- Punctuation: `{`, `}`, `;`

### 2. Syntax Analysis (parser.py)
LL(1) recursive descent parser implementing:
```bnf
<program>   ::= <statement>* EOF
<statement> ::= <canvas_stmt> | <pixel_stmt> | ...
<canvas>    ::= CANVAS NUMBER NUMBER SEMICOLON
<pixel>     ::= PIXEL NUMBER NUMBER COLOR SEMICOLON
<rect>      ::= RECT NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
<loop>      ::= LOOP NUMBER LBRACE <statement>* RBRACE
```

### 3. Semantic Analysis (semantic.py)
37 semantic rules:
- SEM-01: CANVAS must be first statement
- SEM-02: CANVAS at most once
- SEM-03: Canvas dimensions positive
- SEM-04/05: Pixel coordinates within bounds
- SEM-06: Valid color format
- SEM-07/08: Rectangle validation
- SEM-09: Line bounds checking
- SEM-10/11: Circle validation
- SEM-12: Loop count positive
- SEM-13: Rotation angle 0-360
- SEM-27: Bezier curve bounds checking
- SEM-28: Star shape validation
- SEM-29: Rounded rectangle validation
- SEM-30: Heart shape validation
- SEM-31: Arrow bounds checking
- SEM-32/33: Palette index validation (0-15)
- SEM-34: Sprite pattern validation
- SEM-35: Random range validation
- SEM-36/37: Variable definition and assignment

### 4. Code Generation (codegen.py)
Pillow-based renderer with:
- Transform stack for LOOP enter/exit
- TRANSLATE accumulation for patterns
- PNG output

## Dependencies

- Python 3.8+
- Pillow (PIL)
- Tkinter (usually included with Python)

Install Pillow:
```bash
pip install Pillow
```

## Running Tests

```bash
python -m tests.test_compiler
# or
python main.py --test
```

## Sample Programs

### Checkerboard Pattern
```pixel
CANVAS 32 32;
RECT 0 0 32 32 #FFFFFF;
LOOP 4 {
    LOOP 4 {
        RECT 0 0 4 4 #000000;
        TRANSLATE 8 0;
    }
    TRANSLATE -32 4;
    TRANSLATE 4 0;
}
```

### Smiley Face
```pixel
CANVAS 50 50;
CIRCLE 25 25 20 #FFEB3B;  // Face
CIRCLE 18 18 5 #FFFFFF;    // Left eye white
CIRCLE 32 18 5 #FFFFFF;    // Right eye white
CIRCLE 18 18 2 #000000;    // Left pupil
CIRCLE 32 18 2 #000000;    // Right pupil
// ... mouth pixels
```

## GUI Features

- **Editor**: Syntax highlighting with color-coded keywords, colors, numbers, and comments
- **Line Numbers**: Auto-updating gutter
- **Error Panel**: Click errors to jump to line
- **Preview**: Live image preview with zoom controls (Ctrl++, Ctrl+-)
- **Keyboard Shortcuts**:
  - `Ctrl+Return` - Compile & Run
  - `Ctrl+N` - New file
  - `Ctrl+O` - Open file
  - `Ctrl+S` - Save file
  - `Ctrl+Z` - Undo
  - `Ctrl+Y` - Redo
  - `Ctrl++` - Zoom in
  - `Ctrl+-` - Zoom out

## Error Handling

Four error types with line/column information:
- **LexError**: Invalid characters, malformed tokens
- **ParseError**: Grammar violations
- **SemanticError**: Bounds, type, and scope violations
- **CodeGenError**: Image generation failures

## Academic Information

- **Course**: CS4031 Compiler Construction
- **Project**: PixelLang Domain-Specific Language
- **Grammar Type**: LL(1) Context-Free Grammar
- **Parser**: Recursive Descent (Top-down)
- **Sematic Model**: Scoped symbol table with visitor pattern

## License

This project is for educational purposes as part of the Compiler Construction course.
