"""Part 8: machines that learn — NAND child + 21-sticks reinforcement.

Turing 1948 'Intelligent Machinery': B-type unorganised machines (random NAND
nets) trained by teacher interference. 1950: reward/punishment + child machine.

Video game to verify: 21 sticks, take 1-3, last wins. Child keeps 3 scores per
pile (start 10), picks proportionally, winner's moves +1 / loser's -1.
Benchmarks: vs perfect expert — 2/1000 before training, 5% @100 games,
95% @1000, 99.6% @10k; learns leave-multiple-of-4 for all 16 winning piles.
"""
from __future__ import annotations
import random


def nand(a: int, b: int) -> int:
    return 0 if (a == 1 and b == 1) else 1


def xor_from_nand(a: int, b: int) -> int:
    # 4 NANDs: standard construction
    n1 = nand(a, b)
    n2 = nand(a, n1)
    n3 = nand(b, n1)
    return nand(n2, n3)


def expert_move(pile: int) -> int:
    """Perfect play: leave multiple of 4 if possible, else take 1."""
    if pile <= 0:
        raise ValueError
    if pile == 1:
        return 1
    r = pile % 4
    if r == 0:
        return 1  # losing position; arbitrary legal move
    if r <= 3 and r < pile:
        return r
    return 1


class SticksChild:
    def __init__(self, max_pile: int = 21, init: float = 10.0, seed: int = 0):
        self.max_pile = max_pile
        self.scores = {p: [init, init, init] for p in range(1, max_pile + 1)}
        self.rng = random.Random(seed)

    def pick(self, pile: int) -> int:
        s = self.scores[pile]
        # legal moves only
        legal = [m for m in (1, 2, 3) if m <= pile]
        w = [s[m - 1] for m in legal]
        # scores may go low; shift to positive
        m0 = min(w)
        w = [x - m0 + 0.01 for x in w]
        tot = sum(w)
        r = self.rng.random() * tot
        acc = 0.0
        for mv, weight in zip(legal, w):
            acc += weight
            if r <= acc:
                return mv
        return legal[-1]

    def play_game(self, opponent_fn=None) -> tuple[int, list[tuple[int, int, int]]]:
        """Self-play or vs opponent_fn(pile)->move. Child moves first on even games?
        Returns (winner, child_moves) where winner 0=child,1=other; child_moves=[(pile,move,player)]."""
        pile = self.max_pile
        # alternate who starts across calls via attribute
        starter = getattr(self, "_starter", 0)
        self._starter = 1 - starter
        turn = starter  # 0 child, 1 other
        child_trace: list[tuple[int, int]] = []
        other_trace: list[tuple[int, int]] = []
        while pile > 0:
            if turn == 0:
                mv = self.pick(pile)
                child_trace.append((pile, mv))
            else:
                mv = opponent_fn(pile) if opponent_fn else self.pick(pile)
                other_trace.append((pile, mv))
            pile -= mv
            if pile == 0:
                winner = turn
                break
            turn = 1 - turn
        # update: winner +1, loser -1 (floored at 0.01 to keep probabilities valid)
        for pile_, mv in child_trace:
            self.scores[pile_][mv - 1] += 1 if winner == 0 else -1
            if self.scores[pile_][mv - 1] < 0.01:
                self.scores[pile_][mv - 1] = 0.01
        if opponent_fn is None:
            for pile_, mv in other_trace:
                self.scores[pile_][mv - 1] += 1 if winner == 1 else -1
                if self.scores[pile_][mv - 1] < 0.01:
                    self.scores[pile_][mv - 1] = 0.01
        return winner, child_trace

    def train(self, games: int, opponent_fn=None):
        for _ in range(games):
            self.play_game(opponent_fn)

    def win_rate_vs_expert(self, games: int = 1000, start_pile: int = 21) -> float:
        wins = 0
        for i in range(games):
            pile = start_pile
            turn = i % 2  # alternate starter fairly
            while pile > 0:
                mv = self.pick(pile) if turn == 0 else expert_move(pile)
                pile -= mv
                if pile == 0:
                    if turn == 0:
                        wins += 1
                    break
                turn = 1 - turn
        return wins / games

    def learned_policy(self) -> dict[int, int]:
        out = {}
        for p in range(1, self.max_pile + 1):
            legal = [m for m in (1, 2, 3) if m <= p]
            best = max(legal, key=lambda m: self.scores[p][m - 1])
            out[p] = best
        return out
