"""
PixelLang Symbol Table
=======================
Stack-based scoped symbol table for managing:
- Canvas dimensions
- Transform state (tx, ty, angle)
- Loop counters and scope depth
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .errors import SymbolError


@dataclass
class Symbol:
    """Entry in the symbol table."""
    name: str
    kind: str
    value: Any
    value_type: str
    defined_at: int
    scope_depth: int


class SymbolTable:
    """
    Scoped symbol table using a stack of dictionaries.
    Each scope is a dictionary mapping names to Symbols.
    """
    
    def __init__(self):
        # Stack of scopes - [0] is global, higher indices are nested
        self.scopes: List[Dict[str, Symbol]] = [{}]
    
    def enter_scope(self):
        """Push a new scope onto the stack (called when entering a LOOP)."""
        self.scopes.append({})
    
    def exit_scope(self):
        """Pop the current scope (called when exiting a LOOP)."""
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def depth(self) -> int:
        """Return current scope depth (0 = global)."""
        return len(self.scopes) - 1
    
    def define(self, name: str, kind: str, value: Any, value_type: str, line: int):
        """
        Define a new symbol in the current scope.
        Raises SymbolError if name already exists in current scope.
        """
        if name in self.scopes[-1]:
            raise SymbolError(f"'{name}' already defined in this scope", line)
        
        self.scopes[-1][name] = Symbol(
            name=name,
            kind=kind,
            value=value,
            value_type=value_type,
            defined_at=line,
            scope_depth=self.depth()
        )
    
    def lookup(self, name: str) -> Symbol:
        """
        Look up a symbol by name, searching from innermost to outermost scope.
        Raises SymbolError if not found.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SymbolError(f"Undefined symbol: '{name}'")
    
    def lookup_current(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in the current scope only."""
        return self.scopes[-1].get(name)
    
    def update(self, name: str, new_value: Any):
        """
        Update the value of an existing symbol.
        Searches from innermost to outermost scope.
        Raises SymbolError if not found.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name].value = new_value
                return
        raise SymbolError(f"Cannot update undefined: '{name}'")
    
    def is_defined(self, name: str) -> bool:
        """Check if a symbol is defined (in any scope)."""
        try:
            self.lookup(name)
            return True
        except SymbolError:
            return False
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols from all scopes."""
        symbols = []
        for scope in self.scopes:
            symbols.extend(scope.values())
        return symbols
    
    def __str__(self):
        """Pretty print the symbol table."""
        lines = ["Symbol Table:"]
        for i, scope in enumerate(self.scopes):
            lines.append(f"  Scope {i}:")
            for name, sym in scope.items():
                lines.append(f"    {name}: {sym.value} ({sym.kind}, {sym.value_type})")
        return "\n".join(lines)
