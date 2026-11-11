"""Tiny Axelrod-style match: Tit for Tat against a few classic strategies.

Run: python examples/tit_for_tat.py
"""

C, D = "groom", "refuse"
PAYOFF = {(C, C): (3, 3), (D, D): (1, 1), (D, C): (5, 0), (C, D): (0, 5)}


def tit_for_tat(my_moves, their_moves):
    return their_moves[-1] if their_moves else C  # start nice, then copy


def always_refuse(my_moves, their_moves):
    return D


def always_groom(my_moves, their_moves):
    return C


def play(a, b, rounds=10):
    ma, mb, sa, sb = [], [], 0, 0
    for _ in range(rounds):
        x, y = a(ma, mb), b(mb, ma)
        pa, pb = PAYOFF[(x, y)]
        ma.append(x); mb.append(y); sa += pa; sb += pb
    return sa, sb


for rival in (tit_for_tat, always_groom, always_refuse):
    print(f"tit_for_tat vs {rival.__name__:13s} -> {play(tit_for_tat, rival)}")
