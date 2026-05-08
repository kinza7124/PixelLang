"""
PixelLang Compiler
===================
A complete compiler for the PixelLang domain-specific language.
Compiles .px source files into PNG pixel art images.

Phases:
1. Lexical Analysis (lexer.py) - Tokenizes source code
2. Syntax Analysis (parser.py) - Builds AST from tokens (LL(1) grammar)
3. Semantic Analysis (semantic.py) - Checks 13 semantic rules
4. Code Generation (codegen.py) - Generates PNG using Pillow

Usage:
    from compiler import compile_source, compile_file
    
    # Compile from string
    image, errors = compile_source(source_code)
    
    # Compile from file
    image, errors = compile_file("program.px")
"""
from .tokens import Token, TokenType
from .lexer import Lexer, lex
from .parser import Parser, parse
from .ast_nodes import *
from .semantic import SemanticAnalyzer, analyze
from .codegen import CodeGenerator, generate
from .optimizer import optimize
from .ast_printer import ASTFormatter, pretty_print
from .errors import PixelLangError
from .symbol_table import SymbolTable, Symbol


def compile_source(source: str) -> tuple:
    """
    Compile PixelLang source code through all phases.
    
    Args:
        source: The PixelLang source code string
        
    Returns:
        tuple: (PIL.Image.Image | None, list[str])
               - Image if successful, None if errors occurred
               - List of error messages (empty if successful)
    """
    errors = []
    
    try:
        # Phase 1: Lexical Analysis
        try:
            tokens = lex(source)
        except PixelLangError as e:
            return None, [str(e)]
        
        # Phase 2: Syntax Analysis
        try:
            ast = parse(tokens)
        except PixelLangError as e:
            return None, [str(e)]
        
        # Phase 3: Semantic Analysis
        semantic_errors = analyze(ast)
        if semantic_errors:
            return None, [str(e) for e in semantic_errors]

        # Optional Phase: AST Optimizations (safe, semantics-preserving)
        try:
            ast = optimize(ast)
        except Exception:
            # If optimization fails for any reason, fall back to original AST
            pass

        # Phase 4: Code Generation
        try:
            image = generate(ast)
        except PixelLangError as e:
            return None, [str(e)]
        
        return image, []
        
    except Exception as e:
        # Catch any unexpected errors
        return None, [f"Internal compiler error: {str(e)}"]


def compile_file(filepath: str) -> tuple:
    """
    Compile a PixelLang source file.
    
    Args:
        filepath: Path to .px source file
        
    Returns:
        tuple: (PIL.Image.Image | None, list[str])
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        return compile_source(source)
    except FileNotFoundError:
        return None, [f"File not found: {filepath}"]
    except IOError as e:
        return None, [f"Error reading file: {e}"]


# Export public API
__all__ = [
    'compile_source',
    'compile_file',
    'Token',
    'TokenType',
    'Lexer',
    'lex',
    'Parser',
    'parse',
    'ASTNode',
    'ProgramNode',
    'CanvasNode',
    'PixelNode',
    'RectNode',
    'LineNode',
    'CircleNode',
    'FillNode',
    'EllipseNode',
    'ClearNode',
    'BorderNode',
    'TriangleNode',
    'ArcNode',
    'PolygonNode',
    'TextNode',
    'MirrorNode',
    'ScaleNode',
    'LoopNode',
    'TranslateNode',
    'RotateNode',
    # v2.0 Advanced Nodes
    'BezierNode',
    'StarNode',
    'RoundRectNode',
    'HeartNode',
    'ArrowNode',
    'PaletteNode',
    'SetPaletteNode',
    'SpriteNode',
    'RandomNode',
    'VarNode',
    'SetNode',
    'NodeVisitor',
    'ASTPrinter',
    'SemanticAnalyzer',
    'analyze',
    'optimize',
    'ASTFormatter',
    'pretty_print',
    'CodeGenerator',
    'generate',
    'PixelLangError',
    'LexError',
    'ParseError',
    'SemanticError',
    'CodeGenError',
    'SymbolTable',
    'Symbol',
]
