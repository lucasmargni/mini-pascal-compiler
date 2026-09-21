from lexical_analyzer import Token, LexicalAnalyzer
from symbol_table import SymbolTable, Symbol
from typing import Optional
import sys

class SyntacticSemanticAnalyzer:
    curr_token : Optional[Token] = None
    lexical_analyzer : Optional[LexicalAnalyzer] = None
    curr_symbol_table : SymbolTable = SymbolTable()

    def __init__(self, input_file : str):
        self.lexical_analyzer = LexicalAnalyzer(input_file)

    def main(self):
        self.curr_token = self.lexical_analyzer.next_token()

        if (self.curr_token == None):
            # file has no tokens
            self.__syntax_error("program")

        self.__program()

        # there are more tokens, but grammar ended
        if (self.curr_token != None):
            (row, col) = self.lexical_analyzer.get_position()
            print(f"Syntactic Error: program ended but more tokens found (row {row}, col {col})")
            sys.exit(1)

    # ERRORS

    def __syntax_error(self, expected : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Syntactic Error: expected '{expected}' but '{self.curr_token.toTerminal()}' found (row {row}, col {col})")
        sys.exit(1)

    def __uniqueness_error(self, var : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: the variable '{var}' was already declared (row {row}, col {col})")
        sys.exit(1)

    def __undeclared_variable_error(self, var : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: the variable '{var}' was not declared (row {row}, col {col})")
        sys.exit(1)

    def __non_assignable_id_error(self, var : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: the variable '{var}' cannot be assigned (row {row}, col {col})")
        sys.exit(1)

    def __type_error(self, type_found : str, type_expected : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: type expected '{type_expected}' type '{type_found}' found (row {row}, col {col})")
        sys.exit(1)

    # MATCH

    def __match_terminal(self, terminal: str) -> Optional[str]:
        '''returns the lexeme if and only if the terminal match with a identifier'''
        lexeme = None

        if (self.curr_token.equals(terminal)):
            if (terminal == "id"):
                lexeme = self.curr_token.atribute

            self.curr_token = self.lexical_analyzer.next_token()

            if (self.curr_token == None and terminal != "."):
                # no more tokens found and program not ended
                (row, col) = self.lexical_analyzer.get_position()
                print(f"Syntactic Error: invalid end of program (row {row}, col {col})")
                sys.exit(1)
        else:
            # invalid token
            self.__syntax_error(terminal)

        return lexeme

    # PROGRAM

    def __program(self):
        self.__match_terminal("program")
        lexeme = self.__match_terminal("id")

        # add name of program to the symbol table
        self.curr_symbol_table.add_symbol(Symbol(lexeme, "program"))

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
        list_ids = self.__identifiers_list()
        self.__match_terminal(":")
        name_type = self.__type()

        for id in list_ids:
            if(self.curr_symbol_table.exists_symbol(id)):
                '''variable already declared'''
                self.__uniqueness_error(id)

            self.curr_symbol_table.add_symbol(Symbol(id, "var", name_type))

    def __identifiers_list(self) -> list[str]:
        '''returns the list of lexemes of all identifiers'''
        lexeme = self.__match_terminal("id")
        list_ids = self.__identifiers_list_rep()

        list_ids.append(lexeme)

        return list_ids

    def __identifiers_list_rep(self) -> list[str]:
        '''returns the list of lexemes of all identifiers'''
        list_ids = []

        if (self.curr_token.equals(",")):
            self.__match_terminal(",")
            lexeme = self.__match_terminal("id")
            list_ids = self.__identifiers_list_rep()

            list_ids.append(lexeme)

        return list_ids

    def __type(self) -> str:
        '''returns the name of current type as string'''
        name_type = ""

        if (self.curr_token.equals("integer")):
            self.__match_terminal("integer")
            name_type = "integer"
        elif (self.curr_token.equals("boolean")):
            self.__match_terminal("boolean")
            name_type = "boolean"
        else:
            self.__syntax_error("a type")

        return name_type

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
        lexeme = self.__match_terminal("id")

        if (self.curr_symbol_table.exists_symbol(lexeme)):
            self.__uniqueness_error(lexeme)

        # procedure has a new environment, create a new symbol table
        new_symbol_table = SymbolTable(self.curr_symbol_table)
        self.curr_symbol_table = new_symbol_table

        self.__formal_parameters_opt()
        self.__match_terminal(";")

        curr_procedure = Symbol(lexeme, "procedure")
        self.curr_symbol_table.add_symbol(curr_procedure)

        self.__block()

        # end of new environment, delete it and add the procedure to previous table
        self.curr_symbol_table = self.curr_symbol_table.prev
        self.curr_symbol_table.add_symbol(curr_procedure)

    def __function_declaration(self):
        self.__match_terminal("function")
        lexeme = self.__match_terminal("id")
        
        if (self.curr_symbol_table.exists_symbol(lexeme)):
            self.__uniqueness_error(lexeme)

        # function has a new environment, create a new symbol table
        new_symbol_table = SymbolTable(self.curr_symbol_table)
        self.curr_symbol_table = new_symbol_table

        self.__formal_parameters_opt()
        self.__match_terminal(":")
        name_type = self.__type()
        self.__match_terminal(";")

        self.curr_symbol_table.add_symbol(Symbol(lexeme, "function", name_type, can_be_assigned=True))
        
        self.__block()

        # end of new environment, delete it and add the function to previous table
        self.curr_symbol_table = self.curr_symbol_table.prev
        self.curr_symbol_table.add_symbol(Symbol(lexeme, "function", name_type))

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
        list_ids = self.__identifiers_list()
        self.__match_terminal(":")
        name_type = self.__type()

        for id in list_ids:
            if(self.curr_symbol_table.exists_symbol(id)):
                '''variable already declared'''
                self.__uniqueness_error(id)
        
            self.curr_symbol_table.add_symbol(Symbol(id, "var", name_type))

    # STATEMENTS

    def __compound_statement(self):
        self.__match_terminal("begin")
        self.__statement()
        self.__compound_statement_rep()
        self.__match_terminal("end")

    def __compound_statement_rep(self):
        if (self.curr_token.equals(";")):
            self.__match_terminal(";")
            self.__compound_statement_rep_opt()

    def __compound_statement_rep_opt(self):
        if (self.curr_token.equals("id") or self.curr_token.equals("begin") or self.curr_token.equals("if")
            or self.curr_token.equals("while") or self.curr_token.equals("read") or self.curr_token.equals("write")):
            self.__statement()
            self.__compound_statement_rep()

    def __statement(self):
        if (self.curr_token.equals("id")):
            lexeme = self.__match_terminal("id")
            self.__statement_id(lexeme)
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
            self.__syntax_error("a statement")

    def __statement_id(self, lexeme: str):
        if (not self.curr_symbol_table.get_symbol(lexeme)):
            self.__undeclared_variable_error(lexeme)

        if (self.curr_token.equals(":=")):
            # check if the id is a variable or a function that can be assigned
            if(not self.curr_symbol_table.get_symbol(lexeme).can_be_assigned):
                self.__non_assignable_id_error(lexeme)

            self.__assignment_without_id(lexeme)
        else:
            self.__procedure_call_without_id()

    def __assignment_without_id(self, lexeme: str):
        self.__match_terminal(":=")
        expression_type = self.__expression()

        lexeme_type = self.curr_symbol_table.get_symbol(lexeme).data_type

        if (expression_type != lexeme_type):
            self.__type_error(expression_type, lexeme_type)

    def __procedure_call_without_id(self):
        if (self.curr_token.equals("(")):
            self.__match_terminal("(")
            self.__expression_list()
            self.__match_terminal(")")

    def __conditional_statement(self):
        self.__match_terminal("if")
        self.__match_terminal("(")
        expression_type = self.__expression()

        if (expression_type != "boolean"):
            self.__type_error(expression_type, "boolean")

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
        expression_type = self.__expression()

        if (expression_type != "boolean"):
            self.__type_error(expression_type, "boolean")

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

    def __expression(self) -> str:
        name_type = self.__simple_expression()
        return_type = self.__expression_opt(name_type)

        return return_type

    def __expression_opt(self, name_type: str) -> str:
        return_type = name_type

        if (self.curr_token.equals("=") or self.curr_token.equals("<>") or self.curr_token.equals("<")
            or self.curr_token.equals("<=") or self.curr_token.equals(">") or self.curr_token.equals(">=")):
            op_type = self.__relation()
            second_name_type = self.__simple_expression()

            if(name_type != op_type):
                self.__type_error(name_type, op_type)
            elif(op_type != second_name_type):
                self.__type_error(second_name_type, op_type)

            return_type = "boolean"

        return return_type

    def __relation(self) -> str:
        if (self.curr_token.equals("=")):
            self.__match_terminal("=")
            op_type = "boolean"
        elif (self.curr_token.equals("<>")):
            self.__match_terminal("<>")
            op_type = "boolean"
        elif (self.curr_token.equals("<")):
            self.__match_terminal("<")
            op_type = "integer"
        elif (self.curr_token.equals("<=")):
            self.__match_terminal("<=")
            op_type = "integer"
        elif (self.curr_token.equals(">")):
            self.__match_terminal(">")
            op_type = "integer"
        elif (self.curr_token.equals(">=")):
            self.__match_terminal(">=")
            op_type = "integer"
        else:
            self.__syntax_error("a relation operator")

        return op_type

    def __simple_expression(self) -> str:
        found = self.__unary_operator_opt()
        name_type = self.__term()

        if(found and name_type != "integer"):
            self.__type_error(name_type, "integer")

        self.__simple_expression_rep(name_type)

        return name_type

    def __simple_expression_rep(self, name_type: str):
        if (self.curr_token.equals("+") or self.curr_token.equals("-") or self.curr_token.equals("or")):
            op_type = self.__expression_operator()
            second_name_type = self.__term()

            if(name_type != op_type):
                self.__type_error(name_type, op_type)
            elif(op_type != second_name_type):
                self.__type_error(second_name_type, op_type)

            self.__simple_expression_rep(name_type)

    def __unary_operator_opt(self) -> bool:
        found = False

        if (self.curr_token.equals("+")):
            self.__match_terminal("+")
            found = True
        elif (self.curr_token.equals("-")):
            self.__match_terminal("-")
            found = True

        return found

    def __expression_operator(self) -> str:
        if (self.curr_token.equals("+")):
            self.__match_terminal("+")
            op_type = "integer"
        elif (self.curr_token.equals("-")):
            self.__match_terminal("-")
            op_type = "integer"
        elif (self.curr_token.equals("or")):
            self.__match_terminal("or")
            op_type = "boolean"
        else:
            self.__syntax_error("an expression operator")

        return op_type

    def __term(self) -> str:
        name_type = self.__factor()
        self.__term_rep(name_type)

        return name_type

    def __term_rep(self, name_type: str):
        if (self.curr_token.equals("*") or self.curr_token.equals("div") or self.curr_token.equals("and")):
            op_type = self.__term_operator()
            second_name_type = self.__factor()

            if(name_type != op_type):
                self.__type_error(name_type, op_type)
            elif(op_type != second_name_type):
                self.__type_error(second_name_type, op_type)

            self.__term_rep(name_type)

    def __term_operator(self) -> str:
        if (self.curr_token.equals("*")):
            self.__match_terminal("*")
            op_type = "integer"
        elif (self.curr_token.equals("div")):
            self.__match_terminal("div")
            op_type = "integer"
        elif (self.curr_token.equals("and")):
            self.__match_terminal("and")
            op_type = "boolean"
        else:
            self.__syntax_error("a term operator")

        return op_type

    def __factor(self) -> str:
        if (self.curr_token.equals("id")):
            lexeme = self.__match_terminal("id")
            if(not self.curr_symbol_table.get_symbol(lexeme)):
                self.__undeclared_variable_error(lexeme)

            self.__function_call_without_id()

            name_type = self.curr_symbol_table.get_symbol(lexeme).data_type
        elif (self.curr_token.equals("num")):
            self.__match_terminal("num")

            name_type = "integer"
        elif (self.curr_token.equals("(")):
            self.__match_terminal("(")
            name_type = self.__expression()
            self.__match_terminal(")")
        elif (self.curr_token.equals("not")):
            self.__match_terminal("not")
            name_type = self.__factor()

            if(name_type != "boolean"):
                self.__type_error(name_type, "boolean")

        elif (self.curr_token.equals("true") or self.curr_token.equals("false")):
            self.__language_constant()
            name_type = "boolean"
        else:
            self.__syntax_error("a factor")

        return name_type

    def __variable(self):
        lexeme = self.__match_terminal("id")

        curr_sy = self.curr_symbol_table.get_symbol(lexeme)

        if (not curr_sy):
            self.__undeclared_variable_error(lexeme)
        elif (not curr_sy.can_be_assigned):
            self.__non_assignable_id_error(lexeme)

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
            self.__syntax_error("a language constant")