"""Common evaluation metrics."""

from __future__ import annotations

from typing import Any


def accuracy(predictions: list[Any], targets: list[Any]) -> float:
    """Calculate accuracy.

    Args:
        predictions: List of predictions
        targets: List of ground truth targets

    Returns:
        Accuracy score (0-1)
    """
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have same length")

    if not predictions:
        return 0.0

    correct = sum(p == t for p, t in zip(predictions, targets))
    return correct / len(predictions)


def precision_recall_f1(
    predictions: list[Any], targets: list[Any], positive_label: Any = 1
) -> tuple[float, float, float]:
    """Calculate precision, recall, and F1 score.

    Args:
        predictions: List of predictions
        targets: List of ground truth targets
        positive_label: Label to consider as positive

    Returns:
        Tuple of (precision, recall, f1)
    """
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have same length")

    tp = sum(
        1 for p, t in zip(predictions, targets) if p == positive_label and t == positive_label
    )
    fp = sum(
        1 for p, t in zip(predictions, targets) if p == positive_label and t != positive_label
    )
    fn = sum(
        1 for p, t in zip(predictions, targets) if p != positive_label and t == positive_label
    )

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def exact_match(predictions: list[str], targets: list[str]) -> float:
    """Calculate exact match ratio.

    Args:
        predictions: List of predicted strings
        targets: List of target strings

    Returns:
        Exact match score (0-1)
    """
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have same length")

    if not predictions:
        return 0.0

    matches = sum(p.strip() == t.strip() for p, t in zip(predictions, targets))
    return matches / len(predictions)


def bleu_score(prediction: str, reference: str, n: int = 4) -> float:
    """Calculate simple BLEU score (n-gram overlap).

    Args:
        prediction: Predicted text
        reference: Reference text
        n: Maximum n-gram size

    Returns:
        BLEU score (0-1)
    """
    from collections import Counter

    def get_ngrams(tokens: list[str], n: int) -> Counter:
        """Extract n-grams from tokens."""
        ngrams = Counter()
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i : i + n])
            ngrams[ngram] += 1
        return ngrams

    pred_tokens = prediction.lower().split()
    ref_tokens = reference.lower().split()

    if not pred_tokens or not ref_tokens:
        return 0.0

    scores = []
    for i in range(1, min(n + 1, len(pred_tokens) + 1)):
        pred_ngrams = get_ngrams(pred_tokens, i)
        ref_ngrams = get_ngrams(ref_tokens, i)

        if not pred_ngrams:
            continue

        overlap = sum(min(pred_ngrams[ng], ref_ngrams[ng]) for ng in pred_ngrams)
        score = overlap / sum(pred_ngrams.values())
        scores.append(score)

    if not scores:
        return 0.0

    # Geometric mean
    import math

    return math.exp(sum(math.log(s) if s > 0 else float("-inf") for s in scores) / len(scores))


def mean_reciprocal_rank(predictions: list[list[Any]], targets: list[Any]) -> float:
    """Calculate Mean Reciprocal Rank (MRR).

    Args:
        predictions: List of ranked prediction lists
        targets: List of target values

    Returns:
        MRR score
    """
    if len(predictions) != len(targets):
        raise ValueError("Predictions and targets must have same length")

    if not predictions:
        return 0.0

    rr_sum = 0.0
    for pred_list, target in zip(predictions, targets):
        for rank, pred in enumerate(pred_list, start=1):
            if pred == target:
                rr_sum += 1.0 / rank
                break

    return rr_sum / len(predictions)


__all__ = [
    "accuracy",
    "precision_recall_f1",
    "exact_match",
    "bleu_score",
    "mean_reciprocal_rank",
]
