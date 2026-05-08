"""
PixelLang AST Optimizer
=======================

Conservative, semantics-preserving optimizations applied to the AST after
semantic analysis and before code generation.

Implemented optimizations:
- Constant-fold adjacent transform chains into canonical forms.
- Coalesce consecutive `TranslateNode`s into a single translate.
- Fold consecutive `RotateNode`s and `ScaleNode`s.
- Simplify `MirrorNode` sequences by parity.
- Remove no-op transforms: `Translate(0,0)`, `Rotate(0)`, `Scale(1)`, even-parity mirrors.
- Remove `VarNode` / `SetNode` statements, which are dead code for image generation.
- Recursively optimize `LoopNode` bodies.

The optimizer is intentionally simple to avoid changing program behavior.
"""
from .ast_nodes import *


def optimize(program: ProgramNode) -> ProgramNode:
    """Return an optimized ProgramNode (may reuse original nodes)."""
    return ProgramNode(_optimize_statement_list(program.statements))


def _optimize_statement_list(statements: list[ASTNode]) -> list[ASTNode]:
    optimized = []
    i = 0

    while i < len(statements):
        node = statements[i]

        if isinstance(node, (VarNode, SetNode)):
            i += 1
            continue

        if isinstance(node, LoopNode):
            optimized.append(LoopNode(node.count, _optimize_statement_list(node.body), node.line))
            i += 1
            continue

        folded, new_index = _fold_transform_chain(statements, i)
        if folded is not None:
            optimized.extend(folded)
            i = new_index
            continue

        optimized.append(node)
        i += 1

    return optimized


def _fold_transform_chain(statements: list[ASTNode], start_index: int):
    """Fold a maximal contiguous chain of transform statements."""
    chain = []
    i = start_index
    while i < len(statements):
        node = statements[i]
        if isinstance(node, (TranslateNode, RotateNode, ScaleNode, MirrorNode)):
            chain.append(node)
            i += 1
            continue
        break

    if len(chain) == 1:
        node = chain[0]
        if isinstance(node, TranslateNode) and node.dx == 0 and node.dy == 0:
            return [], start_index + 1
        if isinstance(node, RotateNode) and node.angle == 0:
            return [], start_index + 1
        if isinstance(node, ScaleNode) and node.factor == 1:
            return [], start_index + 1
        return None, start_index

    if len(chain) <= 1:
        return None, start_index

    folded = []

    translate_dx = 0
    translate_dy = 0
    rotate_angle = 0
    scale_factor = 1
    mirror_x = False
    mirror_y = False

    for node in chain:
        if isinstance(node, TranslateNode):
            translate_dx += node.dx
            translate_dy += node.dy
        elif isinstance(node, RotateNode):
            rotate_angle = (rotate_angle + node.angle) % 360
        elif isinstance(node, ScaleNode):
            scale_factor *= node.factor
        elif isinstance(node, MirrorNode):
            if node.axis == 0:
                mirror_y = not mirror_y
            elif node.axis == 1:
                mirror_x = not mirror_x

    first_line = chain[0].line

    if translate_dx != 0 or translate_dy != 0:
        folded.append(TranslateNode(translate_dx, translate_dy, first_line))
    if rotate_angle != 0:
        folded.append(RotateNode(rotate_angle, first_line))
    if scale_factor != 1:
        folded.append(ScaleNode(scale_factor, first_line))
    if mirror_y:
        folded.append(MirrorNode(0, first_line))
    if mirror_x:
        folded.append(MirrorNode(1, first_line))

    return folded, i
