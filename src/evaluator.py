from typing import Any, Dict, List, Tuple, Optional
from collections import Counter
import re


# TODO: Explore different evailation matrics

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


def evaluate(pred: Dict[str, Any], gold: Dict[str, Any], text_threshold: float = 0.75):
    """
    Matches predicted action items to gold action items by text similarity.
    Then scores owner and due agreement for matched items.
    """

    pred_items = pred.get("action_items", [])
    gold_items = gold.get("action_items", [])

    used_gold = set()

    matches = []
    hallucinations = []
    missed = []

    owner_correct = 0
    due_correct = 0

    # For each predicted item, find the best matching gold item based on text similarity, while ensuring that each gold item can only be matched once (using used_gold to track which gold items have already been matched).
    for p in pred_items:

        # Find the index of the best matching gold item for the current predicted item, along with the similarity score. The best_text_match function is called with the predicted text, the list of gold items, and the set of used gold indices to ensure that each gold item is only matched once.
        gi, score = best_text_match(p["text"], gold_items, used_gold)

        # If no matching gold item is found (gi is None) or if the similarity score is below the specified text_threshold, consider the predicted item as a hallucination (i.e., an incorrect prediction that does not correspond to any gold item). In this case, add the predicted item and its best score to the hallucinations list and continue to the next predicted item without further evaluation.
        if gi is None or score < text_threshold:
            hallucinations.append({"pred": p, "best_score": score})
            continue

        # If a matching gold item is found and the similarity score meets the threshold, add the index of the matched gold item to the used_gold set to ensure it won't be matched again. Then, retrieve the matched gold item using its index and add a dictionary containing both the predicted item and the matched gold item, along with the text similarity score, to the matches list for further evaluation of owner and due agreement.
        used_gold.add(gi)
        g = gold_items[gi]
        matches.append({"pred": p, "gold": g, "text_score": score})

        # Check if the owner field in the predicted item matches the owner field in the matched gold item. If they match, increment the owner_correct counter by 1.
        if p.get("owner") == g.get("owner"):
            owner_correct += 1
        if p.get("due") == g.get("due"):
            due_correct += 1

    # After processing all predicted items, iterate through the gold items to find any gold items that were not matched with any predicted items (i.e., those whose indices are not in the used_gold set). For each unmatched gold item, add it to the missed list as an item that was missed by the predictions.
    for i, g in enumerate(gold_items):
        if i not in used_gold:
            missed.append(g)

    # Calculate true positives (tp) as the number of matches, false positives (fp) as the number of hallucinations, and false negatives (fn) as the number of missed items. Then compute precision as tp / (tp + fp) and recall as tp / (tp + fn), handling the case where the denominators could be zero to avoid division errors. Finally, calculate owner accuracy and due accuracy for the matched items and return a dictionary containing all the evaluation metrics and details.
    tp = len(matches)
    fp = len(hallucinations)
    fn = len(missed)

    # Calculate precision and recall, ensuring that division by zero is handled gracefully by returning 0.0 when the denominator is zero.
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    # Calculate owner accuracy and due accuracy for the matched items, which is the number of correct owner/due matches divided by the total number of true positives (matches). Again, handle the case where tp could be zero to avoid division errors.
    owner_acc = owner_correct / tp if tp else 0.0
    due_acc = due_correct / tp if tp else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "matched": matches,
        "hallucinations": hallucinations,
        "missed": missed,
        "owner_accuracy_on_matched": owner_acc,
        "due_accuracy_on_matched": due_acc,
        "text_threshold": text_threshold,
    }