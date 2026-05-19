from lexical_analyzer import Token, LexicalAnalyzer
from typing import List
import sys

class SyntacticAnalyzer:
    parse_tree = []
    curr_token : Token | None = None
    lexical_analyzer : LexicalAnalyzer | None = None

    def __init__(self, input_file : str):
        self.lexical_analyzer = LexicalAnalyzer(input_file)

    def main(self):
        self.curr_token = self.lexical_analyzer.next_token()
        self.__program()

    def __syntax_error(self):
        print("Error: syntactic error")
        sys.exit(1)

    # MATCH

    def __match_terminal(self, terminal: str):
        print(f"Expected: {terminal} Current: {self.curr_token.toString()}")

        if (self.curr_token.equals(terminal)):
            self.curr_token = self.lexical_analyzer.next_token()
        else:
            self.__syntax_error()

    # PROGRAM

    def __program(self):
        self.__match_terminal("program")
        self.__match_terminal("id")
        self.__match_terminal(";")
        self.__block()
        self.__match_terminal(".")

    def __block(self):
        self.__variable_declaration_part_opt()
        self.__subroutine_declaration_part_opt()
        self.__compound_statement()

    # DECLARATIONS

    def __variable_declaration_part_opt(self):
        if (self.curr_token.equals("var")):
            self.__variable_declaration_part()

    def __subroutine_declaration_part_opt(self):
        if (self.curr_token.equals("procedure") or self.curr_token.equals("function")):
            self.__subroutine_declaration_part()

    def __variable_declaration_part(self):
        self.__match_terminal("var")
        self.__variable_declaration()
        self.__match_terminal(";")
        self.__variable_declaration_rep()

    def __variable_declaration_rep(self):
        if (self.curr_token.equals("id")):
            self.__variable_declaration()
            self.__match_terminal(";")
            self.__variable_declaration_rep()

    def __variable_declaration(self):
        self.__identifiers_list()
        self.__match_terminal(":")
        self.__type()

    def __identifiers_list(self):
        self.__match_terminal("id")
        self.__identifiers_list_rep()

    def __identifiers_list_rep(self):
        if (self.curr_token.equals(",")):
            self.__match_terminal(",")
            self.__match_terminal("id")
            self.__identifiers_list_rep()

    def __type(self):
        if (self.curr_token.equals("integer")):
            self.__match_terminal("integer")
        elif (self.curr_token.equals("boolean")):
            self.__match_terminal("boolean")
        else:
            self.__syntax_error()

    def __subroutine_declaration_part(self):
        if (self.curr_token.equals("procedure")):
            self.__procedure_declaration()
            self.__match_terminal(";")
            self.__subroutine_declaration_part()
        elif (self.curr_token.equals("function")):
            self.__function_declaration()
            self.__match_terminal(";")
            self.__subroutine_declaration_part()

    def __procedure_declaration(self):
        self.__match_terminal("procedure")
        self.__match_terminal("id")
        self.__formal_parameters_opt()
        self.__match_terminal(";")
        self.__block()

    def __function_declaration(self):
        self.__match_terminal("function")
        self.__match_terminal("id")
        self.__formal_parameters_opt()
        self.__match_terminal(":")
        self.__type()
        self.__match_terminal(";")
        self.__block()

    def __formal_parameters_opt(self):
        if (self.curr_token.equals("(")):
            self.__formal_parameters()

    def __formal_parameters(self):
        self.__match_terminal("(")
        self.__formal_parameter_section()
        self.__formal_parameters_rep()
        self.__match_terminal(")")

    def __formal_parameters_rep(self):
        if (self.curr_token.equals(";")):
            self.__match_terminal(";")
            self.__formal_parameter_section()
            self.__formal_parameters_rep()

    def __formal_parameter_section(self):
        self.__identifiers_list()
        self.__match_terminal(":")
        self.__type()

    # STATEMENTS

    def __compound_statement(self):
        self.__match_terminal("begin")
        self.__statement()
        self.__compound_statement_rep()
        self.__match_terminal("end")

    def __compound_statement_rep(self):
        if (self.curr_token.equals(";")):
            self.__match_terminal(";")
            self.__statement()
            self.__compound_statement_rep()

    def __statement(self):
        if (self.curr_token.equals("id")):
            self.__match_terminal("id")
            self.__statement_id()
        elif (self.curr_token.equals("begin")):
            self.__compound_statement()
        elif (self.curr_token.equals("if")):
            self.__conditional_statement()
        elif (self.curr_token.equals("while")):
            self.__repetitive_statement()
        elif (self.curr_token.equals("read")):
            self.__read_statement()
        elif (self.curr_token.equals("write")):
            self.__write_statement()
        else:
            self.__syntax_error()

    def __statement_id(self):
        if (self.curr_token.equals(":=")):
            self.__assignment_without_id()
        else:
            self.__procedure_call_without_id()

    def __assignment_without_id(self):
        self.__match_terminal(":=")
        self.__expression()

    def __procedure_call_without_id(self):
        if (self.curr_token.equals("(")):
            self.__match_terminal("(")
            self.__expression_list()
            self.__match_terminal(")")

    def __conditional_statement(self):
        self.__match_terminal("if")
        self.__match_terminal("(")
        self.__expression()
        self.__match_terminal(")")
        self.__match_terminal("then")
        self.__statement()
        self.__else_opt()

    def __else_opt(self):
        if (self.curr_token.equals("else")):
            self.__match_terminal("else")
            self.__statement()

    def __repetitive_statement(self):
        self.__match_terminal("while")
        self.__match_terminal("(")
        self.__expression()
        self.__match_terminal(")")
        self.__match_terminal("do")
        self.__statement()

    def __read_statement(self):
        self.__match_terminal("read")
        self.__match_terminal("(")
        self.__variable()
        self.__match_terminal(")")

    def __write_statement(self):
        self.__match_terminal("write")
        self.__match_terminal("(")
        self.__expression()
        self.__match_terminal(")")

    # EXPRESSIONS

    def __expression_list(self):
        self.__expression()
        self.__expression_list_rep()

    def __expression_list_rep(self):
        if (self.curr_token.equals(",")):
            self.__match_terminal(",")
            self.__expression()
            self.__expression_list_rep()

    def __expression(self):
        self.__simple_expression()
        self.__expression_rep()

    def __expression_rep(self):
        if (self.curr_token.equals("=") or self.curr_token.equals("<>") or self.curr_token.equals("<")
            or self.curr_token.equals("<=") or self.curr_token.equals(">") or self.curr_token.equals(">=")):
            self.__relation()
            self.__simple_expression()
            self.__expression_rep()

    def __relation(self):
        if (self.curr_token.equals("=")):
            self.__match_terminal("=")
        elif (self.curr_token.equals("<>")):
            self.__match_terminal("<>")
        elif (self.curr_token.equals("<")):
            self.__match_terminal("<")
        elif (self.curr_token.equals("<=")):
            self.__match_terminal("<=")
        elif (self.curr_token.equals(">")):
            self.__match_terminal(">")
        elif (self.curr_token.equals(">=")):
            self.__match_terminal(">=")
        else:
            self.__syntax_error()

    def __simple_expression(self):
        self.__unary_operator_opt()
        self.__term()
        self.__simple_expression_rep()

    def __simple_expression_rep(self):
        if (self.curr_token.equals("+") or self.curr_token.equals("-") or self.curr_token.equals("or")):
            self.__expression_operator()
            self.__term()
            self.__simple_expression_rep()

    def __unary_operator_opt(self):
        if (self.curr_token.equals("+")):
            self.__match_terminal("+")
        elif (self.curr_token.equals("-")):
            self.__match_terminal("-")

    def __expression_operator(self):
        if (self.curr_token.equals("+")):
            self.__match_terminal("+")
        elif (self.curr_token.equals("-")):
            self.__match_terminal("-")
        elif (self.curr_token.equals("or")):
            self.__match_terminal("or")
        else:
            self.__syntax_error()

    def __term(self):
        self.__factor()
        self.__term_rep()

    def __term_rep(self):
        if (self.curr_token.equals("*") or self.curr_token.equals("div") or self.curr_token.equals("and")):
            self.__term_operator()
            self.__factor()
            self.__term_rep()

    def __term_operator(self):
        if (self.curr_token.equals("*")):
            self.__match_terminal("*")
        elif (self.curr_token.equals("div")):
            self.__match_terminal("div")
        elif (self.curr_token.equals("and")):
            self.__match_terminal("and")
        else:
            self.__syntax_error()

    def __factor(self):
        if (self.curr_token.equals("id")):
            self.__match_terminal("id")
            self.__function_call_without_id()
        elif (self.curr_token.equals("num")):
            self.__match_terminal("num")
        elif (self.curr_token.equals("(")):
            self.__match_terminal("(")
            self.__expression()
            self.__match_terminal(")")
        elif (self.curr_token.equals("not")):
            self.__match_terminal("not")
            self.__factor()
        elif (self.curr_token.equals("true") or self.curr_token.equals("false")):
            self.__language_constant()
        else:
            self.__syntax_error()

    def __variable(self):
        self.__match_terminal("id")

    def __function_call_without_id(self):
        if (self.curr_token.equals("(")):
            self.__match_terminal("(")
            self.__expression_list()
            self.__match_terminal(")")

    def __language_constant(self):
        if (self.curr_token.equals("true")):
            self.__match_terminal("true")
        elif (self.curr_token.equals("false")):
            self.__match_terminal("false")
        else:
            self.__syntax_error()


# parameter: name of the input file
if(len(sys.argv) < 2):
    print("Error: it is required the name of the input file as parameter")
    sys.exit(1)

# pascal file recived
input_file : str = sys.argv[1]

sa = SyntacticAnalyzer(input_file)
sa.main()