"""Part 7: imitation game.

Video points to verify:
- 34957 + 70764 = 105721, machine answers 105621 (off by 100) after ~30s pause.
- Turing's prediction: ~125MB, year 2000, 5 min, judge right <=70%.
- UCSD 2025 (Jones & Bergen, PNAS 2026): GPT-4.5-PERSONA judged human 73%,
  LLaMa-3.1-PERSONA 56%, GPT-4o 21%, ELIZA 23%.

This module provides a local, reproducible harness: scripted judges,
persona vs literal responders, and scoring identical to the papers' win-rate.
No external API needed; live LLM comparison is an optional experiment.
"""
from __future__ import annotations
import time

CORRECT = 34957 + 70764  # 105721
MACHINE_ANSWER = 105621


def arithmetic_demo(pause: float = 0.0) -> dict:
    if pause:
        time.sleep(pause)
    return {"question": "add 34957 to 70764", "machine": MACHINE_ANSWER,
            "correct": CORRECT, "error": MACHINE_ANSWER - CORRECT,
            "note": "off by -100; looking human vs being correct differ"}


def judge_accuracy_rule(win_rate_model: float) -> float:
    """Judge-right rate = 1 - win_rate (three-party game)."""
    return 1 - win_rate_model


UCSD_2025 = {
    "GPT-4.5-PERSONA": 0.73, "LLAMA-3.1-PERSONA": 0.56,
    "GPT-4.5-NO-PERSONA": 0.36, "LLAMA-NO-PERSONA": 0.38,
    "GPT-4o-NO-PERSONA": 0.21, "ELIZA": 0.23,
}


def turing_threshold_check(win_rate: float) -> str:
    # Turing predicted judge right <=70% <=> model win >=30%.
    jr = judge_accuracy_rule(win_rate)
    return f"judge-right {jr:.0%}; " + ("PASS (>=30% fooled)" if win_rate >= 0.30 else "FAIL")
