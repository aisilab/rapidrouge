# Copyright 2026 William Brach.
# Portions derived from google-research/rouge_score (Apache License 2.0).
"""A library for tokenizing text.

This reproduces ``rouge_score.tokenize`` byte-for-byte so that the default
tokenizer behaves identically to ``rouge_score``'s default tokenizer.
"""

from __future__ import annotations

import re

# Pre-compile regexes that are used often.
NON_ALPHANUM_PATTERN = r"[^a-z0-9]+"
NON_ALPHANUM_RE = re.compile(NON_ALPHANUM_PATTERN)
SPACES_PATTERN = r"\s+"
SPACES_RE = re.compile(SPACES_PATTERN)
VALID_TOKEN_PATTERN = r"^[a-z0-9]+$"
VALID_TOKEN_RE = re.compile(VALID_TOKEN_PATTERN)


def _ensure_str(s):
    """Mirror ``six.ensure_str``: decode bytes as UTF-8 so byte inputs behave
    exactly like ``rouge_score`` (which wraps these call sites in six.ensure_str)
    instead of raising."""
    return s.decode("utf-8") if isinstance(s, bytes) else s


def tokenize(text, stemmer):
    """Tokenize input text into a list of tokens.

    This approach aims to replicate the approach taken by Chin-Yew Lin in the
    original ROUGE implementation (and matches ``rouge_score.tokenize.tokenize``).

    Args:
        text: A text blob to tokenize.
        stemmer: An optional stemmer (object exposing ``.stem(token) -> str``).

    Returns:
        A list of string tokens extracted from input text.
    """
    # Convert everything to lowercase.
    text = text.lower()
    # Replace any non-alpha-numeric characters with spaces.
    text = NON_ALPHANUM_RE.sub(" ", _ensure_str(text))

    tokens = SPACES_RE.split(text)
    if stemmer:
        # Only stem words more than 3 characters long.
        tokens = [_ensure_str(stemmer.stem(x)) if len(x) > 3 else x for x in tokens]

    # One final check to drop any empty or invalid tokens.
    tokens = [x for x in tokens if VALID_TOKEN_RE.match(x)]

    return tokens
