"""Tests for AST optimizer ensuring semantics-preserving transforms."""
from compiler import compile_source, lex, optimize, parse, pretty_print
from compiler.ast_nodes import LoopNode, MirrorNode, RotateNode, ScaleNode, SetNode, TranslateNode, VarNode


def test_translate_coalesce():
    source = """
CANVAS 10 10;
TRANSLATE 1 0;
TRANSLATE 2 0;
PIXEL 0 0 #FF0000;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    # The pixel should end up at (3,0)
    pixel = image.getpixel((3, 0))
    assert pixel == (255, 0, 0)


def test_remove_noop_transforms():
    source = """
CANVAS 8 8;
SCALE 1;
ROTATE 0;
PIXEL 4 4 #00FF00;
"""
    image, errors = compile_source(source)
    assert image is not None
    assert len(errors) == 0
    pixel = image.getpixel((4, 4))
    assert pixel == (0, 255, 0)


def test_remove_single_noop_transform_nodes():
    source = """
CANVAS 6 6;
TRANSLATE 0 0;
ROTATE 0;
SCALE 1;
PIXEL 1 1 #123456;
"""
    ast = parse(lex(source))
    optimized = optimize(ast)

    assert len(optimized.statements) == 2
    assert optimized.statements[0].__class__.__name__ == "CanvasNode"
    assert optimized.statements[1].__class__.__name__ == "PixelNode"


def test_fold_transform_chain_and_dce():
    source = """
CANVAS 10 10;
VAR temp 1;
SET temp 2;
TRANSLATE 1 0;
TRANSLATE 2 3;
ROTATE 90;
ROTATE 270;
SCALE 2;
SCALE 1;
MIRROR 0;
MIRROR 0;
LOOP 2 {
    VAR inner 7;
    SET inner 8;
    TRANSLATE 1 2;
    TRANSLATE 2 1;
}
PIXEL 0 0 #0000FF;
"""
    ast = parse(lex(source))
    optimized = optimize(ast)

    assert len(optimized.statements) == 5
    assert isinstance(optimized.statements[0], type(ast.statements[0]))
    assert isinstance(optimized.statements[1], TranslateNode)
    assert optimized.statements[1].dx == 3
    assert optimized.statements[1].dy == 3

    assert isinstance(optimized.statements[2], ScaleNode)
    assert optimized.statements[2].factor == 2

    assert isinstance(optimized.statements[3], LoopNode)
    loop_body = optimized.statements[3].body
    assert len(loop_body) == 1
    assert isinstance(loop_body[0], TranslateNode)
    assert loop_body[0].dx == 3
    assert loop_body[0].dy == 3

    assert not any(isinstance(node, (VarNode, SetNode)) for node in optimized.statements)
    assert not any(isinstance(node, (VarNode, SetNode)) for node in loop_body)
    assert optimized.statements[4].__class__.__name__ == "PixelNode"


def test_pretty_print_before_after():
    source = """
CANVAS 10 10;
VAR temp 1;
SET temp 2;
TRANSLATE 1 0;
TRANSLATE 2 0;
ROTATE 0;
LOOP 2 {
    VAR i 0;
    TRANSLATE 1 1;
}
PIXEL 0 0 #FF0000;
"""
    ast = parse(lex(source))
    
    before = pretty_print(ast)
    assert "VAR temp 1;" in before
    assert "SET temp 2;" in before
    assert "TRANSLATE 1 0;" in before
    assert "TRANSLATE 2 0;" in before
    assert "ROTATE 0;" in before
    assert "VAR i 0;" in before
    
    optimized = optimize(ast)
    after = pretty_print(optimized)
    
    assert "VAR" not in after
    assert "SET" not in after
    assert "TRANSLATE 3 0;" in after
    assert "ROTATE" not in after
    assert "LOOP 2" in after

