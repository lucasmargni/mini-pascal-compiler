from typing import Optional

class Symbol:
    name: str                       # lexeme
    symbol_type: str                # var, function, procedure, program
    data_type: Optional[str]        # integer, boolean, none (for procedures and program)
    can_be_assigned: bool           # true if is a id or a function for returns
    param_types: list[str]          # list of types for functions and procedures

    def __init__(self, name: str, symbol_type: str, data_type: Optional[str] = None, can_be_assigned: bool = False):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type
        self.param_types = []

        if (symbol_type == "var"):
            self.can_be_assigned = True
        else:
            self.can_be_assigned = can_be_assigned

    def set_param_types(self, param_types: list[str]):
        self.param_types = param_types