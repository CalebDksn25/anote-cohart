from typing import Any, Dict, List, Tuple, Optional
from collections import Counter
import re

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def _f1_over_tokens(a: str, b: str) -> float:
    """
    Compute token-based F1 between two strings.
    Uses a bag-of-words tokenization and counts overlap.
    """
    a_tokens = _tokenize(a)
    b_tokens = _tokenize(b)

    if not a_tokens and not b_tokens:
        return 1.0
    if not a_tokens or not b_tokens:
        return 0.0

    a_counts = Counter(a_tokens)
    b_counts = Counter(b_tokens)
    overlap = sum((a_counts & b_counts).values())
    if overlap == 0:
        return 0.0

    precision = overlap / sum(a_counts.values())
    recall = overlap / sum(b_counts.values())
    return (2 * precision * recall) / (precision + recall)


def text_sim(a: str, b: str) -> float:
    """
    Compute a similarity score between two strings using token-based F1.
    """
    return _f1_over_tokens(a, b)


def best_text_match(
    pred_text: str,
    gold_items: List[Dict[str, Any]],
    used_gold_idxs: set,
) -> Tuple[Optional[int], float]:
    """
Find the index of the gold item with the highest text similarity to the predicted text, excluding any gold items that have already been matched (as indicated by used_gold_idxs).
Returns a tuple of (best_index, best_score), where best_index is the index of the best matching gold item
    """

    best_idx = None
    best_score = 0.0
    # Iterate through the gold items and compute the text similarity score for each one that hasn't been used yet
    for i, g in enumerate(gold_items):

        # Skip any gold items that have already been matched
        if i in used_gold_idxs:
            continue

        # Compute the text similarity score between the predicted text and the current gold item's text
        score = text_sim(pred_text, g["text"])

        # If the computed score is better than the best score found so far, update best_idx and best_score
        if score > best_score:
            best_score = score
            best_idx = i
    
    return best_idx, best_score


def _score_section(
    pred_items: List[Dict[str, Any]],
    gold_items: List[Dict[str, Any]],
    text_threshold: float,
    score_owner_due: bool = False,
) -> Dict[str, Any]:
    """
    Generic precision/recall scoring for a list of predicted vs gold items.
    If score_owner_due is True, also tracks owner and due accuracy on matched items.
    """
    used_gold: set = set()
    matches = []
    hallucinations = []
    owner_correct = 0
    due_correct = 0

    for p in pred_items:
        gi, score = best_text_match(p["text"], gold_items, used_gold)
        if gi is None or score < text_threshold:
            hallucinations.append({"pred": p, "best_score": score})
            continue
        used_gold.add(gi)
        g = gold_items[gi]
        matches.append({"pred": p, "gold": g, "text_score": score})
        if score_owner_due:
            if p.get("owner") == g.get("owner"):
                owner_correct += 1
            if p.get("due") == g.get("due"):
                due_correct += 1

    missed = [g for i, g in enumerate(gold_items) if i not in used_gold]

    tp = len(matches)
    fp = len(hallucinations)
    fn = len(missed)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    result = {
        "precision": precision,
        "recall": recall,
        "matched": matches,
        "hallucinations": hallucinations,
        "missed": missed,
        "text_threshold": text_threshold,
    }
    if score_owner_due:
        result["owner_accuracy_on_matched"] = owner_correct / tp if tp else 0.0
        result["due_accuracy_on_matched"] = due_correct / tp if tp else 0.0
    return result


def evaluate(pred: Dict[str, Any], gold: Dict[str, Any], text_threshold: float = 0.75):
    """
    Scores predicted action items, decisions, and follow-ups against gold data
    using token-F1 text matching. Reports precision, recall, and (for action
    items and follow-ups) owner/due accuracy on matched items.
    """
    action_items = _score_section(
        pred.get("action_items", []),
        gold.get("action_items", []),
        text_threshold,
        score_owner_due=True,
    )
    decisions = _score_section(
        pred.get("decisions", []),
        gold.get("decisions", []),
        text_threshold,
        score_owner_due=False,
    )
    follow_ups = _score_section(
        pred.get("follow_ups", []),
        gold.get("follow_ups", []),
        text_threshold,
        score_owner_due=True,
    )

    return {
        "action_items": action_items,
        "decisions": decisions,
        "follow_ups": follow_ups,
        "text_threshold": text_threshold,
    }