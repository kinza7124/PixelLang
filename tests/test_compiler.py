"""
PixelLang Compiler Test Suite
==============================
Tests for all compiler phases:
1. Lexer tests
2. Parser tests  
3. Semantic analyzer tests
4. Code generator tests
5. Integration tests
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler import lex, parse, analyze, generate, compile_source
from compiler.errors import LexError, ParseError, SemanticError
from compiler.tokens import TokenType


def test_lexer():
    """Test lexical analysis."""
    print("Testing Lexer...")
    
    # Test 1: Basic tokens
    source = "CANVAS 32 32;"
    tokens = lex(source)
    assert len(tokens) == 5  # CANVAS, 32, 32, ;, EOF
    assert tokens[0].type == TokenType.CANVAS
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].value == "32"
    assert tokens[4].type == TokenType.EOF
    print("  ✓ Basic tokenization")
    
    # Test 2: Color literal
    source = "PIXEL 0 0 #FF0000;"
    tokens = lex(source)
    assert tokens[3].type == TokenType.COLOR
    assert tokens[3].value == "#FF0000"
    print("  ✓ Color literal tokenization")
    
    # Test 3: Loop with braces
    source = "LOOP 3 { PIXEL 0 0 #00FF00; }"
    tokens = lex(source)
    assert any(t.type == TokenType.LBRACE for t in tokens)
    assert any(t.type == TokenType.RBRACE for t in tokens)
    print("  ✓ Brace tokenization")
    
    # Test 4: Comments are skipped
    source = "CANVAS 10 10; // this is a comment\nPIXEL 0 0 #000000;"
    tokens = lex(source)
    assert not any(t.value == "//" for t in tokens)
    print("  ✓ Comments skipped")
    
    # Test 5: Unknown character raises error
    try:
        lex("CANVAS 10 10; @")
        assert False, "Should have raised LexError"
    except LexError:
        pass
    print("  ✓ Unknown character error")
    
    print("Lexer tests passed!\n")


def test_parser():
    """Test syntax analysis."""
    print("Testing Parser...")
    
    # Test 1: Basic program
    source = """
CANVAS 32 32;
PIXEL 10 10 #FF0000;
"""
    tokens = lex(source)
    ast = parse(tokens)
    assert len(ast.statements) == 2
    print("  ✓ Basic program parsing")
    
    # Test 2: Loop parsing
    source = """
CANVAS 20 20;
LOOP 3 {
    PIXEL 0 0 #00FF00;
    TRANSLATE 1 1;
}
"""
    tokens = lex(source)
    ast = parse(tokens)
    loop = ast.statements[1]
    assert loop.count == 3
    assert len(loop.body) == 2
    print("  ✓ Loop parsing")
    
    # Test 3: All statement types
    source = """
CANVAS 50 50;
PIXEL 0 0 #FF0000;
RECT 0 0 10 10 #00FF00;
LINE 0 0 10 10 #0000FF;
CIRCLE 25 25 5 #FFFFFF;
TRANSLATE 5 5;
ROTATE 45;
"""
    tokens = lex(source)
    ast = parse(tokens)
    assert len(ast.statements) == 7
    print("  ✓ All statement types parsing")
    
    # Test 4: Missing semicolon error
    try:
        tokens = lex("CANVAS 10 10\nPIXEL 0 0 #FF0000;")
        parse(tokens)
        assert False, "Should have raised ParseError"
    except ParseError:
        pass
    print("  ✓ Missing semicolon error")
    
    print("Parser tests passed!\n")


def test_semantic():
    """Test semantic analysis."""
    print("Testing Semantic Analyzer...")
    
    # Test 1: CANVAS must be first
    source = """
PIXEL 0 0 #FF0000;
CANVAS 10 10;
"""
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert len(errors) > 0
    assert "CANVAS must be" in str(errors[0])
    print("  ✓ CANVAS first rule (SEM-01)")
    
    # Test 2: Duplicate CANVAS
    source = """
CANVAS 10 10;
CANVAS 20 20;
"""
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert any("Duplicate" in str(e) for e in errors)
    print("  ✓ Duplicate CANVAS rule (SEM-02)")
    
    # Test 3: Positive canvas dimensions
    source = "CANVAS 0 10;"
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert any("positive" in str(e) for e in errors)
    print("  ✓ Positive dimensions rule (SEM-03)")
    
    # Test 4: Pixel bounds checking
    source = """
CANVAS 10 10;
PIXEL 20 20 #FF0000;
"""
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert any("out of bounds" in str(e) for e in errors)
    print("  ✓ Pixel bounds rule (SEM-04/05)")
    
    # Test 5: Loop count positive
    source = """
CANVAS 20 20;
LOOP 0 {
    PIXEL 0 0 #FF0000;
}
"""
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert any("Loop count" in str(e) for e in errors)
    print("  ✓ Loop count rule (SEM-12)")
    
    # Test 6: Valid program has no errors
    source = """
CANVAS 32 32;
RECT 0 0 32 32 #222222;
CIRCLE 16 16 5 #FF0000;
"""
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert len(errors) == 0
    print("  ✓ Valid program passes semantic analysis")
    
    # Test 7: FILL bounds checking
    source = """
CANVAS 10 10;
FILL 20 20 #FF0000;
"""
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert any("out of bounds" in str(e) for e in errors)
    print("  ✓ FILL bounds rule (SEM-14)")
    
    # Test 8: FILL valid program
    source = """
CANVAS 16 16;
RECT 0 0 16 16 #FFFFFF;
FILL 5 5 #FF0000;
"""
    tokens = lex(source)
    ast = parse(tokens)
    errors = analyze(ast)
    assert len(errors) == 0
    print("  ✓ FILL command passes semantic analysis")
    
    print("Semantic analyzer tests passed!\n")


def test_codegen():
    """Test code generation."""
    print("Testing Code Generator...")
    
    # Test 1: Basic image generation
    source = """
CANVAS 10 10;
PIXEL 5 5 #FF0000;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    assert image.size == (10, 10)
    print("  ✓ Basic image generation")
    
    # Test 2: Loop with translate
    source = """
CANVAS 20 20;
LOOP 3 {
    PIXEL 0 0 #00FF00;
    TRANSLATE 5 5;
}
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    print("  ✓ Loop with translate pattern")
    
    # Test 3: All shapes
    source = """
CANVAS 50 50;
RECT 0 0 50 50 #FFFFFF;
CIRCLE 25 25 10 #FF0000;
LINE 0 0 49 49 #0000FF;
PIXEL 0 0 #00FF00;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    print("  ✓ All drawing primitives")
    
    # Test 4: FILL command
    source = """
CANVAS 16 16;
RECT 0 0 16 16 #FFFFFF;
FILL 0 0 #FF0000;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    assert image.size == (16, 16)
    # Check that fill worked - pixel at (0,0) should be red
    pixel = image.getpixel((0, 0))
    assert pixel == (255, 0, 0), f"Expected red, got {pixel}"
    print("  ✓ FILL flood fill generation")
    
    # Test 5: CLEAR command
    source = """
CANVAS 16 16;
CLEAR #0000FF;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    pixel = image.getpixel((8, 8))
    assert pixel == (0, 0, 255), f"Expected blue, got {pixel}"
    print("  ✓ CLEAR command")
    
    # Test 6: ELLIPSE command
    source = """
CANVAS 32 32;
CLEAR #FFFFFF;
ELLIPSE 16 16 10 5 #FF00FF;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    print("  ✓ ELLIPSE command")
    
    # Test 7: TRIANGLE command
    source = """
CANVAS 32 32;
CLEAR #FFFFFF;
TRIANGLE 16 5 5 25 27 25 #00FF00;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    print("  ✓ TRIANGLE command")
    
    # Test 8: BORDER command
    source = """
CANVAS 16 16;
CLEAR #FFFFFF;
BORDER 2 2 12 12 2 #FF0000;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    print("  ✓ BORDER command")
    
    print("Code generator tests passed!\n")


def test_integration():
    """Integration tests."""
    print("Testing Integration...")
    
    # Sample pixel art program
    source = """
// Checkerboard pattern
CANVAS 16 16;

// Background
RECT 0 0 16 16 #FFFFFF;

// Draw some pixels
PIXEL 0 0 #000000;
PIXEL 2 0 #000000;
PIXEL 0 2 #000000;
PIXEL 2 2 #000000;

// Use loop for pattern
LOOP 4 {
    PIXEL 4 4 #FF0000;
    TRANSLATE 2 0;
}
"""
    image, errors = compile_source(source)
    assert image is not None, f"Errors: {errors}"
    assert len(errors) == 0
    assert image.size == (16, 16)
    print("  ✓ Checkerboard pattern")
    
    # Test error recovery - multiple errors collected
    source = """
PIXEL 0 0 #FF0000;
CANVAS 10 10;
PIXEL 20 20 #GGGGGG;
"""
    image, errors = compile_source(source)
    assert image is None
    assert len(errors) >= 1  # At least one error
    print("  ✓ Error recovery - errors collected")
    
    print("Integration tests passed!\n")


def run_tests():
    """Run all tests."""
    print("=" * 50)
    print("PixelLang Compiler Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_lexer()
        test_parser()
        test_semantic()
        test_codegen()
        test_integration()
        
        print("=" * 50)
        print("All tests passed!")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        return 1
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
