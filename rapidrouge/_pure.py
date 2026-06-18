# Copyright 2026 William Brach.
# Licensed under the Apache License, Version 2.0 (the "License").
"""Pure-Python bit-parallel LCS — the reference oracle AND the fallback.

This is the proven Hyyrö bit-parallel kernel and the SOURCE OF TRUTH for ROUGE-L.
It ships in the ``rapidrouge`` wheel and sdist, so ``rapidrouge`` is always correct
and usable with zero runtime dependencies (plain ``pip install rapidrouge``).

`lcs_length(a, b)` returns the *identical* value to a classic O(n*m) dynamic
program, but runs in O(n*m / w) word operations by treating CPython's
arbitrary-precision ``int`` as a bit-vector (Hyyrö 2004). The classic DP,
``_lcs_length_dp``, ships alongside as a tiny, dependency-free reference oracle
used by the test suite.
"""

from __future__ import annotations

__all__ = ["lcs_length", "_lcs_length_dp"]


def lcs_length(a, b) -> int:
    """Length of the longest common subsequence of token lists ``a`` and ``b``.

    Uses Hyyrö's bit-parallel LCS. LCS length is symmetric, so the bit-vector is
    built over the SHORTER sequence to keep the big integers small. Callers must
    therefore NOT rely on any orientation of ``a``/``b`` here.
    """
    if not a or not b:
        return 0
    # Width optimization: bit-vector over the shorter sequence. Length is symmetric.
    if len(a) > len(b):
        a, b = b, a
    pos: dict = {}
    for i, t in enumerate(a):
        pos[t] = pos.get(t, 0) | (1 << i)
    v = (1 << len(a)) - 1
    full = v
    for t in b:
        m = pos.get(t, 0)
        u = v & m
        v = (v + u) | (v - u)
        v &= full
    return ((~v) & full).bit_count()


def _lcs_length_dp(a, b) -> int:
    """Reference classic O(n*m) DP LCS length, used only by the test suite."""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, start=1):
            if x == y:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = prev[j] if prev[j] >= cur[j - 1] else cur[j - 1]
        prev = cur
    return prev[len(b)]
