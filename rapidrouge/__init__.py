# Copyright 2026 William Brach.
# Licensed under the Apache License, Version 2.0 (the "License").
"""rapidrouge — a fast drop-in replacement for ``rouge_score``.

Same interface and **bit-identical** results as ``rouge_score`` (``RougeScorer``,
``scoring.Score``, ``tokenize``, ``tokenizers``), but ROUGE-L's
longest-common-subsequence length is computed with the Hyyrö bit-parallel
algorithm — far faster on long documents.

``rapidrouge`` is pure-Python with zero runtime dependencies::

    pip install rapidrouge

Migration off ``rouge_score`` is a one-line import swap::

    # before:  from rouge_score import rouge_scorer
    from rapidrouge import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=False)
    scorer.score(target, prediction)["rougeL"].fmeasure
"""

from __future__ import annotations

from . import rouge_scorer, scoring, tokenize, tokenizers
from .lcs import lcs_length
from .rouge_scorer import RougeScorer
from .scoring import AggregateScore, BootstrapAggregator, Score, fmeasure

__all__ = [
    # rouge_score-compatible submodules
    "rouge_scorer",
    "scoring",
    "tokenize",
    "tokenizers",
    # convenience re-exports
    "RougeScorer",
    "Score",
    "AggregateScore",
    "BootstrapAggregator",
    "fmeasure",
    # the bit-parallel kernel
    "lcs_length",
]

__version__ = "0.1.0"
