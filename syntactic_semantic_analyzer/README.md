# Syntactic Semantic Analyzer

The **Syntactic Semantic Analyzer** is the third stage of the Mini Pascal Compiler. Its main responsibility is to verify, in a single pass, that the source program conforms to the grammar of the language and that it respects the semantic rules of declarations and types.

## Overview

This component extends the syntactic analyzer by adding semantic actions to the parsing process. While the tokens are being consumed and the grammar is being validated, the analyzer also checks that the program makes sense according to the rules of the language.

The analyzer validates, in a general way:

- Uniqueness of identifiers within the same scope
- Declaration of every identifier before its use
- Type compatibility in assignments, expressions and conditions
- Correct use of variables, procedures and functions
- Number and types of the parameters in subroutine calls

As in the previous stage, the syntactic structure is defined by the grammar of the language. The semantic information needed to perform the checks is stored in a **symbol table**.

## How It Works

The analyzer is implemented as a **recursive descent parser** with **semantic actions** embedded in the methods of each non-terminal symbol.

Each method, besides matching the expected terminals, can:

- Add new symbols to the symbol table when a declaration is found
- Look up identifiers in the symbol table when they are used
- Return the type of the construct it recognized (e.g., the type of an expression), so that the calling method can verify it

### Symbol Table and Scopes

The symbol table is implemented as a hash table (a Python dictionary) that maps each lexeme to a symbol, which stores:

- Its kind: `program`, `var`, `procedure` or `function`
- Its data type: `integer`, `boolean` or none
- Whether it can be assigned
- The list of parameter types, for procedures and functions

Each procedure or function defines a new scope. When its declaration begins, a new symbol table is created with a reference to the enclosing one, forming a chain of environments. Identifiers are searched first in the current table and then in the enclosing ones. When the declaration ends, the table is discarded and the subroutine is added to the enclosing scope.

Inside a function, its own name is stored as an assignable symbol, which allows setting its return value (e.g., `algo := a + 5`). Outside of it, the name can only be used as a function call.

### Semantic Rules

The following rules are verified during the analysis:

- An identifier cannot be declared twice in the same scope (this includes the program name, variables, parameters, procedures and functions)
- Every identifier must be declared before being used
- Only variables, and a function's name inside its own body, can be assigned or read with `read`
- In an assignment, the type of the expression must match the type of the variable
- The conditions of `if` and `while` must be of type `boolean`
- The operators `+`, `-`, `*` and `div` (and the unary `+` and `-`) require `integer` operands
- The operators `and`, `or` and `not` require `boolean` operands
- The relational operators require `integer` operands and produce a `boolean` result
- Only procedures can be called as statements, and only functions can be called inside expressions
- Calls must provide the exact number of parameters, and each one must match the declared type

## Error Handling

The analysis stops at the first error found, reporting its kind (lexical, syntactic or semantic) along with the row and column where it occurred.

The semantic errors reported are:

- Identifier already declared
- Identifier not declared
- Identifier that cannot be assigned
- Type mismatch, showing the expected type and the type found
- Procedure expected but another kind of identifier found
- Function expected but another kind of identifier found
- Variable or function expected but another kind of identifier found
- Too many parameters in a call
- Not enough parameters in a call

## Running the Analyzer

To execute the syntactic semantic analyzer, run the following command from the root directory:

```bash
python3 -m syntactic_semantic_analyzer.test_syntactic_semantic test_cases/test_case1.pas
```

Additional test cases are provided in the `test_cases` directory (e.g., `test_case2`, `semantic_error_case1`).
You can also provide your own Pascal source file as input to validate different programs.

## Grammar

The analyzer uses the same grammar as the syntactic analyzer. See the [Syntactic Analyzer README](../syntactic_analyzer/README.md#grammar) for the complete BNF definition.
