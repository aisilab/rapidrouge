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

    # Width optimization: build the bit-vector over the SHORTER sequence so the
    # big integers stay as narrow as possible. LCS length is symmetric, so
    # choosing the orientation here does not change the result.
    if len(a) <= len(b):
        shorter, longer = a, b
    else:
        shorter, longer = b, a

    # match_bits[token] has bit i set for every position i where `token` occurs
    # in `shorter` (Hyyrö's per-character match masks).
    match_bits: dict = {}
    for position, token in enumerate(shorter):
        match_bits[token] = match_bits.get(token, 0) | (1 << position)

    all_ones = (1 << len(shorter)) - 1  # mask covering every valid bit position
    row = all_ones  # Hyyrö's running bit-vector V (one DP row, all bits set)

    # Sweep the longer sequence one token at a time, advancing the bit-vector.
    for token in longer:
        matches = match_bits.get(token, 0)
        carry = row & matches
        # (row + carry) | (row - carry) propagates every LCS increment across
        # all positions in a single word operation (Hyyrö 2004); mask back to
        # the valid bits afterwards.
        row = (row + carry) | (row - carry)
        row &= all_ones

    # Each ZERO bit remaining in `row` accounts for one unit of LCS length.
    zero_bits = (~row) & all_ones
    return zero_bits.bit_count()


def _lcs_length_dp(a, b) -> int:
    """Reference classic O(n*m) DP LCS length, used only by the test suite."""
    if not a or not b:
        return 0
    prev_row = [0] * (len(b) + 1)
    for token_a in a:
        cur_row = [0] * (len(b) + 1)
        for j, token_b in enumerate(b, start=1):
            if token_a == token_b:
                cur_row[j] = prev_row[j - 1] + 1
            else:
                # equivalently max(prev_row[j], cur_row[j - 1])
                cur_row[j] = prev_row[j] if prev_row[j] >= cur_row[j - 1] else cur_row[j - 1]
        prev_row = cur_row
    return prev_row[len(b)]
