"""
AST Pretty-Printer for PixelLang
=================================
Formats the AST into human-readable text showing node structure and values.
Useful for debugging and visualizing optimizer transformations.
"""
from .ast_nodes import ASTNode, NodeVisitor


class ASTFormatter(NodeVisitor):
    """Formats AST nodes into readable text with indentation."""
    
    def __init__(self, indent_width: int = 2):
        self.indent_width = indent_width
        self.current_indent = 0
        self.lines = []
    
    def format(self, node: ASTNode) -> str:
        """Format an AST node and return the formatted string."""
        self.lines = []
        self.current_indent = 0
        self.visit(node)
        return "\n".join(self.lines)
    
    def _indent(self) -> str:
        """Return the current indentation."""
        return " " * (self.current_indent * self.indent_width)
    
    def _add_line(self, text: str):
        """Add a line with current indentation."""
        self.lines.append(self._indent() + text)
    
    def generic_visit(self, node: ASTNode):
        """Default visitor for unimplemented node types."""
        class_name = type(node).__name__
        self._add_line(f"{class_name}(...)")
    
    # ─── Draw Statements ───
    
    def visit_CanvasNode(self, node):
        self._add_line(f"CANVAS {node.width} {node.height};")
    
    def visit_PixelNode(self, node):
        self._add_line(f"PIXEL {node.x} {node.y} {node.color};")
    
    def visit_RectNode(self, node):
        self._add_line(f"RECT {node.x} {node.y} {node.w} {node.h} {node.color};")
    
    def visit_LineNode(self, node):
        self._add_line(f"LINE {node.x1} {node.y1} {node.x2} {node.y2} {node.color};")
    
    def visit_CircleNode(self, node):
        self._add_line(f"CIRCLE {node.cx} {node.cy} {node.radius} {node.color};")
    
    def visit_FillNode(self, node):
        self._add_line(f"FILL {node.x} {node.y} {node.color};")
    
    def visit_EllipseNode(self, node):
        self._add_line(f"ELLIPSE {node.cx} {node.cy} {node.rx} {node.ry} {node.color};")
    
    def visit_ClearNode(self, node):
        self._add_line(f"CLEAR {node.color};")
    
    def visit_BorderNode(self, node):
        self._add_line(f"BORDER {node.x} {node.y} {node.width} {node.height} {node.thickness} {node.color};")
    
    def visit_TriangleNode(self, node):
        self._add_line(f"TRIANGLE {node.x1} {node.y1} {node.x2} {node.y2} {node.x3} {node.y3} {node.color};")
    
    def visit_ArcNode(self, node):
        self._add_line(f"ARC {node.cx} {node.cy} {node.radius} {node.start} {node.end} {node.color};")
    
    def visit_PolygonNode(self, node):
        points_str = " ".join([f"{x} {y}" for x, y in node.points])
        self._add_line(f"POLYGON {points_str} {node.color};")
    
    def visit_TextNode(self, node):
        self._add_line(f"TEXT {node.x} {node.y} {node.text} {node.color};")
    
    # ─── Transform Statements ───
    
    def visit_TranslateNode(self, node):
        self._add_line(f"TRANSLATE {node.dx} {node.dy};")
    
    def visit_RotateNode(self, node):
        self._add_line(f"ROTATE {node.angle};")
    
    def visit_ScaleNode(self, node):
        self._add_line(f"SCALE {node.factor};")
    
    def visit_MirrorNode(self, node):
        self._add_line(f"MIRROR {node.axis};")
    
    # ─── Control Flow ───
    
    def visit_LoopNode(self, node):
        self._add_line(f"LOOP {node.count} {{")
        self.current_indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.current_indent -= 1
        self._add_line("}")
    
    # ─── Variable Statements ───
    
    def visit_VarNode(self, node):
        self._add_line(f"VAR {node.name} {node.value};")
    
    def visit_SetNode(self, node):
        self._add_line(f"SET {node.name} {node.value};")
    
    # ─── v2.0 Advanced Nodes ───
    
    def visit_BezierNode(self, node):
        self._add_line(f"BEZIER {node.x1} {node.y1} {node.cx1} {node.cy1} {node.cx2} {node.cy2} {node.x2} {node.y2} {node.color};")
    
    def visit_StarNode(self, node):
        self._add_line(f"STAR {node.cx} {node.cy} {node.outer_radius} {node.inner_radius} {node.points} {node.color};")
    
    def visit_RoundRectNode(self, node):
        self._add_line(f"ROUNDRECT {node.x} {node.y} {node.w} {node.h} {node.radius} {node.color};")
    
    def visit_HeartNode(self, node):
        self._add_line(f"HEART {node.cx} {node.cy} {node.size} {node.color};")
    
    def visit_ArrowNode(self, node):
        self._add_line(f"ARROW {node.x1} {node.y1} {node.x2} {node.y2} {node.head_size} {node.color};")
    
    def visit_PaletteNode(self, node):
        self._add_line(f"PALETTE {node.index} {node.color};")
    
    def visit_SetPaletteNode(self, node):
        self._add_line(f"SETPALETTE {node.index};")
    
    def visit_SpriteNode(self, node):
        self._add_line(f"SPRITE {node.x} {node.y} {node.pattern} {node.color};")
    
    def visit_RandomNode(self, node):
        self._add_line(f"RANDOM {node.min_val} {node.max_val};")
    
    # ─── Program ───
    
    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)


def pretty_print(program) -> str:
    """Convenience function to pretty-print an AST."""
    formatter = ASTFormatter()
    return formatter.format(program)
