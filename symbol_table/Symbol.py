from typing import Optional

class Symbol:
    name: str                       # lexeme
    symbol_type: str                # var, function, procedure, program
    data_type: Optional[str]        # integer, boolean, none (for procedures and program)
    can_be_assigned: bool           # true if is a id or a function for returns
    param_types: list[str]          # list of types for functions and procedures
    level: int                      # lexical level
    offset: int                     # offset with respect to D[level]
    label: Optional[str]            # label (procedures and functions)
    num_params: int                 # for procedures and functions

    def __init__(self, name: str, symbol_type: str, data_type: Optional[str] = None, can_be_assigned: bool = False):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type
        self.param_types = []

        if (symbol_type == "var"):
            self.can_be_assigned = True
        else:
            self.can_be_assigned = can_be_assigned

        self.level = 0
        self.offset = 0
        self.label = None
        self.num_params = 0

    def set_param_types(self, param_types: list[str]):
        self.param_types = param_types