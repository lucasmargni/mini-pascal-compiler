from lexical_analyzer import Token, LexicalAnalyzer
from symbol_table import SymbolTable, Symbol
from typing import Optional
import sys

class IntermediateCodeGenerator:
    curr_token : Optional[Token]
    lexical_analyzer : Optional[LexicalAnalyzer]
    curr_symbol_table : SymbolTable
    code: list[str] # mepa instr list
    label_count: int
    curr_level: int
    next_offset: int

    def __init__(self, input_file : str):
        self.lexical_analyzer = LexicalAnalyzer(input_file)
        self.curr_symbol_table = SymbolTable()

        self.code = []
        self.label_count = 0
        self.curr_level = 0
        self.next_offset = 0

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

    def write_output(self, output_file: str):
        with open(output_file, "w") as file:
            file.write("\n".join(self.code) + "\n")

    def __new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def __emit(self, instruction: str, label: Optional[str] = None):
        self.code.append(f"{label or '':<6}{instruction}")

    def __set_params_addresses(self, params: list[Symbol]):
        n = len(params)

        for i, param in enumerate(params, start=1):
            param.level = self.curr_level
            param.offset = -(n + 3 - i)
        
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

    def __non_procedure_error(self, found : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: procedure expected but '{found}' found (row {row}, col {col})")
        sys.exit(1)
        
    def __non_function_error(self, found : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: function expected but '{found}' found (row {row}, col {col})")
        sys.exit(1)
        
    def __non_return_symbol_error(self, found : str):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: variable or function expected but '{found}' found (row {row}, col {col})")
        sys.exit(1)

    def __too_many_parameters_error(self):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: too much parameters found (row {row}, col {col})")
        sys.exit(1)

    def __not_enough_parameters_error(self):
        (row, col) = self.lexical_analyzer.get_position()
        print(f"Semantic Error: not enough parameters found (row {row}, col {col})")
        sys.exit(1)

    # MATCH

    def __match_terminal(self, terminal: str) -> Optional[str | int]:
        '''returns the lexeme if and only if the terminal match with a identifier or number'''
        lexeme = None

        if (self.curr_token.equals(terminal)):
            if (terminal == "id" or terminal == "num"):
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
        self.__emit("INPP")
        self.__block()
        self.__emit("PARA")
        self.__match_terminal(".")

    def __block(self):
        self.next_offset = 0

        num_vars = self.__variable_declaration_part_opt()
        if (num_vars > 0):
            self.__emit(f"RMEM {num_vars}")

        skip_label = None
        if (self.curr_token.equals("procedure") or self.curr_token.equals("function")):
            skip_label = self.__new_label()
            self.__emit(f"DSVS {skip_label}")

        self.__subroutine_declaration_part_opt()

        if (skip_label):
            self.__emit("NADA", skip_label)

        self.__compound_statement()

        if (num_vars > 0):
            self.__emit(f"LMEM {num_vars}")

    # DECLARATIONS

    def __variable_declaration_part_opt(self) -> int:
        count_vars = 0

        if (self.curr_token.equals("var")):
            count_vars = self.__variable_declaration_part()

        return count_vars

    def __subroutine_declaration_part_opt(self):
        if (self.curr_token.equals("procedure") or self.curr_token.equals("function")):
            self.__subroutine_declaration_part()

    def __variable_declaration_part(self):
        self.__match_terminal("var")
        count_vars = self.__variable_declaration()
        self.__match_terminal(";")
        count_vars += self.__variable_declaration_rep()

        return count_vars

    def __variable_declaration_rep(self):
        count_vars = 0

        if (self.curr_token.equals("id")):
            count_vars = self.__variable_declaration()
            self.__match_terminal(";")
            count_vars += self.__variable_declaration_rep()

        return count_vars

    def __variable_declaration(self):
        list_ids = self.__identifiers_list()
        self.__match_terminal(":")
        name_type = self.__type()

        for id in list_ids:
            if(self.curr_symbol_table.exists_symbol(id)):
                '''variable already declared'''
                self.__uniqueness_error(id)

            var_symbol = Symbol(id, "var", name_type)
            var_symbol.level = self.curr_level
            var_symbol.offset = self.next_offset
            self.next_offset += 1
            self.curr_symbol_table.add_symbol(var_symbol)


        return len(list_ids)

    def __identifiers_list(self) -> list[str]:
        '''returns the list of lexemes of all identifiers'''
        lexeme = self.__match_terminal("id")
        list_rep_ids = self.__identifiers_list_rep()

        list_ids = [lexeme] + list_rep_ids

        return list_ids

    def __identifiers_list_rep(self) -> list[str]:
        '''returns the list of lexemes of all identifiers'''
        list_ids = []

        if (self.curr_token.equals(",")):
            self.__match_terminal(",")
            lexeme = self.__match_terminal("id")
            list_rep_ids = self.__identifiers_list_rep()

            list_ids = [lexeme] + list_rep_ids

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

        label = self.__new_label()

        # procedure has a new environment, create a new symbol table
        new_symbol_table = SymbolTable(self.curr_symbol_table)
        self.curr_symbol_table = new_symbol_table

        self.curr_level += 1

        params = self.__formal_parameters_opt()
        self.__match_terminal(";")

        self.__set_params_addresses(params)

        proc_symbol = Symbol(lexeme, "procedure")
        proc_symbol.set_param_types([p.data_type for p in params])

        proc_symbol.label = label
        proc_symbol.num_params = len(params)
        self.curr_symbol_table.add_symbol(proc_symbol)

        self.__emit(f"ENPR {self.curr_level}", label)

        self.__block()

        self.__emit(f"RTPR {self.curr_level},{len(params)}")

        # end of new environment, delete it and add the procedure to previous table
        self.curr_level -= 1
        self.curr_symbol_table = self.curr_symbol_table.prev
        self.curr_symbol_table.add_symbol(proc_symbol)

    def __function_declaration(self):
        self.__match_terminal("function")
        lexeme = self.__match_terminal("id")
        
        if (self.curr_symbol_table.exists_symbol(lexeme)):
            self.__uniqueness_error(lexeme)

        label = self.__new_label()

        # function has a new environment, create a new symbol table
        new_symbol_table = SymbolTable(self.curr_symbol_table)
        self.curr_symbol_table = new_symbol_table
        self.curr_level += 1

        params = self.__formal_parameters_opt()
        self.__match_terminal(":")
        name_type = self.__type()
        self.__match_terminal(";")

        # params addresses can only be set once the total number of params is known
        self.__set_params_addresses(params)

        num_params = len(params)
        param_types = [param.data_type for param in params]

        # inner symbol: the function name can be assigned to set the return value
        funct_symbol = Symbol(lexeme, "function", name_type, can_be_assigned=True)
        funct_symbol.set_param_types(param_types)
        funct_symbol.label = label
        funct_symbol.num_params = num_params
        funct_symbol.level = self.curr_level
        funct_symbol.offset = -(num_params + 3)
        self.curr_symbol_table.add_symbol(funct_symbol)
        
        self.__emit(f"ENPR {self.curr_level}", label)

        self.__block()

        self.__emit(f"RTPR {self.curr_level},{num_params}")

        # end of new environment, delete it and add the function to previous table
        self.curr_level -= 1
        self.curr_symbol_table = self.curr_symbol_table.prev

        # outer symbol: the function can only be called
        funct_symbol2 = Symbol(lexeme, "function", name_type)
        funct_symbol2.set_param_types(param_types)
        funct_symbol2.label = label
        funct_symbol2.num_params = num_params
        self.curr_symbol_table.add_symbol(funct_symbol2)

    def __formal_parameters_opt(self) -> list[Symbol]:
        params = []

        if (self.curr_token.equals("(")):
            params = self.__formal_parameters()
        
        return params

    def __formal_parameters(self) -> list[Symbol]:
        self.__match_terminal("(")
        params = self.__formal_parameter_section()
        params2 = self.__formal_parameters_rep()
        self.__match_terminal(")")

        return params + params2

    def __formal_parameters_rep(self) -> list[Symbol]:
        if (self.curr_token.equals(";")):
            self.__match_terminal(";")
            params = self.__formal_parameter_section()
            params2 = self.__formal_parameters_rep()

            return params + params2
        
        return []

    def __formal_parameter_section(self) -> list[Symbol]:
        params = []

        list_ids = self.__identifiers_list()
        self.__match_terminal(":")
        name_type = self.__type()

        for id in list_ids:
            if(self.curr_symbol_table.exists_symbol(id)):
                '''variable already declared'''
                self.__uniqueness_error(id)
        
            param_symbol = Symbol(id, "var", name_type)
            self.curr_symbol_table.add_symbol(param_symbol)
            params.append(param_symbol)

        return params

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
        curr_id = self.curr_symbol_table.get_symbol(lexeme)

        if (not curr_id):
            self.__undeclared_variable_error(lexeme)

        if (self.curr_token.equals(":=")):
            # check if the id is a variable or a function that can be assigned
            if (not curr_id.can_be_assigned):
                self.__non_assignable_id_error(lexeme)

            self.__assignment_without_id(lexeme)
        else:
            # check if the id is a procedure
            if(curr_id.symbol_type != "procedure"):
                self.__non_procedure_error(lexeme)
            
            self.__procedure_call_without_id(curr_id)

    def __assignment_without_id(self, lexeme: str):
        self.__match_terminal(":=")
        expression_type = self.__expression()

        symbol = self.curr_symbol_table.get_symbol(lexeme)
        lexeme_type = symbol.data_type

        # check if id and the right side are of the same type
        if (expression_type != lexeme_type):
            self.__type_error(expression_type, lexeme_type)

        self.__emit(f"ALVL {symbol.level},{symbol.offset}")

    def __procedure_call_without_id(self, curr_id: Symbol):
        if (self.curr_token.equals("(")):
            self.__match_terminal("(")
            self.__expression_list(curr_id.param_types)
            self.__match_terminal(")")
        elif (len(curr_id.param_types) > 0):
            self.__not_enough_parameters_error()

        self.__emit(f"LLPR {curr_id.label}")

    def __conditional_statement(self):
        self.__match_terminal("if")
        self.__match_terminal("(")
        expression_type = self.__expression()

        if (expression_type != "boolean"):
            self.__type_error(expression_type, "boolean")

        self.__match_terminal(")")
        self.__match_terminal("then")

        else_label = self.__new_label()
        self.__emit(f"DSVF {else_label}")

        self.__statement()
        self.__else_opt(else_label)

    def __else_opt(self, else_label: str):
        if (self.curr_token.equals("else")):
            end_label = self.__new_label()
            self.__emit(f"DSVS {end_label}")
            self.__emit("NADA", else_label)

            self.__match_terminal("else")
            self.__statement()

            self.__emit("NADA", end_label)
        else:
            self.__emit("NADA", else_label)

    def __repetitive_statement(self):
        start_label = self.__new_label()
        end_label = self.__new_label()

        self.__emit("NADA", start_label)

        self.__match_terminal("while")
        self.__match_terminal("(")
        expression_type = self.__expression()

        if (expression_type != "boolean"):
            self.__type_error(expression_type, "boolean")

        self.__match_terminal(")")
        self.__match_terminal("do")

        self.__emit(f"DSVF {end_label}")

        self.__statement()

        self.__emit(f"DSVS {start_label}")
        self.__emit("NADA", end_label)

    def __read_statement(self):
        self.__match_terminal("read")
        self.__match_terminal("(")
        symbol = self.__variable()

        self.__emit("LEER")
        self.__emit(f"ALVL {symbol.level},{symbol.offset}")

        self.__match_terminal(")")

    def __write_statement(self):
        self.__match_terminal("write")
        self.__match_terminal("(")
        self.__expression()

        self.__emit("IMPR")

        self.__match_terminal(")")

    # EXPRESSIONS

    def __expression_list(self, param_types: list[str]):
        name_type = self.__expression()
        count = 0

        if (count >= len(param_types)):
            self.__too_many_parameters_error()
        elif (name_type != param_types[count]):
            self.__type_error(name_type, param_types[count])

        self.__expression_list_rep(count+1, param_types)

    def __expression_list_rep(self, count: int, param_types: list[str]):
        if (self.curr_token.equals(",")):
            self.__match_terminal(",")
            name_type = self.__expression()
            
            if (count >= len(param_types)):
                self.__too_many_parameters_error()
            elif (name_type != param_types[count]):
                self.__type_error(name_type, param_types[count])
            
            self.__expression_list_rep(count+1, param_types)
        else:
            # check if there are more parameters expected
            if (count < len(param_types)):
                self.__not_enough_parameters_error()

    def __expression(self) -> str:
        name_type = self.__simple_expression()
        return_type = self.__expression_opt(name_type)

        return return_type

    def __expression_opt(self, name_type: str) -> str:
        return_type = name_type

        if (self.curr_token.equals("=") or self.curr_token.equals("<>") or self.curr_token.equals("<")
            or self.curr_token.equals("<=") or self.curr_token.equals(">") or self.curr_token.equals(">=")):
            instruction = self.__relation()
            second_name_type = self.__simple_expression()

            if(name_type != "integer"):
                self.__type_error(name_type, "integer")
            elif(second_name_type != "integer"):
                self.__type_error(second_name_type, "integer")

            self.__emit(instruction)
            return_type = "boolean"

        return return_type

    def __relation(self) -> str:
        if (self.curr_token.equals("=")):
            self.__match_terminal("=")
            instruction = "CMIG"
        elif (self.curr_token.equals("<>")):
            self.__match_terminal("<>")
            instruction = "CMDG"
        elif (self.curr_token.equals("<")):
            self.__match_terminal("<")
            instruction = "CMME"
        elif (self.curr_token.equals("<=")):
            self.__match_terminal("<=")
            instruction = "CMNI"
        elif (self.curr_token.equals(">")):
            self.__match_terminal(">")
            instruction = "CMMA"
        elif (self.curr_token.equals(">=")):
            self.__match_terminal(">=")
            instruction = "CMYI"
        else:
            self.__syntax_error("a relation operator")

        return instruction

    def __simple_expression(self) -> str:
        sign = self.__unary_operator_opt()
        name_type = self.__term()

        if (sign and name_type != "integer"):
            self.__type_error(name_type, "integer")

        if (sign == "-"):
            self.__emit("UMEN")

        self.__simple_expression_rep(name_type)

        return name_type

    def __simple_expression_rep(self, name_type: str):
        if (self.curr_token.equals("+") or self.curr_token.equals("-") or self.curr_token.equals("or")):
            op_type, instruction = self.__expression_operator()
            second_name_type = self.__term()

            if(name_type != op_type):
                self.__type_error(name_type, op_type)
            elif(op_type != second_name_type):
                self.__type_error(second_name_type, op_type)

            self.__emit(instruction)
            self.__simple_expression_rep(name_type)

    def __unary_operator_opt(self) -> Optional[str]:
        sign = None

        if (self.curr_token.equals("+")):
            self.__match_terminal("+")
            sign = "+"
        elif (self.curr_token.equals("-")):
            self.__match_terminal("-")
            sign = "-"

        return sign

    def __expression_operator(self) -> tuple[str, str]:
        if (self.curr_token.equals("+")):
            self.__match_terminal("+")
            op_type = "integer"
            instruction = "SUMA"
        elif (self.curr_token.equals("-")):
            self.__match_terminal("-")
            op_type = "integer"
            instruction = "SUST"
        elif (self.curr_token.equals("or")):
            self.__match_terminal("or")
            op_type = "boolean"
            instruction = "DISJ"
        else:
            self.__syntax_error("an expression operator")

        return op_type, instruction

    def __term(self) -> str:
        name_type = self.__factor()
        self.__term_rep(name_type)

        return name_type

    def __term_rep(self, name_type: str):
        if (self.curr_token.equals("*") or self.curr_token.equals("div") or self.curr_token.equals("and")):
            op_type, instructions = self.__term_operator()
            second_name_type = self.__factor()

            if (name_type != op_type):
                self.__type_error(name_type, op_type)
            elif (op_type != second_name_type):
                self.__type_error(second_name_type, op_type)

            for instr in instructions:
                self.__emit(instr)

            self.__term_rep(name_type)

    def __term_operator(self) -> tuple[str, list[str]]:
        if (self.curr_token.equals("*")):
            self.__match_terminal("*")
            op_type = "integer"
            instructions = ["MULT"]
        elif (self.curr_token.equals("div")):
            self.__match_terminal("div")
            op_type = "integer"
            instructions = ["DIVC", "DIVI"]
        elif (self.curr_token.equals("and")):
            self.__match_terminal("and")
            op_type = "boolean"
            instructions = ["CONJ"]
        else:
            self.__syntax_error("a term operator")

        return op_type, instructions

    def __factor(self) -> str:
        if (self.curr_token.equals("id")):
            lexeme = self.__match_terminal("id")
            curr_id = self.curr_symbol_table.get_symbol(lexeme)

            if (not curr_id):
                self.__undeclared_variable_error(lexeme)
            elif (curr_id.symbol_type not in ["var", "function"]):
                self.__non_return_symbol_error(lexeme)

            if (curr_id.symbol_type == "function"):
                self.__emit("RMEM 1")

            self.__function_call_without_id(curr_id, lexeme)

            if (curr_id.symbol_type == "function"):
                self.__emit(f"LLPR {curr_id.label}")
            else: # = "var"
                self.__emit(f"APVL {curr_id.level},{curr_id.offset}")

            name_type = curr_id.data_type
        elif (self.curr_token.equals("num")):
            value = self.__match_terminal("num")
            self.__emit(f"APCT {value}")

            name_type = "integer"
        elif (self.curr_token.equals("(")):
            self.__match_terminal("(")
            name_type = self.__expression()
            self.__match_terminal(")")
        elif (self.curr_token.equals("not")):
            self.__match_terminal("not")
            name_type = self.__factor()
            self.__emit("NEGA")

            if(name_type != "boolean"):
                self.__type_error(name_type, "boolean")

        elif (self.curr_token.equals("true") or self.curr_token.equals("false")):
            self.__language_constant()
            name_type = "boolean"
        else:
            self.__syntax_error("a factor")

        return name_type

    def __variable(self) -> Symbol:
        lexeme = self.__match_terminal("id")

        curr_sy = self.curr_symbol_table.get_symbol(lexeme)

        if (not curr_sy):
            self.__undeclared_variable_error(lexeme)
        elif (not curr_sy.can_be_assigned):
            self.__non_assignable_id_error(lexeme)

        return curr_sy

    def __function_call_without_id(self, curr_id: Symbol, lexeme: str):
        if (self.curr_token.equals("(")):

            if (curr_id.symbol_type != "function"):
                self.__non_function_error(lexeme)

            self.__match_terminal("(")
            self.__expression_list(curr_id.param_types)
            self.__match_terminal(")")
        elif (curr_id.symbol_type == "function" and len(curr_id.param_types) > 0):
            self.__not_enough_parameters_error()

    def __language_constant(self):
        if (self.curr_token.equals("true")):
            self.__match_terminal("true")
            self.__emit("APCT 1")
        elif (self.curr_token.equals("false")):
            self.__match_terminal("false")
            self.__emit("APCT 0")
        else:
            self.__syntax_error("a language constant")