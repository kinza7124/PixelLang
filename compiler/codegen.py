"""
PixelLang Code Generator
=========================
Final compiler phase that generates PNG images using Pillow (PIL).

Maintains a transform stack to handle TRANSLATE accumulation within LOOP bodies.
Key insight: TRANSLATE values accumulate inside loops, creating patterns.
After a loop exits, the transform is restored to its pre-loop value.
"""
import math
from PIL import Image, ImageDraw
from typing import Optional
from .ast_nodes import *
from .errors import CodeGenError


class CodeGenerator(NodeVisitor):
    """
    Code generator using visitor pattern.
    Walks the validated AST and draws to a PIL Image.
    """
    
    def __init__(self):
        self.image: Optional[Image.Image] = None
        self.draw: Optional[ImageDraw.ImageDraw] = None
        
        # Transform state
        self.tx = 0  # x translation accumulator
        self.ty = 0  # y translation accumulator
        self.angle = 0  # rotation accumulator
        
        # Transform stack for LOOP enter/exit
        self.tx_stack = []
        self.ty_stack = []
    
    def generate(self, program: ProgramNode) -> Image.Image:
        """
        Generate an image from the AST.
        Returns the PIL Image object.
        """
        self.visit(program)
        if self.image is None:
            raise CodeGenError("No CANVAS statement - cannot generate image")
        return self.image
    
    def transform_point(self, x: int, y: int) -> tuple:
        """Apply current translation to a point."""
        return (x + self.tx, y + self.ty)
    
    def visit_ProgramNode(self, node: ProgramNode):
        """Visit all statements in program."""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_CanvasNode(self, node: CanvasNode):
        """
        Create the image canvas.
        CANVAS w h;
        """
        self.image = Image.new("RGB", (node.width, node.height), "white")
        self.draw = ImageDraw.Draw(self.image)
    
    def visit_PixelNode(self, node: PixelNode):
        """
        Draw a single pixel.
        PIXEL x y #COLOR;
        """
        x, y = self.transform_point(node.x, node.y)
        self.draw.point((x, y), fill=node.color)
    
    def visit_RectNode(self, node: RectNode):
        """
        Draw a filled rectangle.
        RECT x y w h #COLOR;
        """
        x0, y0 = self.transform_point(node.x, node.y)
        x1, y1 = x0 + node.w, y0 + node.h
        self.draw.rectangle([x0, y0, x1, y1], fill=node.color)
    
    def visit_LineNode(self, node: LineNode):
        """
        Draw a line.
        LINE x1 y1 x2 y2 #COLOR;
        """
        p1 = self.transform_point(node.x1, node.y1)
        p2 = self.transform_point(node.x2, node.y2)
        self.draw.line([p1, p2], fill=node.color, width=1)
    
    def visit_CircleNode(self, node: CircleNode):
        """
        Draw a filled circle.
        CIRCLE cx cy r #COLOR;
        """
        cx, cy = self.transform_point(node.cx, node.cy)
        r = node.radius
        # Bounding box for ellipse
        bbox = [cx - r, cy - r, cx + r, cy + r]
        self.draw.ellipse(bbox, fill=node.color)
    
    def visit_FillNode(self, node: FillNode):
        """
        Flood fill from position with color.
        FILL x y #COLOR;
        
        Uses iterative flood fill algorithm (BFS to avoid stack overflow).
        """
        x, y = self.transform_point(node.x, node.y)
        target_color = node.color
        
        # Get current pixel color at position
        try:
            seed_color = self.image.getpixel((x, y))
            if isinstance(seed_color, int):
                seed_color = (seed_color, seed_color, seed_color)
            seed_color = '#{:02x}{:02x}{:02x}'.format(*seed_color[:3]).upper()
        except IndexError:
            return  # Out of bounds, skip
        
        # If already target color, nothing to do
        if seed_color.upper() == target_color.upper():
            return
        
        # Convert target color to RGB
        target_rgb = (
            int(target_color[1:3], 16),
            int(target_color[3:5], 16),
            int(target_color[5:7], 16)
        )
        
        # Convert seed color to RGB tuple
        if isinstance(seed_color, str):
            seed_rgb = (
                int(seed_color[1:3], 16),
                int(seed_color[3:5], 16),
                int(seed_color[5:7], 16)
            )
        else:
            seed_rgb = seed_color
        
        # Iterative flood fill using stack
        width, height = self.image.size
        pixels = self.image.load()
        stack = [(x, y)]
        
        while stack:
            cx, cy = stack.pop()
            
            # Check bounds
            if cx < 0 or cx >= width or cy < 0 or cy >= height:
                continue
            
            # Get current pixel
            current = pixels[cx, cy]
            if isinstance(current, int):
                current = (current, current, current)
            
            # Check if matches seed color
            if current[:3] != seed_rgb[:3]:
                continue
            
            # Fill this pixel
            pixels[cx, cy] = target_rgb
            
            # Add neighbors
            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))
    
    def visit_EllipseNode(self, node: EllipseNode):
        """
        Draw a filled ellipse.
        ELLIPSE cx cy rx ry #COLOR;
        """
        cx, cy = self.transform_point(node.cx, node.cy)
        rx, ry = node.rx, node.ry
        # Bounding box for ellipse
        bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
        self.draw.ellipse(bbox, fill=node.color)
    
    def visit_ClearNode(self, node: ClearNode):
        """
        Fill entire canvas with color.
        CLEAR #COLOR;
        """
        width, height = self.image.size
        self.draw.rectangle([0, 0, width - 1, height - 1], fill=node.color)
    
    def visit_BorderNode(self, node: BorderNode):
        """
        Draw hollow rectangle border.
        BORDER x y w h thickness #COLOR;
        """
        x, y = self.transform_point(node.x, node.y)
        w, h, t = node.width, node.height, node.thickness
        # Draw outer rectangle
        outer = [x, y, x + w - 1, y + h - 1]
        # Draw inner rectangle (for hollow effect)
        inner = [x + t, y + t, x + w - 1 - t, y + h - 1 - t]
        # Use outline with thickness
        for i in range(t):
            inset = i
            bbox = [x + inset, y + inset, x + w - 1 - inset, y + h - 1 - inset]
            self.draw.rectangle(bbox, outline=node.color)
    
    def visit_TriangleNode(self, node: TriangleNode):
        """
        Draw a filled triangle.
        TRIANGLE x1 y1 x2 y2 x3 y3 #COLOR;
        """
        x1, y1 = self.transform_point(node.x1, node.y1)
        x2, y2 = self.transform_point(node.x2, node.y2)
        x3, y3 = self.transform_point(node.x3, node.y3)
        self.draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=node.color)
    
    def visit_ArcNode(self, node: ArcNode):
        """
        Draw a circular arc.
        ARC cx cy r start end #COLOR;
        Angles are in degrees, 0 at 3 o'clock, clockwise.
        """
        cx, cy = self.transform_point(node.cx, node.cy)
        r = node.radius
        # Bounding box for the ellipse
        bbox = [cx - r, cy - r, cx + r, cy + r]
        self.draw.arc(bbox, start=node.start, end=node.end, fill=node.color, width=2)
    
    def visit_PolygonNode(self, node: PolygonNode):
        """
        Draw a multi-point polygon.
        POLYGON x1 y1 x2 y2 x3 y3 x4 y4 #COLOR;
        """
        points = []
        for x, y in node.points:
            tx, ty = self.transform_point(x, y)
            points.append((tx, ty))
        self.draw.polygon(points, fill=node.color)
    
    def visit_TextNode(self, node: TextNode):
        """
        Draw text at position.
        TEXT x y text #COLOR;
        Uses default bitmap font.
        """
        x, y = self.transform_point(node.x, node.y)
        # Simple pixel-based text drawing using small rectangles
        self._draw_simple_text(x, y, node.text, node.color)
    
    def _draw_simple_text(self, x: int, y: int, text: str, color: str):
        """Draw simple pixel-based text (uppercase only, 3x5 font with space support)."""
        # Simple 3x5 font for uppercase letters and numbers
        # Space is handled separately - it advances cursor without drawing
        font = {
            'A': [0b010, 0b101, 0b111, 0b101, 0b101],
            'B': [0b110, 0b101, 0b110, 0b101, 0b110],
            'C': [0b011, 0b100, 0b100, 0b100, 0b011],
            'D': [0b110, 0b101, 0b101, 0b101, 0b110],
            'E': [0b111, 0b100, 0b111, 0b100, 0b111],
            'F': [0b111, 0b100, 0b110, 0b100, 0b100],
            'G': [0b011, 0b100, 0b101, 0b101, 0b011],
            'H': [0b101, 0b101, 0b111, 0b101, 0b101],
            'I': [0b111, 0b010, 0b010, 0b010, 0b111],
            'J': [0b001, 0b001, 0b001, 0b101, 0b010],
            'K': [0b101, 0b101, 0b110, 0b101, 0b101],
            'L': [0b100, 0b100, 0b100, 0b100, 0b111],
            'M': [0b101, 0b111, 0b101, 0b101, 0b101],
            'N': [0b111, 0b101, 0b101, 0b101, 0b101],
            'O': [0b010, 0b101, 0b101, 0b101, 0b010],
            'P': [0b110, 0b101, 0b110, 0b100, 0b100],
            'Q': [0b010, 0b101, 0b101, 0b010, 0b001],
            'R': [0b110, 0b101, 0b110, 0b101, 0b101],
            'S': [0b011, 0b100, 0b010, 0b001, 0b110],
            'T': [0b111, 0b010, 0b010, 0b010, 0b010],
            'U': [0b101, 0b101, 0b101, 0b101, 0b011],
            'V': [0b101, 0b101, 0b101, 0b101, 0b010],
            'W': [0b101, 0b101, 0b101, 0b111, 0b101],
            'X': [0b101, 0b101, 0b010, 0b101, 0b101],
            'Y': [0b101, 0b101, 0b010, 0b010, 0b010],
            'Z': [0b111, 0b001, 0b010, 0b100, 0b111],
            '0': [0b010, 0b101, 0b101, 0b101, 0b010],
            '1': [0b010, 0b110, 0b010, 0b010, 0b111],
            '2': [0b110, 0b001, 0b010, 0b100, 0b111],
            '3': [0b110, 0b001, 0b010, 0b001, 0b110],
            '4': [0b101, 0b101, 0b111, 0b001, 0b001],
            '5': [0b111, 0b100, 0b110, 0b001, 0b110],
            '6': [0b010, 0b100, 0b111, 0b101, 0b010],
            '7': [0b111, 0b001, 0b010, 0b010, 0b010],
            '8': [0b010, 0b101, 0b010, 0b101, 0b010],
            '9': [0b010, 0b101, 0b011, 0b001, 0b010],
        }
        
        cursor_x = x
        for char in text.upper():
            if char == ' ':
                # Space: advance cursor by 2 pixels (narrow space)
                cursor_x += 2
            elif char in font:
                pattern = font[char]
                for row, bits in enumerate(pattern):
                    for col in range(3):
                        if bits & (1 << (2 - col)):
                            self.draw.rectangle([cursor_x + col, y + row, cursor_x + col, y + row], fill=color)
                # Advance cursor by 4 pixels (3 for char + 1 for spacing)
                cursor_x += 4
    
    def visit_MirrorNode(self, node: MirrorNode):
        """
        Mirror/flip the transform context.
        MIRROR axis; 0=horizontal (flip Y), 1=vertical (flip X)
        """
        if node.axis == 0:  # Horizontal - flip Y
            self.mirror_y = not getattr(self, 'mirror_y', False)
        else:  # Vertical - flip X
            self.mirror_x = not getattr(self, 'mirror_x', False)
    
    def visit_ScaleNode(self, node: ScaleNode):
        """
        Scale the transform context.
        SCALE factor;
        """
        self.scale = getattr(self, 'scale', 1) * node.factor
    
    def visit_LoopNode(self, node: LoopNode):
        """
        Execute loop body count times.
        LOOP n { statements... }
        
        Key: Save/restore transform state so TRANSLATE accumulates within
        the loop but doesn't affect code after the loop.
        """
        # Save current transform state
        self.tx_stack.append(self.tx)
        self.ty_stack.append(self.ty)
        
        # Execute loop iterations
        for i in range(node.count):
            for stmt in node.body:
                self.visit(stmt)
        
        # Restore transform state
        self.tx = self.tx_stack.pop()
        self.ty = self.ty_stack.pop()
    
    def visit_TranslateNode(self, node: TranslateNode):
        """
        Accumulate translation offset.
        TRANSLATE dx dy;
        
        This accumulates - each call adds to the current offset.
        Inside loops, this creates shifting patterns.
        """
        self.tx += node.dx
        self.ty += node.dy
    
    def visit_RotateNode(self, node: RotateNode):
        """
        Accumulate rotation angle.
        ROTATE angle;
        
        Angle is modulo 360.
        Note: Full rotation support would require more complex transform math.
        For pixel art, we store the angle but drawing remains axis-aligned.
        """
        self.angle = (self.angle + node.angle) % 360
    
    # ==================== v2.0 Code Generation ====================
    
    def visit_BezierNode(self, node: BezierNode):
        """Draw cubic bezier curve using line segments."""
        x1, y1 = self.transform_point(node.x1, node.y1)
        x2, y2 = self.transform_point(node.x2, node.y2)
        cx1, cy1 = self.transform_point(node.cx1, node.cy1)
        cx2, cy2 = self.transform_point(node.cx2, node.cy2)
        
        # Generate points along bezier curve
        points = []
        steps = 50
        for i in range(steps + 1):
            t = i / steps
            # Cubic bezier formula
            t2 = t * t
            t3 = t2 * t
            mt = 1 - t
            mt2 = mt * mt
            mt3 = mt2 * mt
            
            x = int(mt3 * x1 + 3 * mt2 * t * cx1 + 3 * mt * t2 * cx2 + t3 * x2)
            y = int(mt3 * y1 + 3 * mt2 * t * cy1 + 3 * mt * t2 * cy2 + t3 * y2)
            points.append((x, y))
        
        # Draw line segments using pixels for more control
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            # Ensure proper ordering for rectangle
            x0, y0 = min(p1[0], p2[0]), min(p1[1], p2[1])
            x1, y1 = max(p1[0], p2[0]), max(p1[1], p2[1])
            # Draw as small rectangle if single point, otherwise line
            if x0 == x1 and y0 == y1:
                self.draw.point((x0, y0), fill=node.color)
            else:
                self.draw.line([(x0, y0), (x1, y1)], fill=node.color, width=1)
    
    def visit_StarNode(self, node: StarNode):
        """Draw star shape with n points."""
        cx, cy = self.transform_point(node.cx, node.cy)
        points = []
        
        for i in range(node.points * 2):
            angle = math.pi / 2 + (i * math.pi / node.points)
            if i % 2 == 0:
                r = node.outer_radius
            else:
                r = node.inner_radius
            x = cx + r * math.cos(angle)
            y = cy - r * math.sin(angle)
            points.append((x, y))
        
        self.draw.polygon(points, fill=node.color)
    
    def visit_RoundRectNode(self, node: RoundRectNode):
        """Draw rectangle with rounded corners."""
        x, y = self.transform_point(node.x, node.y)
        w, h, r = node.w, node.h, node.radius
        
        if r == 0:
            # Simple rectangle if no radius
            self.draw.rectangle([x, y, x + w - 1, y + h - 1], fill=node.color)
            return
        
        # Draw main rectangle body (without corners)
        self.draw.rectangle([x + r, y, x + w - 1 - r, y + h - 1], fill=node.color)
        self.draw.rectangle([x, y + r, x + w - 1, y + h - 1 - r], fill=node.color)
        
        # Draw four corner circles
        self.draw.ellipse([x, y, x + 2*r, y + 2*r], fill=node.color)  # Top-left
        self.draw.ellipse([x + w - 1 - 2*r, y, x + w - 1, y + 2*r], fill=node.color)  # Top-right
        self.draw.ellipse([x, y + h - 1 - 2*r, x + 2*r, y + h - 1], fill=node.color)  # Bottom-left
        self.draw.ellipse([x + w - 1 - 2*r, y + h - 1 - 2*r, x + w - 1, y + h - 1], fill=node.color)  # Bottom-right
    
    def visit_HeartNode(self, node: HeartNode):
        """Draw heart shape using bezier curves."""
        cx, cy = self.transform_point(node.cx, node.cy)
        size = node.size
        
        # Generate heart shape points
        points = []
        for i in range(100):
            t = i / 100.0 * 2 * math.pi
            # Heart curve parametric equations
            x = 16 * math.sin(t)**3
            y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            # Scale and translate
            x = cx + x * size / 16
            y = cy + y * size / 16
            points.append((x, y))
        
        self.draw.polygon(points, fill=node.color)
    
    def visit_ArrowNode(self, node: ArrowNode):
        """Draw arrow with arrowhead."""
        x1, y1 = self.transform_point(node.x1, node.y1)
        x2, y2 = self.transform_point(node.x2, node.y2)
        head_size = node.head_size
        
        # Draw main line
        self.draw.line([(x1, y1), (x2, y2)], fill=node.color, width=2)
        
        # Calculate arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Arrowhead points
        left_x = x2 - head_size * math.cos(angle - arrow_angle)
        left_y = y2 - head_size * math.sin(angle - arrow_angle)
        right_x = x2 - head_size * math.cos(angle + arrow_angle)
        right_y = y2 - head_size * math.sin(angle + arrow_angle)
        
        # Draw arrowhead
        self.draw.polygon([(x2, y2), (left_x, left_y), (right_x, right_y)], fill=node.color)
    
    def visit_PaletteNode(self, node: PaletteNode):
        """Define palette color at index."""
        if not hasattr(self, 'palette'):
            self.palette = {}
        self.palette[node.index] = node.color
    
    def visit_SetPaletteNode(self, node: SetPaletteNode):
        """Set active palette color (stored for use with next drawing command)."""
        if not hasattr(self, 'palette'):
            self.palette = {}
        if node.index in self.palette:
            self.active_color = self.palette[node.index]
        else:
            self.active_color = "#000000"  # Default to black if not set
    
    def visit_SpriteNode(self, node: SpriteNode):
        """Draw pixel sprite pattern. Pattern is binary string like '111101000'."""
        x, y = self.transform_point(node.x, node.y)
        pattern = node.pattern
        
        # Assume 3x3 sprite grid
        size = int(math.sqrt(len(pattern)))
        if size * size != len(pattern):
            size = 3  # Default to 3x3
        
        idx = 0
        for row in range(size):
            for col in range(size):
                if idx < len(pattern) and pattern[idx] == '1':
                    self.draw.point((x + col, y + row), fill=node.color)
                idx += 1
    
    def visit_RandomNode(self, node: RandomNode):
        """Generate random number and store it."""
        import random as rnd
        self.last_random = rnd.randint(node.min_val, node.max_val)
    
    def visit_VarNode(self, node: VarNode):
        """Define variable (stored in codegen state)."""
        if not hasattr(self, 'variables'):
            self.variables = {}
        self.variables[node.name] = node.value
    
    def visit_SetNode(self, node: SetNode):
        """Set variable value."""
        if not hasattr(self, 'variables'):
            self.variables = {}
        self.variables[node.name] = node.value


def generate(ast: ProgramNode) -> Image.Image:
    """Convenience function to generate image from AST."""
    codegen = CodeGenerator()
    return codegen.generate(ast)
