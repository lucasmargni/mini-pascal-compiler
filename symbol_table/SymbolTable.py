from __future__ import annotations
from typing import Optional
from symbol_table import Symbol

class SymbolTable:
    table: dict[str, Symbol] = {}           # actual symbol table with data
    prev: Optional[SymbolTable] = None      # reference to the symbol table above in the environment

    def __init__(self, prev = None):
        self.prev = prev

    def add_symbol(self, symbol: Symbol):
        self.table[symbol.name] = symbol

    def get_symbol(self, name: str) -> Optional[Symbol]:
        if(name in self.table):
            return self.table[name]
        elif(self.prev != None):
            return self.prev.get_symbol(name)
        else:
            # there is no previous environment
            return None

    def delete_symbol(self, name: str) -> bool:
        if(name in self.table):
            del self.table[name]
            return True
        else:
            return False

    # checks if the symbol exists in the current symbol table
    def exists_symbol(self, name: str) -> bool:
        if(name in self.table):
            return True
        else:
            return False