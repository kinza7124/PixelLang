"""
PixelLang Abstract Syntax Tree (AST) Nodes
==========================================
AST node classes implementing the visitor pattern.
Each node type represents a language construct.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor (double dispatch)."""
        pass


@dataclass
class ProgramNode(ASTNode):
    """Root node - contains list of all statements."""
    statements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_ProgramNode(self)


@dataclass
class CanvasNode(ASTNode):
    """CANVAS width height; - declares canvas size."""
    width: int
    height: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_CanvasNode(self)


@dataclass
class PixelNode(ASTNode):
    """PIXEL x y #COLOR; - places a single pixel."""
    x: int
    y: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_PixelNode(self)


@dataclass
class RectNode(ASTNode):
    """RECT x y w h #COLOR; - draws a filled rectangle."""
    x: int
    y: int
    w: int
    h: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_RectNode(self)


@dataclass
class LineNode(ASTNode):
    """LINE x1 y1 x2 y2 #COLOR; - draws a line."""
    x1: int
    y1: int
    x2: int
    y2: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_LineNode(self)


@dataclass
class CircleNode(ASTNode):
    """CIRCLE cx cy r #COLOR; - draws a filled circle."""
    cx: int
    cy: int
    radius: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_CircleNode(self)


@dataclass
class FillNode(ASTNode):
    """FILL x y #COLOR; - flood fill from position with color."""
    x: int
    y: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_FillNode(self)


@dataclass
class EllipseNode(ASTNode):
    """ELLIPSE cx cy rx ry #COLOR; - draw filled ellipse."""
    cx: int
    cy: int
    rx: int
    ry: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_EllipseNode(self)


@dataclass
class ClearNode(ASTNode):
    """CLEAR #COLOR; - fill entire canvas with color."""
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_ClearNode(self)


@dataclass
class BorderNode(ASTNode):
    """BORDER x y w h thickness #COLOR; - draw hollow rectangle border."""
    x: int
    y: int
    width: int
    height: int
    thickness: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_BorderNode(self)


@dataclass
class TriangleNode(ASTNode):
    """TRIANGLE x1 y1 x2 y2 x3 y3 #COLOR; - draw filled triangle."""
    x1: int
    y1: int
    x2: int
    y2: int
    x3: int
    y3: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_TriangleNode(self)


@dataclass
class ArcNode(ASTNode):
    """ARC cx cy r start end #COLOR; - draw circular arc (start/end in degrees)."""
    cx: int
    cy: int
    radius: int
    start: int
    end: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_ArcNode(self)


@dataclass
class PolygonNode(ASTNode):
    """POLYGON x1 y1 x2 y2 x3 y3 ... #COLOR; - draw multi-point polygon."""
    points: List[tuple[int, int]]  # List of (x, y) tuples
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_PolygonNode(self)


@dataclass
class TextNode(ASTNode):
    """TEXT x y "string" #COLOR; - draw text at position."""
    x: int
    y: int
    text: str
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_TextNode(self)


@dataclass
class MirrorNode(ASTNode):
    """MIRROR axis; - flip/mirror context (axis: 0=horizontal, 1=vertical)."""
    axis: int  # 0 = horizontal (flip Y), 1 = vertical (flip X)
    line: int
    
    def accept(self, visitor):
        return visitor.visit_MirrorNode(self)


@dataclass
class ScaleNode(ASTNode):
    """SCALE factor; - scale drawing context (factor: 1-10)."""
    factor: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_ScaleNode(self)


@dataclass
class LoopNode(ASTNode):
    """LOOP n { statements... } - repeats body n times."""
    count: int
    body: List[ASTNode]
    line: int
    
    def accept(self, visitor):
        return visitor.visit_LoopNode(self)


@dataclass
class TranslateNode(ASTNode):
    """TRANSLATE dx dy; - shifts drawing origin."""
    dx: int
    dy: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_TranslateNode(self)


@dataclass
class RotateNode(ASTNode):
    """ROTATE angle; - rotates drawing context."""
    angle: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_RotateNode(self)


# ==================== v2.0 Advanced Drawing Nodes ====================

@dataclass
class BezierNode(ASTNode):
    """BEZIER x1 y1 cx1 cy1 cx2 cy2 x2 y2 #COLOR; - cubic bezier curve."""
    x1: int
    y1: int
    cx1: int
    cy1: int
    cx2: int
    cy2: int
    x2: int
    y2: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_BezierNode(self)


@dataclass
class StarNode(ASTNode):
    """STAR cx cy outer_r inner_r points #COLOR; - star shape."""
    cx: int
    cy: int
    outer_radius: int
    inner_radius: int
    points: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_StarNode(self)


@dataclass
class RoundRectNode(ASTNode):
    """ROUNDRECT x y w h radius #COLOR; - rectangle with rounded corners."""
    x: int
    y: int
    w: int
    h: int
    radius: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_RoundRectNode(self)


@dataclass
class HeartNode(ASTNode):
    """HEART cx cy size #COLOR; - heart shape."""
    cx: int
    cy: int
    size: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_HeartNode(self)


@dataclass
class ArrowNode(ASTNode):
    """ARROW x1 y1 x2 y2 head_size #COLOR; - arrow with arrowhead."""
    x1: int
    y1: int
    x2: int
    y2: int
    head_size: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_ArrowNode(self)


@dataclass
class PaletteNode(ASTNode):
    """PALETTE index #COLOR; - define palette color at index (0-15)."""
    index: int
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_PaletteNode(self)


@dataclass
class SetPaletteNode(ASTNode):
    """SETPALETTE index; - set active drawing color from palette."""
    index: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_SetPaletteNode(self)


@dataclass
class SpriteNode(ASTNode):
    """SPRITE x y pattern #COLOR; - draw pixel sprite pattern."""
    x: int
    y: int
    pattern: str  # Binary pattern string like "111101000"
    color: str
    line: int
    
    def accept(self, visitor):
        return visitor.visit_SpriteNode(self)


@dataclass
class RandomNode(ASTNode):
    """RANDOM min max; - generate random number (stored in random register)."""
    min_val: int
    max_val: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_RandomNode(self)


@dataclass
class VarNode(ASTNode):
    """VAR name value; - define variable with initial value."""
    name: str
    value: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_VarNode(self)


@dataclass
class SetNode(ASTNode):
    """SET name value; - set variable to new value."""
    name: str
    value: int
    line: int
    
    def accept(self, visitor):
        return visitor.visit_SetNode(self)


class NodeVisitor:
    """
    Base visitor class for traversing the AST.
    
    Usage:
        class MyAnalyzer(NodeVisitor):
            def visit_PixelNode(self, node):
                # Handle PixelNode
                pass
    """
    
    def visit(self, node: ASTNode):
        """Dynamically dispatch to visit_{ClassName} method."""
        method_name = f"visit_{type(node).__name__}"
        visitor_fn = getattr(self, method_name, self.generic_visit)
        return visitor_fn(node)
    
    def generic_visit(self, node: ASTNode):
        """Called when no specific visitor method exists."""
        raise NotImplementedError(f"No visit_{type(node).__name__} method defined")
    
    def visit_children(self, node: ASTNode):
        """Helper to visit all children of a node with statements."""
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self.visit(stmt)
        if hasattr(node, 'body'):
            for stmt in node.body:
                self.visit(stmt)


class ASTPrinter(NodeVisitor):
    """Pretty prints the AST for debugging."""
    
    def __init__(self):
        self.indent = 0
        self.output = []
    
    def _print(self, text: str):
        self.output.append("  " * self.indent + text)
    
    def print(self, node: ASTNode) -> str:
        self.output = []
        self.indent = 0
        self.visit(node)
        return "\n".join(self.output)
    
    def visit_ProgramNode(self, node: ProgramNode):
        self._print(f"ProgramNode ({len(node.statements)} statements)")
        self.indent += 1
        for stmt in node.statements:
            self.visit(stmt)
        self.indent -= 1
    
    def visit_CanvasNode(self, node: CanvasNode):
        self._print(f"CanvasNode: {node.width}x{node.height} (line {node.line})")
    
    def visit_PixelNode(self, node: PixelNode):
        self._print(f"PixelNode: ({node.x}, {node.y}) color={node.color} (line {node.line})")
    
    def visit_RectNode(self, node: RectNode):
        self._print(f"RectNode: ({node.x}, {node.y}) size={node.w}x{node.h} color={node.color} (line {node.line})")
    
    def visit_LineNode(self, node: LineNode):
        self._print(f"LineNode: ({node.x1}, {node.y1}) -> ({node.x2}, {node.y2}) color={node.color} (line {node.line})")
    
    def visit_CircleNode(self, node: CircleNode):
        self._print(f"CircleNode: center=({node.cx}, {node.cy}) r={node.radius} color={node.color} (line {node.line})")
    
    def visit_FillNode(self, node: FillNode):
        self._print(f"FillNode: ({node.x}, {node.y}) color={node.color} (line {node.line})")
    
    def visit_EllipseNode(self, node: EllipseNode):
        self._print(f"EllipseNode: center=({node.cx}, {node.cy}) radius=({node.rx}, {node.ry}) color={node.color} (line {node.line})")
    
    def visit_ClearNode(self, node: ClearNode):
        self._print(f"ClearNode: color={node.color} (line {node.line})")
    
    def visit_BorderNode(self, node: BorderNode):
        self._print(f"BorderNode: ({node.x}, {node.y}) size={node.width}x{node.height} thickness={node.thickness} color={node.color} (line {node.line})")
    
    def visit_TriangleNode(self, node: TriangleNode):
        self._print(f"TriangleNode: ({node.x1}, {node.y1}) ({node.x2}, {node.y2}) ({node.x3}, {node.y3}) color={node.color} (line {node.line})")
    
    def visit_ArcNode(self, node: ArcNode):
        self._print(f"ArcNode: center=({node.cx}, {node.cy}) r={node.radius} angles=({node.start}°-{node.end}°) color={node.color} (line {node.line})")
    
    def visit_PolygonNode(self, node: PolygonNode):
        points_str = ' '.join([f"({x},{y})" for x, y in node.points])
        self._print(f"PolygonNode: {points_str} color={node.color} (line {node.line})")
    
    def visit_TextNode(self, node: TextNode):
        self._print(f"TextNode: ({node.x}, {node.y}) text=\"{node.text}\" color={node.color} (line {node.line})")
    
    def visit_MirrorNode(self, node: MirrorNode):
        axis_str = "horizontal" if node.axis == 0 else "vertical"
        self._print(f"MirrorNode: {axis_str} (line {node.line})")
    
    def visit_ScaleNode(self, node: ScaleNode):
        self._print(f"ScaleNode: factor={node.factor}x (line {node.line})")
    
    def visit_LoopNode(self, node: LoopNode):
        self._print(f"LoopNode: count={node.count} (line {node.line})")
        self.indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent -= 1
    
    def visit_TranslateNode(self, node: TranslateNode):
        self._print(f"TranslateNode: ({node.dx}, {node.dy}) (line {node.line})")
    
    def visit_RotateNode(self, node: RotateNode):
        self._print(f"RotateNode: {node.angle}° (line {node.line})")
    
    # v2.0 Advanced Drawing Nodes
    def visit_BezierNode(self, node: BezierNode):
        self._print(f"BezierNode: ({node.x1},{node.y1}) -> ({node.x2},{node.y2}) c1=({node.cx1},{node.cy1}) c2=({node.cx2},{node.cy2}) color={node.color} (line {node.line})")
    
    def visit_StarNode(self, node: StarNode):
        self._print(f"StarNode: center=({node.cx},{node.cy}) outer={node.outer_radius} inner={node.inner_radius} points={node.points} color={node.color} (line {node.line})")
    
    def visit_RoundRectNode(self, node: RoundRectNode):
        self._print(f"RoundRectNode: ({node.x},{node.y}) size={node.w}x{node.h} radius={node.radius} color={node.color} (line {node.line})")
    
    def visit_HeartNode(self, node: HeartNode):
        self._print(f"HeartNode: center=({node.cx},{node.cy}) size={node.size} color={node.color} (line {node.line})")
    
    def visit_ArrowNode(self, node: ArrowNode):
        self._print(f"ArrowNode: ({node.x1},{node.y1}) -> ({node.x2},{node.y2}) head={node.head_size} color={node.color} (line {node.line})")
    
    def visit_PaletteNode(self, node: PaletteNode):
        self._print(f"PaletteNode: index={node.index} color={node.color} (line {node.line})")
    
    def visit_SetPaletteNode(self, node: SetPaletteNode):
        self._print(f"SetPaletteNode: index={node.index} (line {node.line})")
    
    def visit_SpriteNode(self, node: SpriteNode):
        self._print(f"SpriteNode: ({node.x},{node.y}) pattern='{node.pattern}' color={node.color} (line {node.line})")
    
    def visit_RandomNode(self, node: RandomNode):
        self._print(f"RandomNode: range=[{node.min_val},{node.max_val}] (line {node.line})")
    
    def visit_VarNode(self, node: VarNode):
        self._print(f"VarNode: {node.name}={node.value} (line {node.line})")
    
    def visit_SetNode(self, node: SetNode):
        self._print(f"SetNode: {node.name}={node.value} (line {node.line})")
