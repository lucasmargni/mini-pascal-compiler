# Mini Pascal Compiler

A **simplified Pascal compiler** developed in Python, as part of an academic project at the *Universidad Nacional del Comahue*.

## About the Project

This repository aims to build a compiler for a **simplified version of the Pascal programming language**, focusing on clarity, structure, and incremental development.

Rather than covering the full complexity of Pascal, this project adopts a **well-defined subset** that preserves its core concepts while remaining approachable from an implementation standpoint. The compiler is designed to evolve step by step, with each stage developed and organized independently.

The compiler translates Pascal source programs into **MEPA** code, the instruction set of the Pascal Execution Machine (*Máquina de Ejecución para Pascal*), and includes an interpreter that executes the generated code, so the whole process can be run and verified from source to output.

## Language Scope

The supported subset of Pascal includes the following elements:

* **Basic types**: `integer`, `boolean`
* **Declarations**: variables, procedures, and functions
* **Control structures**: `if`, `while`
* **Input / Output**: `read`, `write`
* **Expressions**: relational, arithmetic and logical operations

This selection provides a representative model of the language, suitable for exploring compiler construction techniques.

## Repository Structure

```
mini-pascal-compiler/
├── lexical_analyzer/               # Stage 1: tokenization of the source file
├── syntactic_analyzer/             # Stage 2: grammar validation
├── syntactic_semantic_analyzer/    # Stage 3: grammar and semantic validation
├── intermediate_code_generator/    # Stage 4: translation to MEPA code
├── mepa_interpreter/               # Stage 5: execution of the generated MEPA code
├── symbol_table/                   # Symbol table shared by stages 3 and 4
└── test_cases/                     # Example Pascal programs, valid and with errors
```

Each stage has its own README describing how it works and how to run it:

* [Lexical Analyzer](lexical_analyzer/README.md)
* [Syntactic Analyzer](syntactic_analyzer/README.md)
* [Syntactic Semantic Analyzer](syntactic_semantic_analyzer/README.md)
* [Intermediate Code Generator](intermediate_code_generator/README.md)
* [MEPA Interpreter](mepa_interpreter/README.md)

## Compiling and Running a Program

A Pascal program can be compiled and executed in two steps, running the following commands from the root directory:

```bash
# 1. Translate the Pascal program into MEPA code
python3 -m intermediate_code_generator.test_intermediate_code_generator test_cases/test_case1.pas

# 2. Execute the generated MEPA code
python3 mepa_interpreter/MepaInterpreter.py mepa_output/test_case1.mep
```

The first command writes the MEPA code to `mepa_output/test_case1.mep`, and the second one executes it, printing the program output to the console. If the program contains `read` statements, the values are requested from the standard input.

## Academic Context

This work is part of a university-level project in Computer Science, developed with the objective of gaining practical experience in:

* Formal language specification
* Compiler design principles
* Implementation of language processing tools

## Authors

[![lucasmargni](https://img.shields.io/badge/lucasmargni-181717?style=for-the-badge&logo=github)](https://github.com/lucasmargni)
[![nicaFernandez12](https://img.shields.io/badge/nicaFernandez12-181717?style=for-the-badge&logo=github)](https://github.com/nicaFernandez12)

## License

© 2026 Lucas Margni, Nicanor Fernandez. All rights reserved.

This project is provided for academic and educational purposes only.
No part of this repository may be reproduced, distributed, or used for commercial purposes without explicit permission from the authors.