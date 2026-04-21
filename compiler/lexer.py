"""
PixelLang Lexer (Lexical Analyzer)
===================================
Deterministic Finite Automaton (DFA) based lexer that tokenizes PixelLang source code.

The lexer recognizes:
- Keywords (30+ reserved words: CANVAS, PIXEL, RECT, LINE, CIRCLE, LOOP, etc.)
- Numbers (sequences of digits)
- Colors (hex codes like #FF0000)
- Identifiers (letter/underscore followed by alphanumeric)
- Punctuation ({, }, ;)
- Comments (// to end of line, /* */ multi-line - discarded)
- Strings (single or double quoted)
- Binary patterns (for SPRITE command)
- Whitespace (skipped)
"""
from .tokens import Token, TokenType, RESERVED_WORDS
from .errors import LexError


class Lexer:
    """
    DFA-based lexer for PixelLang.
    
    The main DFA dispatch:
    - [a-zA-Z_] -> read_word() (keyword or IDENT)
    - [0-9] -> read_number() -> NUMBER
    - [#] -> read_color() -> COLOR
    - [{] -> LBRACE
    - [}] -> RBRACE
    - [;] -> SEMICOLON
    - [/][/] -> skip_comment()
    - [ \t\n\r] -> skip_whitespace()
    - [EOF] -> EOF
    - anything else -> LexError
    """
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
    
    def error(self, msg: str):
        """Raise a lexical error at current position."""
        raise LexError(msg, self.line, self.col)
    
    def peek(self) -> str:
        """Return current character or empty string if at end."""
        if self.pos >= len(self.source):
            return ''
        return self.source[self.pos]
    
    def advance(self) -> str:
        """Consume and return current character, updating line/col."""
        if self.pos >= len(self.source):
            return ''
        
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines, carriage returns."""
        WHITESPACE = ' \t\n\r'
        max_iterations = len(self.source) + 10  # Safety limit
        iterations = 0
        
        while iterations < max_iterations:
            char = self.peek()
            if char == '' or char not in WHITESPACE:
                break
            self.advance()
            iterations += 1
    
    def skip_comment(self):
        """Skip // comment to end of line."""
        # We've already seen //, so consume until newline or EOF
        max_iterations = len(self.source) + 10
        iterations = 0
        while iterations < max_iterations:
            char = self.peek()
            if char == '' or char == '\n':
                break
            self.advance()
            iterations += 1
    
    def skip_multiline_comment(self):
        """Skip /* */ multi-line comment."""
        # We've already seen /*, so consume until */
        max_iterations = len(self.source) + 10
        iterations = 0
        while iterations < max_iterations:
            char = self.peek()
            if char == '':
                self.error("Unterminated multi-line comment: missing */")
                break
            if char == '*' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
                self.advance()  # consume *
                self.advance()  # consume /
                break
            self.advance()
            iterations += 1
    
    def read_word(self) -> Token:
        """
        DFA for words (keywords or identifiers).
        Pattern: [a-zA-Z_][a-zA-Z0-9_]*
        
        q0 --[letter|_]--> q1 --[letter|digit|_]--> q1 (accept)
        """
        start_line = self.line
        start_col = self.col
        
        word = ''
        
        # q0 -> q1 transition: must start with letter or underscore
        char = self.peek()
        if char.isalpha() or char == '_':
            word += self.advance()
        else:
            # This shouldn't happen if called correctly, but handle gracefully
            self.error(f"Expected letter or underscore, got '{char}'")
        
        # q1 loop: read more letters, digits, or underscores
        while True:
            char = self.peek()
            if char.isalnum() or char == '_':
                word += self.advance()
            else:
                break
        
        # Check if it's a reserved word (keyword)
        # Keywords are case-sensitive and must be ALL UPPERCASE
        token_type = RESERVED_WORDS.get(word, TokenType.IDENT)
        
        return Token(token_type, word, start_line, start_col)
    
    def read_binary_pattern(self) -> Token:
        """
        DFA for binary pattern (for SPRITE command).
        Pattern: [01]{9,16} (treat as IDENT for SPRITE)
        """
        start_line = self.line
        start_col = self.col
        
        pattern = ''
        
        # Read binary digits
        while self.peek() in '01':
            pattern += self.advance()
        
        if len(pattern) < 4:
            self.error(f"Invalid binary pattern '{pattern}' - must be at least 4 bits")
        
        return Token(TokenType.IDENT, pattern, start_line, start_col)
    
    def read_number(self) -> Token:
        """
        DFA for NUMBER token.
        Pattern: [0-9]+
        
        q0 --[digit]--> q1 --[digit]--> q1 (accept)
        """
        start_line = self.line
        start_col = self.col
        
        num_str = ''
        
        # Must have at least one digit
        while self.peek().isdigit():
            num_str += self.advance()
        
        if num_str == '':
            self.error(f"Expected number, got '{self.peek()}'")
        
        return Token(TokenType.NUMBER, num_str, start_line, start_col)
    
    def read_color(self) -> Token:
        """
        DFA for COLOR token.
        Pattern: #[0-9A-Fa-f]{6}
        
        q0 --[#]--> q1 --[hex]--> q2 --> q3 --> q4 --> q5 --> q6 --> q7 (accept)
        """
        start_line = self.line
        start_col = self.col
        
        color = self.advance()  # consume #
        
        # Must have exactly 6 hex digits
        for _ in range(6):
            char = self.peek()
            if char in '0123456789ABCDEFabcdef':
                color += self.advance()
            else:
                self.error(f"Invalid color format: expected 6 hex digits after #, got '{char}'")
                # Try to recover by skipping to whitespace
                while self.peek() not in ' \t\n' and self.peek() != '':
                    self.advance()
                return Token(TokenType.COLOR, color, start_line, start_col)
        
        return Token(TokenType.COLOR, color, start_line, start_col)
    
    def read_string(self) -> Token:
        """
        DFA for STRING token (quoted text).
        Pattern: "[^"]*" or '[^']*'
        
        Supports both single and double quotes.
        """
        start_line = self.line
        start_col = self.col
        
        quote = self.advance()  # consume opening quote
        string = ''
        
        while self.peek() != quote and self.peek() != '\0' and self.peek() != '\n':
            char = self.advance()
            string += char
        
        if self.peek() == quote:
            self.advance()  # consume closing quote
        else:
            self.error(f"Unterminated string literal: missing closing {quote}")
        
        return Token(TokenType.STRING, string, start_line, start_col)
    
    def tokenize(self) -> list[Token]:
        """
        Main tokenization loop.
        Returns list of all tokens including EOF.
        """
        self.tokens = []
        
        while True:
            self.skip_whitespace()
            
            char = self.peek()
            start_line = self.line
            start_col = self.col
            
            # EOF check
            if char == '':
                self.tokens.append(Token(TokenType.EOF, '', start_line, start_col))
                break
            
            # Single-character punctuation
            if char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_col))
                continue
            
            if char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_col))
                continue
            
            if char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_col))
                continue
            
            # Comment check (// or /* */)
            if char == '/' and self.pos + 1 < len(self.source):
                if self.source[self.pos + 1] == '/':
                    self.advance()  # consume first /
                    self.advance()  # consume second /
                    self.skip_comment()
                    continue
                elif self.source[self.pos + 1] == '*':
                    self.advance()  # consume /
                    self.advance()  # consume *
                    self.skip_multiline_comment()
                    continue
            
            # Color literal (starts with #)
            if char == '#':
                self.tokens.append(self.read_color())
                continue
            
            # Binary pattern for SPRITE (starts with 0 or 1 and followed by only 0s and 1s, min 4 chars)
            if char in '01':
                # Look ahead to check if this is a binary pattern
                lookahead = self.pos
                while lookahead < len(self.source) and self.source[lookahead] in '01':
                    lookahead += 1
                pattern_len = lookahead - self.pos
                
                # If it's 4+ binary digits and not followed by more digits (0-9), treat as pattern
                if pattern_len >= 4:
                    # Check next char - if it's a digit (2-9), this is a regular number
                    next_char = self.source[lookahead] if lookahead < len(self.source) else ''
                    if not next_char.isdigit():
                        self.tokens.append(self.read_binary_pattern())
                        continue
            
            # String literal (starts with quote)
            if char in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Number (starts with digit)
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Word (keyword or identifier)
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_word())
                continue
            
            # Unknown character
            self.error(f"Unknown character '{char}' - not valid in PixelLang")
        
        return self.tokens


def lex(source: str) -> list[Token]:
    """Convenience function to tokenize source code."""
    lexer = Lexer(source)
    return lexer.tokenize()
