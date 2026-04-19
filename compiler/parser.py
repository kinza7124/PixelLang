"""
PixelLang Parser (Syntax Analyzer)
===================================
LL(1) Recursive Descent Parser implementing the formal grammar.

Grammar (BNF):
    <program>       ::= <statement>* EOF
    <statement>     ::= <canvas_stmt> | <pixel_stmt> | <rect_stmt> | <line_stmt>
                       | <circle_stmt> | <loop_stmt> | <translate_stmt> | <rotate_stmt>
    <canvas_stmt>   ::= CANVAS NUMBER NUMBER SEMICOLON
    <pixel_stmt>    ::= PIXEL NUMBER NUMBER COLOR SEMICOLON
    <rect_stmt>     ::= RECT NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
    <line_stmt>     ::= LINE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
    <circle_stmt>   ::= CIRCLE NUMBER NUMBER NUMBER COLOR SEMICOLON
    <loop_stmt>     ::= LOOP NUMBER LBRACE <statement>* RBRACE
    <translate_stmt>::= TRANSLATE NUMBER NUMBER SEMICOLON
    <rotate_stmt>   ::= ROTATE NUMBER SEMICOLON

This is LL(1) because each statement alternative starts with a distinct keyword,
so we can select the production with one token of lookahead.
"""
from .tokens import Token, TokenType
from .ast_nodes import *
from .errors import ParseError


class Parser:
    """
    LL(1) Recursive Descent Parser for PixelLang.
    """
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current(self) -> Token:
        """Return current token without consuming."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def peek(self, offset: int = 0) -> Token:
        """Look ahead by offset tokens."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF
    
    def advance(self) -> Token:
        """Consume and return current token."""
        tok = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok
    
    def expect(self, expected_type: TokenType) -> Token:
        """
        Expect a specific token type, consume and return it.
        Raises ParseError if token type doesn't match.
        """
        tok = self.current()
        if tok.type != expected_type:
            raise ParseError(
                f"Expected {expected_type.name}, got '{tok.value}' ({tok.type.name})",
                tok.line, tok.col
            )
        return self.advance()
    
    def expect_number(self) -> int:
        """Expect and return a NUMBER token value as int."""
        tok = self.expect(TokenType.NUMBER)
        return int(tok.value)
    
    def expect_color(self) -> str:
        """Expect and return a COLOR token value."""
        tok = self.expect(TokenType.COLOR)
        return tok.value
    
    def parse(self) -> ProgramNode:
        """
        Parse the token stream into an AST.
        Entry point: <program> ::= <statement>* EOF
        """
        statements = []
        
        while self.current().type != TokenType.EOF:
            statements.append(self.parse_statement())
        
        return ProgramNode(statements)
    
    def parse_statement(self) -> ASTNode:
        """
        Parse a single statement.
        LL(1) dispatch based on first token (lookahead).
        """
        tok = self.current()
        
        # LL(1) parse table: select production based on lookahead token
        if tok.type == TokenType.CANVAS:
            return self.parse_canvas()
        elif tok.type == TokenType.PIXEL:
            return self.parse_pixel()
        elif tok.type == TokenType.RECT:
            return self.parse_rect()
        elif tok.type == TokenType.LINE:
            return self.parse_line()
        elif tok.type == TokenType.CIRCLE:
            return self.parse_circle()
        elif tok.type == TokenType.FILL:
            return self.parse_fill()
        elif tok.type == TokenType.ELLIPSE:
            return self.parse_ellipse()
        elif tok.type == TokenType.CLEAR:
            return self.parse_clear()
        elif tok.type == TokenType.BORDER:
            return self.parse_border()
        elif tok.type == TokenType.TRIANGLE:
            return self.parse_triangle()
        elif tok.type == TokenType.ARC:
            return self.parse_arc()
        elif tok.type == TokenType.POLYGON:
            return self.parse_polygon()
        elif tok.type == TokenType.TEXT:
            return self.parse_text()
        elif tok.type == TokenType.MIRROR:
            return self.parse_mirror()
        elif tok.type == TokenType.SCALE:
            return self.parse_scale()
        elif tok.type == TokenType.LOOP:
            return self.parse_loop()
        elif tok.type == TokenType.TRANSLATE:
            return self.parse_translate()
        elif tok.type == TokenType.ROTATE:
            return self.parse_rotate()
        # v2.0 Advanced Commands
        elif tok.type == TokenType.BEZIER:
            return self.parse_bezier()
        elif tok.type == TokenType.STAR:
            return self.parse_star()
        elif tok.type == TokenType.ROUNDRECT:
            return self.parse_roundrect()
        elif tok.type == TokenType.HEART:
            return self.parse_heart()
        elif tok.type == TokenType.ARROW:
            return self.parse_arrow()
        elif tok.type == TokenType.PALETTE:
            return self.parse_palette()
        elif tok.type == TokenType.SETPALETTE:
            return self.parse_setpalette()
        elif tok.type == TokenType.SPRITE:
            return self.parse_sprite()
        elif tok.type == TokenType.RANDOM:
            return self.parse_random()
        elif tok.type == TokenType.VAR:
            return self.parse_var()
        elif tok.type == TokenType.SET:
            return self.parse_set()
        else:
            raise ParseError(
                f"Unexpected token '{tok.value}' - expected a drawing command",
                tok.line, tok.col
            )
    
    def parse_canvas(self) -> CanvasNode:
        """
        <canvas_stmt> ::= CANVAS NUMBER NUMBER SEMICOLON
        """
        tok = self.advance()  # consume CANVAS
        line = tok.line
        width = self.expect_number()
        height = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return CanvasNode(width, height, line)
    
    def parse_pixel(self) -> PixelNode:
        """
        <pixel_stmt> ::= PIXEL NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume PIXEL
        line = tok.line
        x = self.expect_number()
        y = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return PixelNode(x, y, color, line)
    
    def parse_rect(self) -> RectNode:
        """
        <rect_stmt> ::= RECT NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume RECT
        line = tok.line
        x = self.expect_number()
        y = self.expect_number()
        w = self.expect_number()
        h = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return RectNode(x, y, w, h, color, line)
    
    def parse_line(self) -> LineNode:
        """
        <line_stmt> ::= LINE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume LINE
        line = tok.line
        x1 = self.expect_number()
        y1 = self.expect_number()
        x2 = self.expect_number()
        y2 = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return LineNode(x1, y1, x2, y2, color, line)
    
    def parse_circle(self) -> CircleNode:
        """
        <circle_stmt> ::= CIRCLE NUMBER NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume CIRCLE
        line = tok.line
        cx = self.expect_number()
        cy = self.expect_number()
        r = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return CircleNode(cx, cy, r, color, line)
    
    def parse_fill(self) -> FillNode:
        """
        <fill_stmt> ::= FILL NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume FILL
        line = tok.line
        x = self.expect_number()
        y = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return FillNode(x, y, color, line)
    
    def parse_ellipse(self) -> EllipseNode:
        """
        <ellipse_stmt> ::= ELLIPSE NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume ELLIPSE
        line = tok.line
        cx = self.expect_number()
        cy = self.expect_number()
        rx = self.expect_number()
        ry = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return EllipseNode(cx, cy, rx, ry, color, line)
    
    def parse_clear(self) -> ClearNode:
        """
        <clear_stmt> ::= CLEAR COLOR SEMICOLON
        """
        tok = self.advance()  # consume CLEAR
        line = tok.line
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return ClearNode(color, line)
    
    def parse_border(self) -> BorderNode:
        """
        <border_stmt> ::= BORDER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume BORDER
        line = tok.line
        x = self.expect_number()
        y = self.expect_number()
        w = self.expect_number()
        h = self.expect_number()
        thickness = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return BorderNode(x, y, w, h, thickness, color, line)
    
    def parse_triangle(self) -> TriangleNode:
        """
        <triangle_stmt> ::= TRIANGLE NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        """
        tok = self.advance()  # consume TRIANGLE
        line = tok.line
        x1 = self.expect_number()
        y1 = self.expect_number()
        x2 = self.expect_number()
        y2 = self.expect_number()
        x3 = self.expect_number()
        y3 = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return TriangleNode(x1, y1, x2, y2, x3, y3, color, line)
    
    def parse_arc(self) -> ArcNode:
        """
        <arc_stmt> ::= ARC NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        Draws circular arc from start angle to end angle (in degrees).
        """
        tok = self.advance()  # consume ARC
        line = tok.line
        cx = self.expect_number()
        cy = self.expect_number()
        radius = self.expect_number()
        start = self.expect_number()
        end = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return ArcNode(cx, cy, radius, start, end, color, line)
    
    def parse_polygon(self) -> PolygonNode:
        """
        <polygon_stmt> ::= POLYGON NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        Draws 4-point polygon (quad). Format: x1 y1 x2 y2 x3 y3 x4 y4 #COLOR
        """
        tok = self.advance()  # consume POLYGON
        line = tok.line
        # Parse 4 points (x, y pairs)
        points = []
        for _ in range(4):
            x = self.expect_number()
            y = self.expect_number()
            points.append((x, y))
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return PolygonNode(points, color, line)
    
    def parse_text(self) -> TextNode:
        """
        <text_stmt> ::= TEXT NUMBER NUMBER IDENT COLOR SEMICOLON
        Draws text string at position. Text is an identifier (use UPPERCASE).
        """
        tok = self.advance()  # consume TEXT
        line = tok.line
        x = self.expect_number()
        y = self.expect_number()
        # Text is parsed as an identifier
        text_tok = self.expect(TokenType.IDENT)
        text = text_tok.value
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return TextNode(x, y, text, color, line)
    
    def parse_mirror(self) -> MirrorNode:
        """
        <mirror_stmt> ::= MIRROR NUMBER SEMICOLON
        Mirrors context: 0=horizontal (flip Y), 1=vertical (flip X)
        """
        tok = self.advance()  # consume MIRROR
        line = tok.line
        axis = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return MirrorNode(axis, line)
    
    def parse_scale(self) -> ScaleNode:
        """
        <scale_stmt> ::= SCALE NUMBER SEMICOLON
        Scales drawing context by factor (1-10).
        """
        tok = self.advance()  # consume SCALE
        line = tok.line
        factor = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return ScaleNode(factor, line)
    
    def parse_loop(self) -> LoopNode:
        """
        <loop_stmt> ::= LOOP NUMBER LBRACE <statement>* RBRACE
        """
        tok = self.advance()  # consume LOOP
        line = tok.line
        count = self.expect_number()
        self.expect(TokenType.LBRACE)
        
        body = []
        while self.current().type != TokenType.RBRACE:
            if self.current().type == TokenType.EOF:
                raise ParseError(
                    "Unexpected EOF - missing closing brace '}'",
                    self.current().line, self.current().col
                )
            body.append(self.parse_statement())
        
        self.expect(TokenType.RBRACE)
        return LoopNode(count, body, line)
    
    def parse_translate(self) -> TranslateNode:
        """
        <translate_stmt> ::= TRANSLATE NUMBER NUMBER SEMICOLON
        """
        tok = self.advance()  # consume TRANSLATE
        line = tok.line
        dx = self.expect_number()
        dy = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return TranslateNode(dx, dy, line)
    
    def parse_rotate(self) -> RotateNode:
        """
        <rotate_stmt> ::= ROTATE NUMBER SEMICOLON
        """
        tok = self.advance()  # consume ROTATE
        line = tok.line
        angle = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return RotateNode(angle, line)


    def parse_bezier(self) -> BezierNode:
        """
        <bezier_stmt> ::= BEZIER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        Format: x1 y1 cx1 cy1 cx2 cy2 x2 y2 #COLOR
        """
        tok = self.advance()
        line = tok.line
        x1 = self.expect_number()
        y1 = self.expect_number()
        cx1 = self.expect_number()
        cy1 = self.expect_number()
        cx2 = self.expect_number()
        cy2 = self.expect_number()
        x2 = self.expect_number()
        y2 = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return BezierNode(x1, y1, cx1, cy1, cx2, cy2, x2, y2, color, line)
    
    def parse_star(self) -> StarNode:
        """
        <star_stmt> ::= STAR NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        Format: cx cy outer_r inner_r points #COLOR
        """
        tok = self.advance()
        line = tok.line
        cx = self.expect_number()
        cy = self.expect_number()
        outer_r = self.expect_number()
        inner_r = self.expect_number()
        points = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return StarNode(cx, cy, outer_r, inner_r, points, color, line)
    
    def parse_roundrect(self) -> RoundRectNode:
        """
        <roundrect_stmt> ::= ROUNDRECT NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        Format: x y w h radius #COLOR
        """
        tok = self.advance()
        line = tok.line
        x = self.expect_number()
        y = self.expect_number()
        w = self.expect_number()
        h = self.expect_number()
        radius = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return RoundRectNode(x, y, w, h, radius, color, line)
    
    def parse_heart(self) -> HeartNode:
        """
        <heart_stmt> ::= HEART NUMBER NUMBER NUMBER COLOR SEMICOLON
        Format: cx cy size #COLOR
        """
        tok = self.advance()
        line = tok.line
        cx = self.expect_number()
        cy = self.expect_number()
        size = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return HeartNode(cx, cy, size, color, line)
    
    def parse_arrow(self) -> ArrowNode:
        """
        <arrow_stmt> ::= ARROW NUMBER NUMBER NUMBER NUMBER NUMBER COLOR SEMICOLON
        Format: x1 y1 x2 y2 head_size #COLOR
        """
        tok = self.advance()
        line = tok.line
        x1 = self.expect_number()
        y1 = self.expect_number()
        x2 = self.expect_number()
        y2 = self.expect_number()
        head_size = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return ArrowNode(x1, y1, x2, y2, head_size, color, line)
    
    def parse_palette(self) -> PaletteNode:
        """
        <palette_stmt> ::= PALETTE NUMBER COLOR SEMICOLON
        Format: index #COLOR (index 0-15)
        """
        tok = self.advance()
        line = tok.line
        index = self.expect_number()
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return PaletteNode(index, color, line)
    
    def parse_setpalette(self) -> SetPaletteNode:
        """
        <setpalette_stmt> ::= SETPALETTE NUMBER SEMICOLON
        Format: index (index 0-15)
        """
        tok = self.advance()
        line = tok.line
        index = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return SetPaletteNode(index, line)
    
    def parse_sprite(self) -> SpriteNode:
        """
        <sprite_stmt> ::= SPRITE NUMBER NUMBER IDENT COLOR SEMICOLON
        Format: x y pattern #COLOR (pattern is binary string identifier)
        """
        tok = self.advance()
        line = tok.line
        x = self.expect_number()
        y = self.expect_number()
        pattern_tok = self.expect(TokenType.IDENT)
        pattern = pattern_tok.value
        color = self.expect_color()
        self.expect(TokenType.SEMICOLON)
        return SpriteNode(x, y, pattern, color, line)
    
    def parse_random(self) -> RandomNode:
        """
        <random_stmt> ::= RANDOM NUMBER NUMBER SEMICOLON
        Format: min max
        """
        tok = self.advance()
        line = tok.line
        min_val = self.expect_number()
        max_val = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return RandomNode(min_val, max_val, line)
    
    def parse_var(self) -> VarNode:
        """
        <var_stmt> ::= VAR IDENT NUMBER SEMICOLON
        Format: name value
        """
        tok = self.advance()
        line = tok.line
        name_tok = self.expect(TokenType.IDENT)
        name = name_tok.value
        value = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return VarNode(name, value, line)
    
    def parse_set(self) -> SetNode:
        """
        <set_stmt> ::= SET IDENT NUMBER SEMICOLON
        Format: name value
        """
        tok = self.advance()
        line = tok.line
        name_tok = self.expect(TokenType.IDENT)
        name = name_tok.value
        value = self.expect_number()
        self.expect(TokenType.SEMICOLON)
        return SetNode(name, value, line)


def parse(tokens: list[Token]) -> ProgramNode:
    """Convenience function to parse tokens into an AST."""
    parser = Parser(tokens)
    return parser.parse()
