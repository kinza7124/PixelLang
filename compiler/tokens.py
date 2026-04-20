"""
PixelLang Token Definitions
============================
TokenType enum and Token dataclass for lexical analysis.
"""
from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    """All token types in PixelLang."""
    
    # Keywords (18 reserved words)
    CANVAS = auto()
    PIXEL = auto()
    RECT = auto()
    LINE = auto()
    CIRCLE = auto()
    FILL = auto()  # Flood fill command
    ELLIPSE = auto()  # Draw ellipse with rx, ry
    CLEAR = auto()  # Clear/fill entire canvas
    BORDER = auto()  # Hollow rectangle border
    TRIANGLE = auto()  # 3-point polygon
    ARC = auto()  # Draw circular arc
    POLYGON = auto()  # Multi-point polygon
    TEXT = auto()  # Draw text
    MIRROR = auto()  # Mirror/flip context
    SCALE = auto()  # Scale transform
    LOOP = auto()
    TRANSLATE = auto()
    ROTATE = auto()
    
    # Advanced Drawing Commands v2.0
    BEZIER = auto()       # Cubic Bezier curve
    STAR = auto()         # Star shape with n points
    ROUNDRECT = auto()    # Rectangle with rounded corners
    HEART = auto()        # Heart shape
    ARROW = auto()        # Arrow shape
    
    # Palette & Color Management
    PALETTE = auto()      # Define color palette
    SETPALETTE = auto()   # Set active palette color
    
    # Advanced Features
    SPRITE = auto()       # Draw pixel sprite pattern
    RANDOM = auto()       # Random number for generative art
    
    # Variable support (limited)
    VAR = auto()          # Define variable
    SET = auto()          # Set variable value
    
    # Literals
    NUMBER = auto()
    COLOR = auto()
    STRING = auto()  # Quoted string literal
    
    # Identifiers
    IDENT = auto()
    
    # Punctuation
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    
    # Sentinel
    EOF = auto()


# Reserved words dictionary - maps uppercase strings to token types
RESERVED_WORDS: dict[str, TokenType] = {
    "CANVAS": TokenType.CANVAS,
    "PIXEL": TokenType.PIXEL,
    "RECT": TokenType.RECT,
    "LINE": TokenType.LINE,
    "CIRCLE": TokenType.CIRCLE,
    "FILL": TokenType.FILL,
    "ELLIPSE": TokenType.ELLIPSE,
    "CLEAR": TokenType.CLEAR,
    "BORDER": TokenType.BORDER,
    "TRIANGLE": TokenType.TRIANGLE,
    "ARC": TokenType.ARC,
    "POLYGON": TokenType.POLYGON,
    "TEXT": TokenType.TEXT,
    "MIRROR": TokenType.MIRROR,
    "SCALE": TokenType.SCALE,
    "LOOP": TokenType.LOOP,
    "TRANSLATE": TokenType.TRANSLATE,
    "ROTATE": TokenType.ROTATE,
    # v2.0 Advanced Commands
    "BEZIER": TokenType.BEZIER,
    "STAR": TokenType.STAR,
    "ROUNDRECT": TokenType.ROUNDRECT,
    "HEART": TokenType.HEART,
    "ARROW": TokenType.ARROW,
    "PALETTE": TokenType.PALETTE,
    "SETPALETTE": TokenType.SETPALETTE,
    "SPRITE": TokenType.SPRITE,
    "RANDOM": TokenType.RANDOM,
    "VAR": TokenType.VAR,
    "SET": TokenType.SET,
}


@dataclass
class Token:
    """A token with type, value (lexeme), and position information."""
    type: TokenType
    value: str
    line: int
    col: int
    
    def __str__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.col})"
    
    def __repr__(self):
        return self.__str__()
