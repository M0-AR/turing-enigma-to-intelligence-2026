"""Part 9: Turing patterns — activator-inhibitor reaction-diffusion.

Turing 1952: maker (activator) makes itself + blocker (inhibitor); blocker
inhibits maker; blocker diffuses faster => spots/stripes from noise.
Validated 1995 Kondo & Asai angelfish; 2026 Bull. Math. Biol. revisit.

Discrete model (Anisotropic Gray-Scott-like activator-inhibitor, stable + fast):
  U += dt*(a - U + U^2 V * k1 - decay...) — we use classic FitzHugh-style:
  du = Du*lap(U) + (U - U^3 - V + alpha)
  dv = Dv*lap(V) + eps*(U - gamma*V)
with Du << Dv for patterns; Du==Dv => fade (video test 1).
Grid with Neumann (edge clamp) boundaries, 4-neighbour Laplacian.
"""
from __future__ import annotations
import random


def lap(grid: list[list[float]]) -> list[list[float]]:
    h, w = len(grid), len(grid[0])
    out = [[0.0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            xm = grid[y][x - 1] if x > 0 else grid[y][x]
            xp = grid[y][x + 1] if x + 1 < w else grid[y][x]
            ym = grid[y - 1][x] if y > 0 else grid[y][x]
            yp = grid[y + 1][x] if y + 1 < h else grid[y][x]
            out[y][x] = xm + xp + ym + yp - 4 * grid[y][x]
    return out


def run_pattern(w: int = 64, h: int = 64, steps: int = 2000, Du: float = 0.16,
                Dv: float = 2.88, alpha: float = -0.05, eps: float = 0.08,
                gamma: float = 2.0, dt: float = 0.05, seed: int = 0) -> list[list[float]]:
    """Returns maker field U. Dv/Du=18 => stripes/spots; Dv==Du => fade."""
    rng = random.Random(seed)
    U = [[rng.uniform(-0.1, 0.1) for _ in range(w)] for _ in range(h)]
    V = [[rng.uniform(-0.1, 0.1) for _ in range(w)] for _ in range(h)]
    for _ in range(steps):
        LU, LV = lap(U), lap(V)
        for y in range(h):
            for x in range(w):
                u, v = U[y][x], V[y][x]
                U[y][x] = u + dt * (Du * LU[y][x] + (u - u**3 - v + alpha))
                V[y][x] = v + dt * (Dv * LV[y][x] + eps * (u - gamma * v))
    return U


def pattern_stats(U: list[list[float]]) -> dict:
    flat = [v for row in U for v in row]
    mean = sum(flat) / len(flat)
    var = sum((v - mean) ** 2 for v in flat) / len(flat)
    # crude spot count: local maxima above mean+std
    import math
    std = math.sqrt(var)
    h, w = len(U), len(U[0])
    peaks = 0
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            v = U[y][x]
            if v > mean + std and v >= max(U[y-1][x], U[y+1][x], U[y][x-1], U[y][x+1]):
                peaks += 1
    return {"mean": mean, "std": std, "var": var, "peaks": peaks}
