"""turing_universe: from Turing machine to Enigma to learning — verified from scratch."""
from .turing_machine import TuringMachine, binary_increment_table, run_demo
from .enigma import EnigmaMachine, ROTORS, REFLECTORS

__all__ = [
    "TuringMachine",
    "binary_increment_table",
    "run_demo",
    "EnigmaMachine",
    "ROTORS",
    "REFLECTORS",
]
__version__ = "1.0.0"
