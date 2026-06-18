# Copyright 2026 William Brach.
# Portions derived from google-research/rouge_score (Apache License 2.0).
"""Scoring data structures and aggregation, compatible with ``rouge_score.scoring``.

``Score`` and ``AggregateScore`` are the same namedtuples ``rouge_score`` exposes,
so existing code that does ``result["rougeL"].fmeasure`` keeps working unchanged.
``numpy`` is imported lazily inside :class:`BootstrapAggregator`, so the common
scoring path has zero third-party dependencies.
"""

from __future__ import annotations

import abc
import collections
from typing import Dict


class Score(collections.namedtuple("Score", ["precision", "recall", "fmeasure"])):
    """Tuple containing precision, recall, and f-measure values."""


class BaseScorer(object, metaclass=abc.ABCMeta):
    """Base class for Scorer objects."""

    @abc.abstractmethod
    def score(self, target: str, prediction: str) -> Dict[str, Score]:
        """Calculates score between the target and prediction.

        Args:
            target: Text containing the target (ground truth) text.
            prediction: Text containing the predicted text.

        Returns:
            A dict mapping each score_type (string) to a Score object.
        """


class AggregateScore(
    collections.namedtuple("AggregateScore", ["low", "mid", "high"])
):
    """Tuple containing confidence intervals for scores."""


class BootstrapAggregator(object):
    """Aggregates scores to provide confidence intervals.

    Sample usage::

        scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'])
        aggregator = BootstrapAggregator()
        aggregator.add_scores(scorer.score("one two three", "one two"))
        aggregator.add_scores(scorer.score("one two five six", "seven eight"))
        result = aggregator.aggregate()

    Requires ``numpy`` (install the ``aggregate`` extra).
    """

    def __init__(self, confidence_interval=0.95, n_samples=1000):
        """Initializes a BootstrapAggregator object.

        Args:
            confidence_interval: Confidence interval to compute on the mean as a
                decimal.
            n_samples: Number of samples to use for bootstrap resampling.

        Raises:
            ValueError: If an invalid argument is given.
        """
        if confidence_interval < 0 or confidence_interval > 1:
            raise ValueError("confidence_interval must be in range [0, 1]")
        if n_samples <= 0:
            raise ValueError("n_samples must be positive")

        self._n_samples = n_samples
        self._confidence_interval = confidence_interval
        self._scores = collections.defaultdict(list)

    def add_scores(self, scores):
        """Adds a sample for future aggregation.

        Args:
            scores: Dict mapping score_type strings to a namedtuple representing
                a score.
        """
        for score_type, score in scores.items():
            self._scores[score_type].append(score)

    def aggregate(self):
        """Aggregates scores previously added using add_scores.

        Returns:
            A dict mapping score_type to AggregateScore objects.
        """
        import numpy as np

        result = {}
        for score_type, scores in self._scores.items():
            # Stack scores into a 2-d matrix of (sample, measure).
            score_matrix = np.vstack(tuple(scores))
            # Percentiles are returned as (interval, measure).
            percentiles = self._bootstrap_resample(score_matrix)
            # Extract the three intervals (low, mid, high).
            intervals = tuple(
                (scores[0].__class__(*percentiles[j, :]) for j in range(3))
            )
            result[score_type] = AggregateScore(
                low=intervals[0], mid=intervals[1], high=intervals[2]
            )
        return result

    def _bootstrap_resample(self, matrix):
        """Performs bootstrap resampling on a matrix of scores.

        Args:
            matrix: A 2-d matrix of (sample, measure).

        Returns:
            A 2-d matrix of (bounds, measure): low (row 0), mid (row 1), high
            (row 2). Mid is always the mean; low and high are specified by
            ``self._confidence_interval``.
        """
        import numpy as np

        # Matrix of (bootstrap sample, measure).
        sample_mean = np.zeros((self._n_samples, matrix.shape[1]))
        for i in range(self._n_samples):
            sample_idx = np.random.choice(
                np.arange(matrix.shape[0]), size=matrix.shape[0]
            )
            sample = matrix[sample_idx, :]
            sample_mean[i, :] = np.mean(sample, axis=0)

        # Take percentiles on the estimate of the mean using bootstrap samples.
        percentile_delta = (1 - self._confidence_interval) / 2
        q = 100 * np.array([percentile_delta, 0.5, 1 - percentile_delta])
        return np.percentile(sample_mean, q, axis=0)


def fmeasure(precision, recall):
    """Computes f-measure given precision and recall values."""
    if precision + recall > 0:
        return 2 * precision * recall / (precision + recall)
    else:
        return 0.0
