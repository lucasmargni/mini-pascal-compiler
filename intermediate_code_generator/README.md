# Intermediate Code Generator

The **Intermediate Code Generator** is the fourth stage of the Mini Pascal Compiler. Its main responsibility is to translate a valid Mini Pascal program into **MEPA** code, the instruction set of the Pascal Execution Machine (*Máquina de Ejecución para Pascal*).

## Overview

This component extends the syntactic semantic analyzer by adding code generation actions to the parsing process. In a single pass, while the tokens are consumed and the syntactic and semantic rules are verified, the MEPA instructions corresponding to each construct are emitted.

The generator translates, in a general way:

- Program structure and memory reservation for variables
- Procedure and function declarations and calls
- Parameter passing and function return values
- Assignments, `read` and `write` statements
- Control flow constructs such as `if` and `while`
- Arithmetic, relational and logical expressions

If an error is found during the analysis, no code is generated. Otherwise, the resulting instructions are written to a `.mep` file.

## How It Works

The generator is implemented as a **recursive descent parser** with **semantic actions** and **code generation actions** embedded in the methods of each non-terminal symbol.

Each method, besides performing the syntactic and semantic checks described in the previous stages, emits the MEPA instructions of the construct it recognizes. Since expressions are parsed following operator precedence, the instructions are emitted in postfix order, which matches the stack-based evaluation of the MEPA machine.

### Memory Organization

The MEPA machine uses a stack and a display of registers `D[k]`, where each `D[k]` points to the activation record of lexical level `k`. Every variable is identified by a pair `(level, offset)`, which is stored in the symbol table when the variable is declared:

- The main program has lexical level `0`, and each procedure or function increases the level by one
- Variables declared in a block get consecutive non-negative offsets starting at `0`
- Parameters get negative offsets, since they are pushed by the caller before the call. For a subprogram with `n` parameters, the `i`-th parameter is located at offset `-(n + 3 - i)`
- The return value of a function is stored at offset `-(n + 3)`, a memory cell reserved by the caller before pushing the parameters

The offsets of the parameters can only be computed once all of them have been read, since they depend on the total number of parameters.

### Labels

Labels are generated with a counter (`L1`, `L2`, ...) and are used for:

- The entry point of each procedure and function, stored in its symbol so it can be called later
- Jumping over the subprogram declarations of a block, so that the execution starts at its compound statement
- The jumps of the `if` and `while` statements

## Translation to MEPA

| Construct | MEPA instructions |
|-----------|-------------------|
| Program | `INPP` at the beginning, `PARA` at the end |
| Variable declarations | `RMEM n` at the start of the block, `LMEM n` at the end |
| Subprogram declarations | `DSVS` to jump over them, `NADA` to mark the start of the block body |
| Procedure / function declaration | `ENPR k` at its label, `RTPR k,n` at the end |
| Procedure call | Parameters are evaluated, then `LLPR label` |
| Function call | `RMEM 1` for the return value, parameters are evaluated, then `LLPR label` |
| Assignment | The expression is evaluated, then `ALVL level,offset` |
| `read(x)` | `LEER`, then `ALVL level,offset` |
| `write(e)` | The expression is evaluated, then `IMPR` |
| `if` / `if-else` | `DSVF` to the `else` part (or the end), `DSVS` over the `else` part |
| `while` | Label before the condition, `DSVF` to the end, `DSVS` back to the condition |
| Variable / constant | `APVL level,offset` / `APCT value` (`true` = `1`, `false` = `0`) |
| `+` `-` `*` `div` | `SUMA`, `SUST`, `MULT`, `DIVC` + `DIVI` |
| Unary `-` | `UMEN` |
| `and` `or` `not` | `CONJ`, `DISJ`, `NEGA` |
| `=` `<>` `<` `<=` `>` `>=` | `CMIG`, `CMDG`, `CMME`, `CMNI`, `CMMA`, `CMYI` |

The `DIVC` instruction is emitted before each `DIVI` to check that the divisor is not zero.

## Examples

### Local Variables of a Subprogram

```pascal
procedure p;
var x, y: integer;
begin
  x := 1;
  y := x
end;
```

```
L2    ENPR 1        { enter level 1 }
      RMEM 2        { reserve x (1,0) and y (1,1) }
      APCT 1
      ALVL 1,0      { x := 1 }
      APVL 1,0
      ALVL 1,1      { y := x }
      LMEM 2        { free local variables }
      RTPR 1,0      { return from level 1, 0 parameters }
```

### Parameter Passing for a Function

```pascal
function suma(a, b: integer): integer;
var t: integer;
begin
  t := a + b;
  suma := t
end;
...
r := suma(3, 4)
```

```
L2    ENPR 1
      RMEM 1        { local t (1,0) }
      APVL 1,-4     { a is the 1st of 2 parameters: -(2 + 3 - 1) }
      APVL 1,-3     { b is the 2nd of 2 parameters: -(2 + 3 - 2) }
      SUMA
      ALVL 1,0      { t := a + b }
      APVL 1,0
      ALVL 1,-5     { return value: -(2 + 3) }
      LMEM 1
      RTPR 1,2      { return and free the 2 parameters }
...
      RMEM 1        { space for the return value }
      APCT 3        { 1st parameter }
      APCT 4        { 2nd parameter }
      LLPR L2       { call suma }
      ALVL 0,0      { r := return value }
```

### Conditional Statement

```pascal
if (r > 5) then write(r) else write(0)
```

```
      APVL 0,0
      APCT 5
      CMMA          { r > 5 }
      DSVF L3       { if false, jump to else }
      APVL 0,0
      IMPR          { write(r) }
      DSVS L4       { skip the else part }
L3    NADA
      APCT 0
      IMPR          { write(0) }
L4    NADA
```

### Repetitive Statement

```pascal
while (r > 0) do r := r - 1
```

```
L5    NADA          { start of the loop }
      APVL 0,0
      APCT 0
      CMMA          { r > 0 }
      DSVF L6       { if false, exit the loop }
      APVL 0,0
      APCT 1
      SUST
      ALVL 0,0      { r := r - 1 }
      DSVS L5       { back to the condition }
L6    NADA
```

## Error Handling

The generator performs the same checks as the syntactic semantic analyzer. The analysis stops at the first error found, reporting its kind (lexical, syntactic or semantic) along with the row and column where it occurred, and no output file is generated.

See the [Syntactic Semantic Analyzer README](../syntactic_semantic_analyzer/README.md#error-handling) for the complete list of semantic errors.

## Running the Generator

To execute the intermediate code generator, run the following command from the root directory:

```bash
python3 -m intermediate_code_generator.test_intermediate_code_generator test_cases/test_case1.pas
```

The generated code is written to the `mepa_output` directory, using the name of the input file with the `.mep` extension (e.g., `test_cases/test_case1.pas` → `mepa_output/test_case1.mep`). The directory is created automatically if it does not exist.

Additional test cases are provided in the `test_cases` directory (e.g., `test_case14`, which includes nested procedures).
You can also provide your own Pascal source file as input to generate its MEPA code.

## Grammar

The generator uses the same grammar as the syntactic analyzer. See the [Syntactic Analyzer README](../syntactic_analyzer/README.md#grammar) for the complete BNF definition.