# Copyright 2026 William Brach.
# Portions derived from google-research/rouge_score (Apache License 2.0).
"""Tokenizer definitions, drop-in compatible with ``rouge_score.tokenizers``.

A ``RougeScorer`` can be instantiated with the tokenizers defined here. New
tokenizers can be defined by subclassing :class:`Tokenizer` and overriding
``tokenize()``.

The Porter stemmer (used when ``use_stemmer=True``) is imported lazily from
``nltk`` so that the common ``use_stemmer=False`` path keeps zero dependencies.
"""

from __future__ import annotations

import abc

from . import tokenize


class Tokenizer(abc.ABC):
    """Abstract base class for a tokenizer.

    Subclasses of Tokenizer must implement the ``tokenize()`` method.
    """

    @abc.abstractmethod
    def tokenize(self, text):
        raise NotImplementedError("Tokenizer must override tokenize() method")


class DefaultTokenizer(Tokenizer):
    """Default tokenizer; matches ``rouge_score``'s default tokenizer exactly."""

    def __init__(self, use_stemmer=False):
        """Constructor for DefaultTokenizer.

        Args:
            use_stemmer: bool; whether the Porter stemmer should be used to strip
                word suffixes to improve matching. Requires ``nltk`` (install the
                ``stemmer`` extra). When False, no third-party deps are needed.
        """
        if use_stemmer:
            # Lazy import: only stemming pulls in nltk, matching rouge_score's
            # PorterStemmer so results stay bit-identical.
            from nltk.stem import porter

            self._stemmer = porter.PorterStemmer()
        else:
            self._stemmer = None

    def tokenize(self, text):
        return tokenize.tokenize(text, self._stemmer)
