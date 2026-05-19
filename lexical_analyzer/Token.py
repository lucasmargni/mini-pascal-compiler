from typing import List, Dict

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
    
    # checks if the current token matches the given grammar terminal
    def equals(self, terminal: str) -> bool:

        terminal_relop: Dict[str, str] = {
            "<": "lt",
            "<=": "leq",
            ">": "gt",
            ">=": "geq",
            "=": "eq",
            "<>": "neq"
        }

        terminal_arithop: Dict[str, str] = {
            "+": "plus",
            "-": "minus",
            "*": "mult",
            "div": "div"
        }

        terminal_logicop: Dict[str, str] = {
            "and": "and",
            "or": "or",
            "not": "not"
        }

        terminal_punctuation_marks: Dict[str, str] = {
            ":=": "asign",
            ";": "semicolon",
            ",": "comma",
            ":": "colon",
            ".": "dot",
            "(": "lpar",
            ")": "rpar"
        }

        terminal_literals : List[str] = [
            "program",
            "begin",
            "end",
            "var",
            "if",
            "then",
            "else",
            "while",
            "do",
            "function",
            "procedure",
            "read",
            "write"
        ]

        terminal_bool : List[str] = [
            "true",
            "false"
        ]

        terminal_type : List[str] = [
            "integer",
            "boolean"
        ]

        # identifier
        if terminal == "id":
            return self.name == "id"

        # number
        elif terminal == "num":
            return self.name == "num"

        # relational operators
        elif terminal in terminal_relop:
            return self.name == "relop" and self.atribute == terminal_relop[terminal]

        # arithmetic operators
        elif terminal in terminal_arithop:
            return self.name == "arithop" and self.atribute == terminal_arithop[terminal]

        # logical operators
        elif terminal in terminal_logicop:
            return self.name == "logicop" and self.atribute == terminal_logicop[terminal]

        # punctuation marks
        elif terminal in terminal_punctuation_marks:
            return self.name == terminal_punctuation_marks[terminal]

        # reserved words
        elif terminal in terminal_literals:
            return self.name == terminal

        # boolean constants
        elif terminal in terminal_bool:
            return self.name == "bool" and self.atribute == terminal

        # types
        elif terminal in terminal_type:
            return self.name == "type" and self.atribute == terminal

        return False