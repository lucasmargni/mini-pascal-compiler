class Symbol:
    name: str = ""                  # lexeme
    symbol_type = ""                # var, const, function, procedure
    data_type: str | None = ""      # integer, boolean

    def __init__(self, name, symbol_type, data_type):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type