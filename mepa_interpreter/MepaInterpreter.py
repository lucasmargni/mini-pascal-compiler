#!/usr/bin/env python3
"""
MEPA interpreter (Maquina de Ejecucion de Pascal).

Usage:
    python3 mepa.py program.mep                  # run the program
    python3 mepa.py program.mep --trace          # print every instruction and the stack
    python3 mepa.py program.mep --input data.txt # read the LEER values from a file
    python3 mepa.py program.mep --list           # print the loaded program (with addresses)

Accepted format (one instruction per line):
    [LABEL[:]]  INSTR  [arg1[,arg2[,arg3]]]   [{ comment }]
E.g.: "L2    ENPR 1", "      APVL 1,-4", "L3: NADA", "APVL 1, -4  { n }"
Comments starting with //, # or ; and empty lines are also ignored.
"""

import argparse
import re
import sys

# Number of arguments of each instruction
ARITY = {
    "INPP": 0, "PARA": 0, "NADA": 0,
    "APCT": 1, "APVL": 2, "ALVL": 2,
    "SUMA": 0, "SUST": 0, "MULT": 0, "DIVI": 0, "MODU": 0, "UMEN": 0,
    "CONJ": 0, "DISJ": 0, "NEGA": 0,
    "CMME": 0, "CMMA": 0, "CMIG": 0, "CMDG": 0, "CMNI": 0, "CMYI": 0,
    "DSVS": 1, "DSVF": 1,
    "LEER": 0, "LELN": 0, "IMPR": 0, "IMLN": 0,
    "RMEM": 1, "LMEM": 1, "ENPR": 1, "LLPR": 1, "RTPR": 2,
    "APAR": 2, "ALAR": 2, "PUAR": 3, "POAR": 3,
    "APRE": 2, "ALRE": 2, "PURE": 3, "PORE": 3,
    "CONT": 2, "DIVC": 0,
}
JUMPS = {"DSVS", "DSVF", "LLPR"}

MAX_STACK = 1_000_000      # cells of the stack M
MAX_STEPS = 50_000_000     # executed instructions before assuming an infinite loop

class MepaError(Exception):
    pass

# Program loading

def strip_comments(line: str) -> str:
    line = re.sub(r"\{.*?\}", " ", line)
    line = re.sub(r"\(\*.*?\*\)", " ", line)
    for mark in ("//", "#", ";"):
        pos = line.find(mark)
        if pos != -1:
            line = line[:pos]
    return line.strip()

def load(path: str):
    """Return (program, labels).
    program: list of (op, args, line_number, original_text).
    labels:  dict label -> instruction index."""
    with open(path, encoding="utf-8", errors="replace") as f:
        raw_lines = f.read().splitlines()

    program, labels = [], {}
    pending_labels = []
    for lineno, raw in enumerate(raw_lines, 1):
        text = strip_comments(raw)
        if not text:
            continue
        # split arguments: "APVL 1,-4" / "APVL 1, -4" / "APVL 1 -4"
        tokens = text.replace(",", " ").split()

        # optional label at the beginning of the line
        if tokens[0].upper() not in ARITY:
            lab = tokens[0].rstrip(":").upper()
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", lab):
                raise MepaError(f"line {lineno}: unknown instruction '{tokens[0]}'")
            if lab in labels or lab in pending_labels:
                raise MepaError(f"line {lineno}: label '{lab}' defined twice")
            pending_labels.append(lab)
            tokens = tokens[1:]
            if not tokens:          # label alone on its line: points to the next instruction
                continue

        op = tokens[0].upper()
        if op not in ARITY:
            raise MepaError(f"line {lineno}: unknown instruction '{tokens[0]}'")
        args = tokens[1:]
        if len(args) != ARITY[op]:
            raise MepaError(f"line {lineno}: {op} expects {ARITY[op]} argument(s) "
                            f"but got {len(args)}: '{raw.strip()}'")

        for lab in pending_labels:
            labels[lab] = len(program)
        pending_labels = []

        if op in JUMPS:
            parsed = [args[0].upper()]
        else:
            try:
                parsed = [int(a) for a in args]
            except ValueError:
                raise MepaError(f"line {lineno}: non-integer argument in '{raw.strip()}'")
        program.append((op, parsed, lineno, raw.strip()))

    for lab in pending_labels:          # label at the end of the file
        labels[lab] = len(program)

    # resolve jump targets
    resolved = []
    for op, args, lineno, raw in program:
        if op in JUMPS:
            lab = args[0]
            if lab in labels:
                args = [labels[lab]]
            elif lab.lstrip("-").isdigit():
                args = [int(lab)]
            else:
                raise MepaError(f"line {lineno}: undefined label '{lab}'")
        resolved.append((op, args, lineno, raw))

    if not resolved:
        raise MepaError("the program is empty")
    return resolved, labels

# Input

class Input:
    def __init__(self, stream, interactive):
        self.stream = stream
        self.interactive = interactive
        self.buffer = []

    def _fill(self):
        while not self.buffer:
            if self.interactive:
                sys.stdout.write("? ")
                sys.stdout.flush()
            line = self.stream.readline()
            if line == "":
                raise MepaError("LEER: end of input reached, no more values to read")
            self.buffer = line.split()

    def read_int(self, newline=False):
        self._fill()
        tok = self.buffer.pop(0)
        if newline:
            self.buffer = []
        low = tok.lower()
        if low == "true":
            return 1
        if low == "false":
            return 0
        try:
            return int(tok)
        except ValueError:
            raise MepaError(f"LEER: integer expected but '{tok}' was read")

# Machine

def run(program, inp: Input, out, trace=False, trace_out=sys.stderr):
    M = [0] * 1024
    D = [0] * 64
    s = -1
    i = 0
    steps = 0
    started = False

    def ensure(addr):
        nonlocal M
        if addr < 0:
            raise MepaError(f"invalid memory access M[{addr}]")
        if addr >= MAX_STACK:
            raise MepaError("stack overflow (possible infinite recursion)")
        if addr >= len(M):
            M.extend([0] * max(len(M), addr - len(M) + 1))

    def need(k):
        if s - k + 1 < 0:
            raise MepaError(f"stack underflow: {k} value(s) required")

    def disp(k):
        if not 0 <= k < len(D):
            raise MepaError(f"lexical level {k} out of the display")
        return D[k]

    while True:
        if not 0 <= i < len(program):
            raise MepaError(f"program counter out of the code (i={i}); "
                            "missing PARA or RTPR returned to an invalid address")
        op, a, lineno, raw = program[i]
        steps += 1
        if steps > MAX_STEPS:
            raise MepaError(f"more than {MAX_STEPS} instructions executed (possible infinite loop)")
        if not started and op != "INPP":
            raise MepaError("the first executed instruction must be INPP")
        nxt = i + 1

        if trace:
            top = M[max(0, s - 7):s + 1] if s >= 0 else []
            pre = "... " if s > 7 else ""
            trace_out.write(f"[{i:4}] {raw:<24} s={s:<4} stack={pre}{top}\n")

        try:
            if op == "INPP":
                s = -1; D[0] = 0; started = True
            elif op == "PARA":
                return s
            elif op == "NADA":
                pass
            elif op == "APCT":
                s += 1; ensure(s); M[s] = a[0]
            elif op == "APVL":
                addr = disp(a[0]) + a[1]; ensure(addr)
                s += 1; ensure(s); M[s] = M[addr]
            elif op == "ALVL":
                need(1); addr = disp(a[0]) + a[1]; ensure(addr)
                M[addr] = M[s]; s -= 1
            elif op in ("SUMA", "SUST", "MULT", "DIVI", "MODU",
                        "CONJ", "DISJ", "CMME", "CMMA", "CMIG", "CMDG", "CMNI", "CMYI"):
                need(2)
                x, y = M[s - 1], M[s]
                if op == "SUMA": r = x + y
                elif op == "SUST": r = x - y
                elif op == "MULT": r = x * y
                elif op in ("DIVI", "MODU"):
                    if y == 0:
                        raise MepaError("division by zero")
                    q = abs(x) // abs(y)            # truncate towards 0 (as Pascal does)
                    if (x < 0) != (y < 0):
                        q = -q
                    r = q if op == "DIVI" else x - q * y
                elif op == "CONJ": r = 1 if (x == 1 and y == 1) else 0
                elif op == "DISJ": r = 1 if (x == 1 or y == 1) else 0
                elif op == "CMME": r = int(x < y)
                elif op == "CMMA": r = int(x > y)
                elif op == "CMIG": r = int(x == y)
                elif op == "CMDG": r = int(x != y)
                elif op == "CMNI": r = int(x <= y)
                else: r = int(x >= y)
                M[s - 1] = r; s -= 1
            elif op == "UMEN":
                need(1); M[s] = -M[s]
            elif op == "NEGA":
                need(1); M[s] = 1 - M[s]
            elif op == "DSVS":
                nxt = a[0]
            elif op == "DSVF":
                need(1)
                if M[s] == 0:
                    nxt = a[0]
                s -= 1
            elif op in ("LEER", "LELN"):
                v = inp.read_int(newline=(op == "LELN"))
                s += 1; ensure(s); M[s] = v
            elif op in ("IMPR", "IMLN"):
                need(1)
                out.write(f"{M[s]}\n"); out.flush()
                s -= 1
            elif op == "RMEM":
                s += a[0]; ensure(max(s, 0))
            elif op == "LMEM":
                s -= a[0]
                if s < -1:
                    raise MepaError("LMEM freed more memory than reserved")
            elif op == "ENPR":
                k = a[0]; disp(k)
                s += 1; ensure(s); M[s] = D[k]; D[k] = s + 1
            elif op == "LLPR":
                s += 1; ensure(s); M[s] = i + 1; nxt = a[0]
            elif op == "RTPR":
                k, n = a; disp(k); need(2)
                D[k] = M[s]; nxt = M[s - 1]; s -= n + 2
            elif op == "APAR" or op == "APRE":
                need(1); addr = disp(a[0]) + a[1] + M[s]; ensure(addr)
                M[s] = M[addr]
            elif op == "ALAR":
                need(2); addr = disp(a[0]) + a[1] + M[s - 1]; ensure(addr)
                M[addr] = M[s]; s -= 2
            elif op == "ALRE":
                need(2); addr = disp(a[0]) + a[1] + M[s]; ensure(addr)
                M[addr] = M[s - 1]; s -= 2
            elif op in ("PUAR", "PURE"):
                m, n, l = a; base = disp(m) + n
                for idx in range(l):
                    ensure(base + idx); s += 1; ensure(s); M[s] = M[base + idx]
            elif op in ("POAR", "PORE"):
                m, n, l = a; base = disp(m) + n; need(l)
                for idx in range(l - 1, -1, -1):
                    ensure(base + idx); M[base + idx] = M[s]; s -= 1
            elif op == "CONT":
                need(1)
                if not a[0] <= M[s] <= a[1]:
                    raise MepaError(f"value {M[s]} out of range [{a[0]}..{a[1]}]")
            elif op == "DIVC":
                need(1)
                if M[s] == 0:
                    raise MepaError("division by zero")
        except MepaError as e:
            raise MepaError(f"{e}\n  at instruction {i} (line {lineno}): {raw}") from None

        i = nxt

def main():
    ap = argparse.ArgumentParser(description="MEPA interpreter")
    ap.add_argument("file", help=".mep program")
    ap.add_argument("--trace", action="store_true", help="print an execution trace to stderr")
    ap.add_argument("--input", help="file with the values for LEER (default: stdin)")
    ap.add_argument("--list", action="store_true", help="print the loaded program and exit")
    args = ap.parse_args()

    try:
        program, labels = load(args.file)
    except (MepaError, OSError) as e:
        print(f"Load error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.list:
        inv = {}
        for lab, pos in labels.items():
            inv.setdefault(pos, []).append(lab)
        for idx, (op, a, lineno, raw) in enumerate(program):
            lab = ",".join(inv.get(idx, []))
            print(f"{idx:4}  {lab:<6} {op} {','.join(map(str, a))}")
        return

    if args.input:
        stream, interactive = open(args.input), False
    else:
        stream, interactive = sys.stdin, sys.stdin.isatty()

    try:
        final_s = run(program, Input(stream, interactive), sys.stdout, trace=args.trace)
    except MepaError as e:
        sys.stdout.flush()
        print(f"\nRuntime error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)

    if final_s != -1:
        print(f"Warning: the program ended with the stack at s={final_s} (expected -1); "
              "check RMEM/LMEM", file=sys.stderr)

if __name__ == "__main__":
    main()
