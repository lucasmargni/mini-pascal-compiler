from Token import Token
from typing import List, Dict
import sys

# parameter: name of the input file
if(len(sys.argv) < 2):
    print("Error: it is required the name of the input file as parameter")
    sys.exit(1)

class LexicalAnalyzer:
    # pascal file recived
    input_file : str = ""
    file = None

    # local variables for functionality
    state : str = "start"
    char : str = ""
    row : int = 1
    col : int = 0

    # symbol table storing pointers to all numbers and identifiers
    symbol_table : List[str] = []

    # dictionary of all key words with corresponding token
    key_words : Dict[str, Token] = {
        "div" : Token("arithop", "div"),
        "and" : Token("logicop", "and"),
        "or" : Token("logicop", "or"),
        "not" : Token("logicop", "not"),
        "program" : Token("program"),
        "begin" : Token("begin"),
        "end" : Token("end"),
        "var" : Token("var"),
        "if" : Token("if"),
        "then" : Token("then"),
        "else" : Token("else"),
        "while" : Token("while"),
        "do" : Token("do"),
        "function" : Token("function"),
        "procedure" : Token("procedure"),
        "read" : Token("read"),
        "write" : Token("write"),
        "true" : Token("bool", "true"),
        "false" : Token("bool", "false"),
        "integer" : Token("type", "integer"),
        "boolean" : Token("type", "boolean")
    }

    no_more_tokens : bool = False

    def __init__(self, input_file):
        self.input_file = input_file

        self.file = open(self.input_file, "r")    

    def read_char(self) -> str:
        if(self.char == "\n"):
            # last char in row
            self.row += 1
            self.col = 1
        else:
            self.col += 1

        return self.file.read(1)
    
    def go_back(self):
        self.col -= 1

        self.file.seek(self.file.tell() - 1)

    def next_token(self) -> Token | None:
        if(self.no_more_tokens):
            return None
        
        curr_word : str = ""
        self.state = "start"

        while(1):
            match self.state:
                case "start":
                    # read a character and continue in correspondig state
                    self.char = self.read_char()

                    match self.char:
                        case "<":
                            self.state = "saw_lt"
                        case ">":
                            self.state = "saw_gt"
                        case "=":
                            self.state = "got_eq"
                        case "+":
                            self.state = "got_plus"
                        case "-":
                            self.state = "got_minus"
                        case "*":
                            self.state = "got_mult"
                        case ":":
                            self.state = "saw_colon"
                        case ";":
                            self.state = "got_semicolon"
                        case ",":
                            self.state = "got_comma"
                        case ".":
                            self.state = "got_dot"
                        case "(":
                            self.state = "got_lpar"
                        case ")":
                            self.state = "got_rpar"
                        case " " | "\n" | "\r" | "\t":
                            self.state = "start"
                        case "{":
                            self.state = "in_comment"
                        case _ if self.char.isalpha():
                            self.state = "in_letter"
                        case _ if self.char.isdigit():
                            self.state = "in_digit"
                        case "":
                            self.no_more_tokens = True
                            self.file.close()
                            return None
                        case _:
                            # othewise
                            print(f"Error: invalid character detected: {self.char} (row {self.row}, col {self.col})")
                            self.file.close()
                            sys.exit(1)
                
                # cases when it can continue with more characters
                case "saw_lt":
                    next_char : str = self.read_char()

                    if(next_char == "="):
                        self.state = "got_leq"
                    elif(next_char == ">"):
                        self.state = "got_neq"
                    else:
                        # go back a character and process only lt
                        self.go_back()
                        self.state = "got_lt"
                    
                case "saw_gt":
                    next_char : str = self.read_char()

                    if(next_char == "="):
                        self.state = "got_geq"
                    else:
                        # go back a character and process only gt
                        self.go_back()
                        self.state = "got_gt"

                case "saw_colon":
                    next_char : str = self.read_char()

                    if(next_char == "="):
                        self.state = "got_asign"
                    else:
                        # go back a character and process only colon
                        self.go_back()
                        self.state = "got_colon"

                case "in_comment":
                    next_char : str = self.char

                    while(next_char not in ["}", ""]):
                        # continue in_comment until close comment or end of file
                        next_char : str = self.read_char()
                        
                    if(next_char == "}"):
                        self.state = "start"
                    else:
                        # end of file reached
                        print(f"Error: comment opened but not closed (row {self.row}, col {self.col})")
                        self.file.close()
                        exit(1)
                case "in_digit":
                    next_char : str = self.char
                    curr_word = ""

                    while(next_char.isdigit()):
                        # continue processing word (number)
                        curr_word += next_char
                        next_char : str = self.read_char()

                    # go back a character and process the current word (number)
                    self.go_back()
                    self.state = "got_num"

                case "in_letter":
                    next_char : str = self.char
                    curr_word = ""

                    while(next_char.isalpha() or next_char.isdigit()):
                        # continue processing word (key word or identifier)
                        curr_word += next_char
                        next_char : str = self.read_char()

                    # go back a character and process the current word (key word or identifier)
                    self.go_back()
                    self.state = "got_word"

                # cases when the current word is a token
                case "got_lt":
                    return Token("relop", "lt")
                case "got_leq":
                    return Token("relop", "leq")
                case "got_gt":
                    return Token("relop", "gt")
                case "got_geq":
                    return Token("relop", "geq")
                case "got_eq":
                    return Token("relop", "eq")
                case "got_neq":
                    return Token("relop", "neq")
                case "got_plus":
                    return Token("arithop", "plus")
                case "got_minus":
                    return Token("arithop", "minus")
                case "got_mult":
                    return Token("arithop", "mult")
                case "got_asign":
                    return Token("asign")
                case "got_semicolon":
                    return Token("semicolon")
                case "got_comma":
                    return Token("comma")
                case "got_colon":
                    return Token("colon")
                case "got_dot":
                    return Token("dot")
                case "got_lpar":
                    return Token("lpar")
                case "got_rpar":
                    return Token("rpar")
                case "got_num":
                    # verify symbol table pointer of current word
                    if(curr_word not in self.symbol_table):
                        self.symbol_table.append(curr_word)
                    
                    return Token(curr_word, str(self.symbol_table.index(curr_word)))
                    
                case "got_word":
                    if(curr_word.lower() in self.key_words):
                        # current word is a key word
                        return self.key_words[curr_word.lower()]
                    else:
                        # current word is a identifier, verify symbol table pointer
                        if(curr_word not in self.symbol_table):
                            self.symbol_table.append(curr_word)
            
                    return Token(curr_word, str(self.symbol_table.index(curr_word)))