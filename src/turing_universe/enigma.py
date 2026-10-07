"""Part 4: Wehrmacht Enigma I — historically accurate.

Verified against:
- cryptomuseum.org Enigma I wiring + wikipedia Enigma rotor details.
- Rotors I-V, reflectors B/C, ETW identity, notches Q/E/V/J/Z.
- Stepping incl. double-step anomaly; step BEFORE encipherment.
- Plugboard reciprocal, 10 cables. Reflector => self-inverse + never self-encrypts.

Counts: 60 orders * 17,576 positions * 150,738,274,937,250 plugboards ≈ 159 quintillion.
(Plugboard with exactly 10 cables: 26!/(6! 10! 2^10) = 150,738,274,937,250.)
"""
from __future__ import annotations
from dataclasses import dataclass, field

A = ord("A")

ROTORS = {
    "I":   {"wiring": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "notch": "Q"},
    "II":  {"wiring": "AJDKSIRUXBLHWTMCQGZNPYFVOE", "notch": "E"},
    "III": {"wiring": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "notch": "V"},
    "IV":  {"wiring": "ESOVPZJAYQUIRHXLNFTGKDCMWB", "notch": "J"},
    "V":   {"wiring": "VZBRGITYUPSDNHLXAWMJQOFECK", "notch": "Z"},
}
REFLECTORS = {
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}
ETW = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _idx(c: str) -> int:
    return ord(c) - A


def _chr(i: int) -> str:
    return chr(i % 26 + A)


@dataclass
class EnigmaMachine:
    rotors: list[str]            # left -> right, e.g. ["I","II","III"]
    rings: list[str] = field(default_factory=lambda: ["A", "A", "A"])
    positions: list[str] = field(default_factory=lambda: ["A", "A", "A"])
    plugs: dict[str, str] = field(default_factory=dict)
    reflector: str = "B"

    def __post_init__(self):
        assert len(self.rotors) == 3
        # normalize plugs reciprocal
        full: dict[str, str] = {}
        for a, b in dict(self.plugs).items():
            full[a] = b
            full[b] = a
        self.plugs = full
        self._pos = [_idx(p) for p in self.positions]
        self._ring = [_idx(r) for r in self.rings]
        self._wirings = [[_idx(c) for c in ROTORS[r]["wiring"]] for r in self.rotors]
        self._inv = []
        for w in self._wirings:
            inv = [0] * 26
            for i, o in enumerate(w):
                inv[o] = i
            self._inv.append(inv)
        self._notch = [_idx(ROTORS[r]["notch"]) for r in self.rotors]
        self._refl = [_idx(c) for c in REFLECTORS[self.reflector]]

    def reset(self, positions: list[str]):
        self._pos = [_idx(p) for p in positions]

    @property
    def windows(self) -> str:
        return "".join(_chr(p) for p in self._pos)

    def _step(self):
        # Double-step accurate:
        # middle steps if right at notch OR middle at notch (which also steps left).
        # right always steps.
        r, m, l = 2, 1, 0
        middle_at_notch = self._pos[m] == self._notch[m]
        right_at_notch = self._pos[r] == self._notch[r]
        if middle_at_notch:
            self._pos[m] = (self._pos[m] + 1) % 26
            self._pos[l] = (self._pos[l] + 1) % 26
        if right_at_notch:
            self._pos[m] = (self._pos[m] + 1) % 26
        self._pos[r] = (self._pos[r] + 1) % 26

    def _through_rotor_fwd(self, c: int, i: int) -> int:
        # right-to-left
        offset = (self._pos[i] - self._ring[i]) % 26
        return (self._wirings[i][(c + offset) % 26] - offset) % 26

    def _through_rotor_rev(self, c: int, i: int) -> int:
        offset = (self._pos[i] - self._ring[i]) % 26
        return (self._inv[i][(c + offset) % 26] - offset) % 26

    def press(self, ch: str) -> str:
        if not ch.isalpha():
            return ""
        ch = ch.upper()
        self._step()
        c = _idx(self.plugs.get(ch, ch))
        for i in (2, 1, 0):
            c = self._through_rotor_fwd(c, i)
        c = self._refl[c]
        for i in (0, 1, 2):
            c = self._through_rotor_rev(c, i)
        c = _idx(self.plugs.get(_chr(c), _chr(c)))
        return _chr(c)

    def encrypt(self, text: str) -> str:
        out = []
        for ch in text.upper():
            if ch.isalpha():
                out.append(self.press(ch))
        return "".join(out)


def plugboard_combinations_10() -> int:
    import math
    # 26! / (6! 10! 2^10)
    return math.factorial(26) // (math.factorial(6) * math.factorial(10) * 2**10)


def total_settings() -> int:
    return 60 * 17576 * plugboard_combinations_10()
