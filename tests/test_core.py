import sys
sys.path.insert(0, "src")
from turing_universe.turing_machine import TuringMachine, binary_increment_table, run_blank, beaver_table_2state
from turing_universe.enigma import EnigmaMachine

def test_increment():
    tm = TuringMachine(binary_increment_table())
    out, steps, _ = tm.run("1011")
    assert out == "1100" and steps == 8

def test_bb2():
    s, h, _ = run_blank(beaver_table_2state(), "A", 100)
    assert h and s == 6

def test_enigma_vectors():
    e = EnigmaMachine(["I","II","III"], ["A","A","A"], ["A","A","A"], {}, "B")
    assert e.encrypt("AAAAA") == "BDZGO"
    e1 = EnigmaMachine(["I","II","III"], ["A","A","A"], ["A","A","A"], {}, "B")
    ct = e1.encrypt("HELLOWORLD")
    e2 = EnigmaMachine(["I","II","III"], ["A","A","A"], ["A","A","A"], {}, "B")
    assert e2.encrypt(ct) == "HELLOWORLD"
    e3 = EnigmaMachine(["I","II","III"], ["A","A","A"], ["A","A","A"], {}, "B")
    c = e3.encrypt("A"*100)
    assert all(a != b for a, b in zip("A"*100, c))
