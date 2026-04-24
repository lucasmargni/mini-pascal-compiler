from Token import Token
from typing import List, Dict
import sys

# parameter: name of the input file
if(len(sys.argv) < 2):
    print("Error: it is required the name of the input file as parameter")
    sys.exit(1)

# pascal file recived
input_file : str = sys.argv[1]

# local variables for functionality
state : str = "start"
char : str = ""
curr_word : str = ""

# list of all tokens generated from the input file
token_list : List[Token] = []

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

file = open(input_file, "r")

while(state != "end"):
    #print(state)
    match state:
        case "start":
            # read a character and continue in correspondig state
            char = file.read(1)

            match char:
                case "<":
                    state = "saw_lt"
                case ">":
                    state = "saw_gt"
                case "=":
                    state = "got_eq"
                case "+":
                    state = "got_plus"
                case "-":
                    state = "got_minus"
                case "*":
                    state = "got_mult"
                case ":":
                    state = "saw_colon"
                case ";":
                    state = "got_semicolon"
                case ",":
                    state = "got_comma"
                case ".":
                    state = "got_dot"
                case "(":
                    state = "got_lpar"
                case ")":
                    state = "got_rpar"
                case " " | "\n" | "\r" | "\t":
                    state = "start"
                case "{":
                    state = "in_comment"
                case _ if char.isalpha():
                    state = "in_letter"
                case _ if char.isdigit():
                    state = "in_digit"
                case "":
                    state = "end"
                case _:
                    # othewise
                    print(f"Error: invalid character detected: {char}")
                    sys.exit(1)
        
        # cases when it can continue with more characters
        case "saw_lt":
            next_char : str = file.read(1)

            if(next_char == "="):
                state = "got_leq"
            elif(next_char == ">"):
                state = "got_neq"
            else:
                # go back a character and process only lt
                file.seek(file.tell() - 1)
                state = "got_lt"
            
        case "saw_gt":
            next_char : str = file.read(1)

            if(next_char == "="):
                state = "got_geq"
            else:
                # go back a character and process only gt
                file.seek(file.tell() - 1)
                state = "got_gt"

        case "saw_colon":
            next_char : str = file.read(1)

            if(next_char == "="):
                state = "got_asign"
            else:
                # go back a character and process only colon
                file.seek(file.tell() - 1)
                state = "got_colon"

        case "in_comment":
            next_char : str = char

            while(next_char not in ["}", ""]):
                # continue in_comment until close comment or end of file
                next_char : str = file.read(1)
                
            if(next_char == "}"):
                state = "start"
            else:
                print(f"Error: comment opened but not closed")
                sys.exit(1)
            
        case "in_digit":
            next_char : str = char
            curr_word = ""

            while(next_char.isdigit()):
                # continue processing word (number)
                curr_word += next_char
                next_char : str = file.read(1)

            # go back a character and process the current word (number)
            file.seek(file.tell() - 1)
            state = "got_num"

        case "in_letter":
            next_char : str = char
            curr_word = ""

            while(next_char.isalpha() or next_char.isdigit()):
                # continue processing word (key word or identifier)
                curr_word += next_char
                next_char : str = file.read(1)

            # go back a character and process the current word (key word or identifier)
            file.seek(file.tell() - 1)
            state = "got_word"

        # cases when the current word is a token
        case "got_lt":
            token_list.append(Token("relop", "lt"))
            state = "start"
        case "got_leq":
            token_list.append(Token("relop", "leq"))
            state = "start"
        case "got_gt":
            token_list.append(Token("relop", "gt"))
            state = "start"
        case "got_geq":
            token_list.append(Token("relop", "geq"))
            state = "start"
        case "got_eq":
            token_list.append(Token("relop", "eq"))
            state = "start"
        case "got_neq":
            token_list.append(Token("relop", "neq"))
            state = "start"
        case "got_plus":
            token_list.append(Token("arithop", "plus"))
            state = "start"
        case "got_minus":
            token_list.append(Token("arithop", "minus"))
            state = "start"
        case "got_mult":
            token_list.append(Token("arithop", "mult"))
            state = "start"
        case "got_asign":
            token_list.append(Token("asign"))
            state = "start"
        case "got_semicolon":
            token_list.append(Token("semicolon"))
            state = "start"
        case "got_comma":
            token_list.append(Token("comma"))
            state = "start"
        case "got_colon":
            token_list.append(Token("colon"))
            state = "start"
        case "got_dot":
            token_list.append(Token("dot"))
            state = "start"
        case "got_lpar":
            token_list.append(Token("lpar"))
            state = "start"
        case "got_rpar":
            token_list.append(Token("rpar"))
            state = "start"
        case "got_num":
            # verify symbol table pointer of current word
            if(curr_word not in symbol_table):
                symbol_table.append(curr_word)
            
            token_list.append(Token(curr_word, str(symbol_table.index(curr_word))))
            state = "start"
            
        case "got_word":
            if(curr_word.lower() in key_words):
                # current word is a key word
                token_list.append(key_words[curr_word.lower()])
            else:
                # current word is a identifier, verify symbol table pointer
                if(curr_word not in symbol_table):
                    symbol_table.append(curr_word)
            
                token_list.append(Token(curr_word, str(symbol_table.index(curr_word))))
            state = "start"

output_file = open("result.out", "w")

for token in token_list:
    output_file.write(token.toString())
    output_file.write("\n")

print("Pascal program processed successfully!")
print("See all tokens in result.out")

file.close()
output_file.close()