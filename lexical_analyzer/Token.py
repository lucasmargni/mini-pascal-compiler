from typing import List, Dict, Tuple

class Token:
    name : str = ""
    atribute : str = ""

    # constructor
    def __init__(self, name : str, atribute : str = ""):
        self.name = name
        self.atribute = atribute

    # shows the token name and atribute (if exists) between < and >
    def toString(self) -> str:
        string : str = ""

        if(self.atribute):
            string = f"<{self.name}, {self.atribute}>"
        else:
            string = f"<{self.name}>"

        return string
    

    def toTerminal(self) -> str:
        TOKEN_TERMINALS : Dict[Tuple[str, str], str] = {
            ("relop", "lt"): "<",
            ("relop", "leq"): "<=",
            ("relop", "gt"): ">",
            ("relop", "geq"): ">=",
            ("relop", "eq"): "=",
            ("relop", "neq"): "<>",

            ("arithop", "plus"): "+",
            ("arithop", "minus"): "-",
            ("arithop", "mult"): "*",
            ("arithop", "div"): "div",

            ("logicop", "and"): "and",
            ("logicop", "or"): "or",
            ("logicop", "not"): "not",

            ("asign", ""): ":=",
            ("semicolon", ""): ";",
            ("comma", ""): ",",
            ("colon", ""): ":",
            ("dot", ""): ".",
            ("lpar", ""): "(",
            ("rpar", ""): ")",

            ("program", ""): "program",
            ("begin", ""): "begin",
            ("end", ""): "end",
            ("var", ""): "var",
            ("if", ""): "if",
            ("then", ""): "then",
            ("else", ""): "else",
            ("while", ""): "while",
            ("do", ""): "do",
            ("function", ""): "function",
            ("procedure", ""): "procedure",
            ("read", ""): "read",
            ("write", ""): "write",

            ("bool", "true"): "true",
            ("bool", "false"): "false",

            ("type", "integer"): "integer",
            ("type", "boolean"): "boolean",

            ("id", ""): "id",
            ("num", ""): "num"
        }

        # identifiers and numbers ignore attribute
        if (self.name == "id" or self.name == "num"):
            return TOKEN_TERMINALS[(self.name, "")]
        
        elif (self.name, self.atribute) in TOKEN_TERMINALS:
            return TOKEN_TERMINALS[(self.name, self.atribute)]

        else:
            return "unknown"
    
    # checks if the current token matches the given grammar terminal
    def equals(self, terminal: str) -> bool:
        return self.toTerminal() == terminal