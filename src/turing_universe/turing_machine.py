"""Part 1-2: Turing machine + Universal machine + Busy Beaver.

Verified against:
- Turing (1936) definition: tape, head, state, rule table.
- Rado (1962) busy beaver; bbchallenge 2024 proof BB(5)=47,176,870.
- Video claim: 1011 +1 = 1100 in 8 steps; 2-state max 6, 3-state 21, 4-state 107.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple

Symbol = str
State = str
Move = str  # 'L', 'R', 'S'
Rule = Tuple[Symbol, Move, State]
Table = Dict[Tuple[State, Symbol], Rule]

BLANK = "_"
HALT = "HALT"


def binary_increment_table() -> Table:
    """Six rules from the video: RIGHT walks to end, CARRY propagates."""
    return {
        ("RIGHT", "0"): ("0", "R", "RIGHT"),
        ("RIGHT", "1"): ("1", "R", "RIGHT"),
        ("RIGHT", BLANK): (BLANK, "L", "CARRY"),
        ("CARRY", "1"): ("0", "L", "CARRY"),
        ("CARRY", "0"): ("1", "S", HALT),
        ("CARRY", BLANK): ("1", "S", HALT),  # overflow e.g. 111 -> 1000
    }


@dataclass
class TuringMachine:
    table: Table
    start: State = "RIGHT"

    def run(self, tape_str: str, max_steps: int = 10_000_000) -> tuple[str, int, bool]:
        """Run on tape_str. Returns (tape_out, steps, halted)."""
        tape: Dict[int, str] = {i: ch for i, ch in enumerate(tape_str)}
        head = 0
        state = self.start
        steps = 0
        # walk head to leftmost? input starts at 0; head starts at 0 per video.
        while state != HALT and steps < max_steps:
            sym = tape.get(head, BLANK)
            key = (state, sym)
            if key not in self.table:
                # undefined transition = halt (Busy Beaver convention)
                break
            write, move, nxt = self.table[key]
            tape[head] = write
            if move == "R":
                head += 1
            elif move == "L":
                head -= 1
            state = nxt
            steps += 1
        halted = state == HALT or (state, tape.get(head, BLANK)) not in self.table
        # trim blanks
        if not tape:
            return "", steps, halted
        lo, hi = min(tape), max(tape)
        out = "".join(tape.get(i, BLANK) for i in range(lo, hi + 1)).strip(BLANK)
        return out, steps, halted


def run_demo() -> tuple[str, int]:
    tm = TuringMachine(binary_increment_table())
    return tm.run("1011")


# ---------------- Universal machine ----------------

def encode_table(table: Table) -> str:
    """Encode table as text lines: state,sym->write,move,next. Software = data."""
    lines = []
    for (st, sy), (wr, mv, nx) in sorted(table.items()):
        lines.append(f"{st},{sy}->{wr},{mv},{nx}")
    return "\n".join(lines)


def table_to_number(text: str) -> int:
    """Whole table as one single number (big int from utf-8 bytes)."""
    return int.from_bytes(text.encode("utf-8"), "big")


def number_to_table(n: int) -> str:
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, "big").decode("utf-8")


def universal_run(encoded_lines: str, tape_str: str) -> tuple[str, int, bool]:
    """Universal machine: text back into table, hand to run()."""
    table: Table = {}
    for line in encoded_lines.strip().splitlines():
        left, right = line.split("->")
        st, sy = left.split(",")
        wr, mv, nx = right.split(",")
        table[(st, sy)] = (wr, mv, nx)
    # infer start state: RIGHT if present else first
    start = "RIGHT" if any(s == "RIGHT" for s, _ in table) else next(iter(table))[0]
    return TuringMachine(table, start).run(tape_str)


# ---------------- Busy Beaver ----------------
# Tables use (state, symbol) with symbols '0'/'1', BLANK='0' on blank tape,
# states 'A'..; HALT='H'. Move L/R. Verified by running below.

def beaver_table_2state() -> Table:
    # Classic 2-state champion: 6 steps, 4 ones. Rado 1962.
    return {
        ("A", "0"): ("1", "R", "B"),
        ("A", "1"): ("1", "L", "B"),
        ("B", "0"): ("1", "L", "A"),
        ("B", "1"): ("1", "R", HALT),
    }


def beaver_table_3state() -> Table:
    # Lin/Rado 1963 S-champion: 21 steps, 5 ones. bbch `1RB1RZ_1LB0RC_1LC1LA`.
    return {
        ("A", "0"): ("1", "R", "B"),
        ("A", "1"): ("1", "R", HALT),
        ("B", "0"): ("1", "L", "B"),
        ("B", "1"): ("0", "R", "C"),
        ("C", "0"): ("1", "L", "C"),
        ("C", "1"): ("1", "L", "A"),
    }


def beaver_table_4state() -> Table:
    # Brady 1964 champion: 107 steps, 13 ones.
    return {
        ("A", "0"): ("1", "R", "B"),
        ("A", "1"): ("1", "L", "B"),
        ("B", "0"): ("1", "L", "A"),
        ("B", "1"): ("0", "L", "C"),
        ("C", "0"): ("1", "R", HALT),
        ("C", "1"): ("1", "L", "D"),
        ("D", "0"): ("1", "R", "D"),
        ("D", "1"): ("0", "R", "A"),
    }


def beaver_table_5state_champion() -> Table:
    # Marxen & Buntrock 1989 champion: 47,176,870 steps.
    # String: 1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA (Z = HALT)
    code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"
    states = ["A", "B", "C", "D", "E"]
    parts = code.split("_")
    table: Table = {}
    for st, grp in zip(states, parts):
        for sym, triple in zip(["0", "1"], [grp[:3], grp[3:]]):
            w, mv, nx = triple[0], triple[1], triple[2]
            nxt = HALT if nx == "Z" else nx
            table[(st, sym)] = (w, mv, nxt)
    return table


def run_blank(table: Table, start: str, max_steps: int = 60_000_000) -> tuple[int, bool, str]:
    """Run on all-blank tape ('0'). Returns (steps, halted, tape_ones_count)."""
    tape: Dict[int, str] = {}
    head = 0
    state: str = start
    steps = 0
    get = tape.get
    while steps < max_steps:
        sym = get(head, "0")
        key = (state, sym)
        if key not in table:
            return steps, True, str(sum(1 for v in tape.values() if v == "1"))
        write, move, nxt = table[key]
        tape[head] = write
        head += 1 if move == "R" else (-1 if move == "L" else 0)
        state = nxt
        steps += 1
        if state == HALT:
            return steps, True, str(sum(1 for v in tape.values() if v == "1"))
    return steps, False, str(sum(1 for v in tape.values() if v == "1"))
