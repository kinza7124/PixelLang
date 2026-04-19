"""
PixelLang Error Classes
========================
Base exception class and specific error types for each compiler phase.
All errors include line and column numbers for GUI highlighting.
"""


class PixelLangError(Exception):
    """Base for all PixelLang compiler errors."""
    pass


class LexError(PixelLangError):
    """Raised by the Lexer for invalid characters or malformed tokens."""
    
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"[LexError] line {line}, col {col}: {message}")
        self.line = line
        self.col = col
        self.message = message
    
    def __str__(self):
        return f"[LexError] line {self.line}, col {self.col}: {self.message}"


class ParseError(PixelLangError):
    """Raised by the Parser for grammar rule violations."""
    
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"[ParseError] line {line}, col {col}: {message}")
        self.line = line
        self.col = col
        self.message = message
    
    def __str__(self):
        return f"[ParseError] line {self.line}, col {self.col}: {self.message}"


class SemanticError(PixelLangError):
    """Raised by SemanticAnalyzer for type/bounds/scope violations."""
    
    def __init__(self, message: str, line: int):
        super().__init__(f"[SemanticError] line {line}: {message}")
        self.line = line
        self.message = message
    
    def __str__(self):
        return f"[SemanticError] line {self.line}: {self.message}"


class CodeGenError(PixelLangError):
    """Raised during code generation if drawing fails."""
    
    def __init__(self, message: str):
        super().__init__(f"[CodeGenError]: {message}")
        self.message = message
    
    def __str__(self):
        return f"[CodeGenError]: {self.message}"


class SymbolError(PixelLangError):
    """Raised by SymbolTable for scope/symbol violations."""
    
    def __init__(self, message: str, line: int = None):
        if line:
            super().__init__(f"[SymbolError] line {line}: {message}")
        else:
            super().__init__(f"[SymbolError]: {message}")
        self.line = line
        self.message = message
