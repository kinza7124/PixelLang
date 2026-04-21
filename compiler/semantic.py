"""
PixelLang Semantic Analyzer
============================
Semantic analysis phase with 37 validation rules:

Core Rules (SEM-01 to SEM-13):
1. CANVAS must be first statement (SEM-01)
2. CANVAS declared at most once (SEM-02)
3. Canvas dimensions positive (SEM-03)
4-5. PIXEL coordinates within bounds (SEM-04, SEM-05)
6. Color format valid #RRGGBB (SEM-06)
7. Rectangle dimensions positive (SEM-07)
8. Rectangle within bounds (SEM-08)
9. Line endpoints within bounds (SEM-09)
10. Circle radius positive (SEM-10)
11. Circle within bounds (SEM-11)
12. Loop count positive (SEM-12)
13. Rotate angle 0-360 (SEM-13)

Extended Rules (SEM-14 to SEM-26):
14. FILL position within bounds (SEM-14)
15-16. Ellipse radii positive and within bounds (SEM-15, SEM-16)
17-18. Border dimensions positive and within bounds (SEM-17, SEM-18)
19. Triangle vertices within bounds (SEM-19)
20-22. Arc radius positive, center within bounds, angles 0-360 (SEM-20, SEM-21, SEM-22)
23. Polygon points within bounds (SEM-23)
24. Text position within bounds (SEM-24)
25. Mirror axis 0 or 1 (SEM-25)
26. Scale factor 1-10 (SEM-26)

v2.0 Rules (SEM-27 to SEM-37):
27. Bezier points within bounds (SEM-27)
28. Star parameters valid (SEM-28)
29. RoundRect within bounds (SEM-29)
30. Heart within bounds (SEM-30)
31. Arrow endpoints within bounds (SEM-31)
32-33. Palette index 0-15 (SEM-32, SEM-33)
34. Sprite pattern valid 0/1 (SEM-34)
35. Random range valid (SEM-35)
36. Variable definition (SEM-36)
37. Variable assignment exists (SEM-37)

Collects ALL errors (doesn't stop at first error).
"""
import re
from typing import List
from .ast_nodes import *
from .symbol_table import SymbolTable
from .errors import SemanticError


class SemanticAnalyzer(NodeVisitor):
    """
    Semantic analyzer using visitor pattern.
    Walks the AST and collects semantic errors.
    """
    
    # Color validation regex: #RRGGBB
    COLOR_REGEX = re.compile(r'^#[0-9A-Fa-f]{6}$')
    
    def __init__(self):
        self.sym_table = SymbolTable()
        self.canvas_w = None
        self.canvas_h = None
        self.errors: List[SemanticError] = []
        self.canvas_seen = False
    
    def error(self, msg: str, line: int):
        """Add a semantic error to the list."""
        self.errors.append(SemanticError(msg, line))
    
    def analyze(self, prog: ProgramNode) -> List[SemanticError]:
        """
        Analyze the AST and return list of all semantic errors.
        Empty list means no errors (clean pass).
        """
        self.errors = []
        self.visit(prog)
        return self.errors
    
    def check_color(self, color: str, line: int) -> bool:
        """Check if color is valid #RRGGBB format (SEM-06)."""
        if not self.COLOR_REGEX.match(color):
            self.error(f"Invalid color '{color}' - must be #RRGGBB format", line)
            return False
        return True
    
    def check_canvas_exists(self, line: int) -> bool:
        """Check if CANVAS has been declared."""
        if not self.canvas_seen:
            self.error("No CANVAS declared - CANVAS must be the first statement", line)
            return False
        return True
    
    def visit_ProgramNode(self, node: ProgramNode):
        """SEM-01: CANVAS must be the first statement."""
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
            self.error(f"Duplicate CANVAS declaration at line {node.line}", node.line)
        
        if node.width <= 0 or node.height <= 0:
            self.error("Canvas dimensions must be positive integers", node.line)
        
        # Only set canvas and define in symbol table if not already seen
        if not self.canvas_seen:
            self.canvas_w = node.width
            self.canvas_h = node.height
            self.canvas_seen = True
            
            # Define in symbol table
            self.sym_table.define("canvas", "canvas", (node.width, node.height), "tuple", node.line)
    
    def visit_PixelNode(self, node: PixelNode):
        """
        SEM-04: PIXEL x within bounds.
        SEM-05: PIXEL y within bounds.
        SEM-06: Color format valid.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check bounds
        if not (0 <= node.x < self.canvas_w):
            self.error(
                f"PIXEL x={node.x} out of bounds (canvas width={self.canvas_w})",
                node.line
            )
        
        if not (0 <= node.y < self.canvas_h):
            self.error(
                f"PIXEL y={node.y} out of bounds (canvas height={self.canvas_h})",
                node.line
            )
        
        # Check color
        self.check_color(node.color, node.line)
    
    def visit_RectNode(self, node: RectNode):
        """
        SEM-06: Color format valid.
        SEM-07: Rectangle dimensions must be positive.
        SEM-08: Rectangle must be within canvas bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-07: Dimensions positive
        if node.w <= 0 or node.h <= 0:
            self.error("Rectangle dimensions must be positive", node.line)
        
        # SEM-08: Within bounds
        if node.x + node.w > self.canvas_w or node.y + node.h > self.canvas_h:
            self.error("Rectangle extends outside canvas bounds", node.line)
        
        if node.x < 0 or node.y < 0:
            self.error("Rectangle extends outside canvas bounds (negative origin)", node.line)
    
    def visit_LineNode(self, node: LineNode):
        """
        SEM-06: Color format valid.
        SEM-09: Line endpoints within bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-09: Endpoints within bounds
        for label, x, y in [("x1", node.x1, node.y1), ("x2", node.x2, node.y2)]:
            if not (0 <= x < self.canvas_w) or not (0 <= y < self.canvas_h):
                self.error(
                    f"LINE endpoint ({x}, {y}) out of canvas bounds "
                    f"(width={self.canvas_w}, height={self.canvas_h})",
                    node.line
                )
                break
    
    def visit_CircleNode(self, node: CircleNode):
        """
        SEM-06: Color format valid.
        SEM-10: Circle radius must be positive.
        SEM-11: Circle must be completely within bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-10: Positive radius
        if node.radius <= 0:
            self.error("Circle radius must be a positive integer", node.line)
        
        # SEM-11: Circle within bounds
        cx, cy, r = node.cx, node.cy, node.radius
        if cx - r < 0 or cx + r >= self.canvas_w or cy - r < 0 or cy + r >= self.canvas_h:
            self.error(
                f"Circle extends outside canvas bounds "
                f"(center=({cx},{cy}), r={r}, canvas={self.canvas_w}x{self.canvas_h})",
                node.line
            )
    
    def visit_FillNode(self, node: FillNode):
        """
        SEM-06: Color format valid.
        SEM-14: Fill position within bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-14: Position within bounds
        if not (0 <= node.x < self.canvas_w):
            self.error(
                f"FILL x={node.x} out of bounds (canvas width={self.canvas_w})",
                node.line
            )
        
        if not (0 <= node.y < self.canvas_h):
            self.error(
                f"FILL y={node.y} out of bounds (canvas height={self.canvas_h})",
                node.line
            )
    
    def visit_EllipseNode(self, node: EllipseNode):
        """
        SEM-06: Color format valid.
        SEM-15: Ellipse radii must be positive.
        SEM-16: Ellipse must be within canvas bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-15: Positive radii
        if node.rx <= 0 or node.ry <= 0:
            self.error("Ellipse radii must be positive integers", node.line)
        
        # SEM-16: Ellipse within bounds
        cx, cy, rx, ry = node.cx, node.cy, node.rx, node.ry
        if cx - rx < 0 or cx + rx >= self.canvas_w or cy - ry < 0 or cy + ry >= self.canvas_h:
            self.error(
                f"Ellipse extends outside canvas bounds "
                f"(center=({cx},{cy}), rx={rx}, ry={ry}, canvas={self.canvas_w}x{self.canvas_h})",
                node.line
            )
    
    def visit_ClearNode(self, node: ClearNode):
        """SEM-06: Color format valid."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
    
    def visit_BorderNode(self, node: BorderNode):
        """
        SEM-06: Color format valid.
        SEM-17: Border dimensions must be positive.
        SEM-18: Border must be within canvas bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-17: Positive dimensions
        if node.width <= 0 or node.height <= 0 or node.thickness <= 0:
            self.error("Border width, height, and thickness must be positive integers", node.line)
        
        # SEM-18: Border within bounds
        if not (0 <= node.x < self.canvas_w) or not (0 <= node.y < self.canvas_h):
            self.error(
                f"Border position ({node.x}, {node.y}) out of canvas bounds",
                node.line
            )
        if node.x + node.width > self.canvas_w or node.y + node.height > self.canvas_h:
            self.error(
                f"Border extends outside canvas bounds "
                f"(x={node.x}, y={node.y}, w={node.width}, h={node.height}, "
                f"canvas={self.canvas_w}x{self.canvas_h})",
                node.line
            )
    
    def visit_TriangleNode(self, node: TriangleNode):
        """
        SEM-06: Color format valid.
        SEM-19: Triangle vertices must be within canvas bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-19: Vertices within bounds
        for label, x, y in [("x1", node.x1, node.y1), ("x2", node.x2, node.y2), ("x3", node.x3, node.y3)]:
            if not (0 <= x < self.canvas_w) or not (0 <= y < self.canvas_h):
                self.error(
                    f"TRIANGLE vertex ({x}, {y}) out of canvas bounds "
                    f"(width={self.canvas_w}, height={self.canvas_h})",
                    node.line
                )
    
    def visit_ArcNode(self, node: ArcNode):
        """
        SEM-06: Color format valid.
        SEM-20: Arc radius must be positive.
        SEM-21: Arc center must be within bounds.
        SEM-22: Arc angles must be 0-360.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-20: Positive radius
        if node.radius <= 0:
            self.error("Arc radius must be a positive integer", node.line)
        
        # SEM-21: Center within bounds
        if not (0 <= node.cx < self.canvas_w) or not (0 <= node.cy < self.canvas_h):
            self.error(
                f"ARC center ({node.cx}, {node.cy}) out of canvas bounds",
                node.line
            )
        
        # SEM-22: Angle range
        if not (0 <= node.start <= 360) or not (0 <= node.end <= 360):
            self.error(f"ARC angles must be 0-360 (got {node.start}-{node.end})", node.line)
    
    def visit_PolygonNode(self, node: PolygonNode):
        """
        SEM-06: Color format valid.
        SEM-23: Polygon points must be within canvas bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-23: Points within bounds
        for i, (x, y) in enumerate(node.points):
            if not (0 <= x < self.canvas_w) or not (0 <= y < self.canvas_h):
                self.error(
                    f"POLYGON point {i+1} ({x}, {y}) out of canvas bounds "
                    f"(width={self.canvas_w}, height={self.canvas_h})",
                    node.line
                )
    
    def visit_TextNode(self, node: TextNode):
        """
        SEM-06: Color format valid.
        SEM-24: Text position must be within canvas bounds.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # Check color
        self.check_color(node.color, node.line)
        
        # SEM-24: Position within bounds
        if not (0 <= node.x < self.canvas_w) or not (0 <= node.y < self.canvas_h):
            self.error(
                f"TEXT position ({node.x}, {node.y}) out of canvas bounds",
                node.line
            )
    
    def visit_MirrorNode(self, node: MirrorNode):
        """
        SEM-25: Mirror axis must be 0 or 1.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        if node.axis not in [0, 1]:
            self.error(f"MIRROR axis must be 0 (horizontal) or 1 (vertical) (got {node.axis})", node.line)
    
    def visit_ScaleNode(self, node: ScaleNode):
        """
        SEM-26: Scale factor must be 1-10.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        if not (1 <= node.factor <= 10):
            self.error(f"SCALE factor must be 1-10 (got {node.factor})", node.line)
    
    def visit_LoopNode(self, node: LoopNode):
        """
        SEM-12: Loop count must be positive.
        Creates a new scope for the loop body.
        """
        # SEM-12: Positive count
        if node.count <= 0:
            self.error(f"Loop count must be a positive integer (got {node.count})", node.line)
        
        # Enter new scope for loop body
        self.sym_table.enter_scope()
        self.sym_table.define("loop_count", "loop_counter", node.count, "int", node.line)
        self.sym_table.define("loop_iter", "loop_counter", 0, "int", node.line)
        
        # Visit body statements
        for stmt in node.body:
            self.visit(stmt)
        
        # Exit scope
        self.sym_table.exit_scope()
    
    def visit_TranslateNode(self, node: TranslateNode):
        """TRANSLATE - no semantic checks needed beyond canvas existing."""
        self.check_canvas_exists(node.line)
    
    def visit_RotateNode(self, node: RotateNode):
        """
        SEM-13: Rotate angle must be 0-360.
        """
        if not self.check_canvas_exists(node.line):
            return
        
        # SEM-13: Angle range
        if not (0 <= node.angle <= 360):
            self.error(f"ROTATE angle must be 0-360 (got {node.angle})", node.line)
    
    # ==================== v2.0 Semantic Analysis ====================
    
    def visit_BezierNode(self, node: BezierNode):
        """SEM-27: Bezier points must be within canvas bounds."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
        
        points = [(node.x1, node.y1), (node.cx1, node.cy1), 
                  (node.cx2, node.cy2), (node.x2, node.y2)]
        for i, (x, y) in enumerate(points):
            if not (0 <= x < self.canvas_w) or not (0 <= y < self.canvas_h):
                self.error(f"BEZIER point {i+1} ({x}, {y}) out of canvas bounds", node.line)
    
    def visit_StarNode(self, node: StarNode):
        """SEM-28: Star must be within canvas bounds and have valid parameters."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
        
        if node.outer_radius <= 0 or node.inner_radius <= 0:
            self.error("STAR radii must be positive", node.line)
        if node.points < 3:
            self.error("STAR must have at least 3 points", node.line)
        if node.points > 20:
            self.error("STAR can have at most 20 points", node.line)
        
        # Check center within bounds (rough check)
        if not (0 <= node.cx < self.canvas_w) or not (0 <= node.cy < self.canvas_h):
            self.error(f"STAR center ({node.cx}, {node.cy}) out of canvas bounds", node.line)
    
    def visit_RoundRectNode(self, node: RoundRectNode):
        """SEM-29: RoundRect must be within canvas bounds."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
        
        if node.w <= 0 or node.h <= 0:
            self.error("ROUNDRECT dimensions must be positive", node.line)
        if node.radius < 0:
            self.error("ROUNDRECT radius must be non-negative", node.line)
        if node.radius > min(node.w, node.h) // 2:
            self.error("ROUNDRECT radius too large for dimensions", node.line)
        
        if node.x + node.w > self.canvas_w or node.y + node.h > self.canvas_h:
            self.error("ROUNDRECT extends outside canvas bounds", node.line)
    
    def visit_HeartNode(self, node: HeartNode):
        """SEM-30: Heart must be within canvas bounds."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
        
        if node.size <= 0:
            self.error("HEART size must be positive", node.line)
        
        # Heart extends roughly 1 size in each direction from center
        if node.cx - node.size < 0 or node.cx + node.size >= self.canvas_w:
            self.error("HEART extends outside canvas bounds (x-axis)", node.line)
        if node.cy - node.size < 0 or node.cy + node.size >= self.canvas_h:
            self.error("HEART extends outside canvas bounds (y-axis)", node.line)
    
    def visit_ArrowNode(self, node: ArrowNode):
        """SEM-31: Arrow endpoints must be within canvas bounds."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
        
        if node.head_size <= 0:
            self.error("ARROW head size must be positive", node.line)
        
        for label, x, y in [("start", node.x1, node.y1), ("end", node.x2, node.y2)]:
            if not (0 <= x < self.canvas_w) or not (0 <= y < self.canvas_h):
                self.error(f"ARROW {label} ({x}, {y}) out of canvas bounds", node.line)
    
    def visit_PaletteNode(self, node: PaletteNode):
        """SEM-32: Palette index must be 0-15."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
        
        if not (0 <= node.index <= 15):
            self.error(f"PALETTE index must be 0-15 (got {node.index})", node.line)
    
    def visit_SetPaletteNode(self, node: SetPaletteNode):
        """SEM-33: SetPalette index must be 0-15."""
        if not self.check_canvas_exists(node.line):
            return
        
        if not (0 <= node.index <= 15):
            self.error(f"SETPALETTE index must be 0-15 (got {node.index})", node.line)
    
    def visit_SpriteNode(self, node: SpriteNode):
        """SEM-34: Sprite position and pattern must be valid."""
        if not self.check_canvas_exists(node.line):
            return
        self.check_color(node.color, node.line)
        
        # Validate pattern contains only 0s and 1s
        if not all(c in '01' for c in node.pattern):
            self.error(f"SPRITE pattern must contain only 0s and 1s", node.line)
        
        if not (0 <= node.x < self.canvas_w) or not (0 <= node.y < self.canvas_h):
            self.error(f"SPRITE position ({node.x}, {node.y}) out of canvas bounds", node.line)
    
    def visit_RandomNode(self, node: RandomNode):
        """SEM-35: Random range must be valid."""
        if not self.check_canvas_exists(node.line):
            return
        
        if node.min_val >= node.max_val:
            self.error(f"RANDOM min must be less than max", node.line)
    
    def visit_VarNode(self, node: VarNode):
        """SEM-36: Variable definition."""
        if not self.check_canvas_exists(node.line):
            return
        
        # Define in symbol table
        self.sym_table.define(node.name, "variable", node.value, "int", node.line)
    
    def visit_SetNode(self, node: SetNode):
        """SEM-37: Variable assignment - variable must exist."""
        if not self.check_canvas_exists(node.line):
            return
        
        symbol = self.sym_table.lookup(node.name)
        if symbol is None:
            self.error(f"Variable '{node.name}' not defined", node.line)


def analyze(ast: ProgramNode) -> List[SemanticError]:
    """Convenience function to run semantic analysis."""
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)
