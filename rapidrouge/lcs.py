# Copyright 2026 William Brach.
# Licensed under the Apache License, Version 2.0 (the "License").
"""LCS entry point for the scorer.

``rouge_scorer`` imports ``lcs_length`` from here, so the scoring code stays
decoupled from the kernel. The implementation is the pure-Python Hyyrö
bit-parallel kernel in ``_pure``.
"""

from __future__ import annotations

from ._pure import lcs_length

__all__ = ["lcs_length"]
