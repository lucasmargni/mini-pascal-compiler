from typing import Optional

class Symbol:
    name: str = ""                  # lexeme
    symbol_type = ""                # var, const, function, procedure
    data_type: Optional[str] = ""   # integer, boolean, none (for procedures and program)
    can_be_assigned: bool = False   #

    def __init__(self, name: str, symbol_type: str, data_type: Optional[str] = None, can_be_assigned: bool = False):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type

        if (symbol_type == "var"):
            self.can_be_assigned = True
        else:
            self.can_be_assigned = can_be_assigned