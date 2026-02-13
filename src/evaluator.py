from typing import Dict, Any

def normalize_action_items(items):
    """
    Convert action items to comparable tuples of text.
    """

    # Normalize text by stripping whitespace and converting to lowercase
    normalized = []
    for item in items:
        normalized.append((
            item["text"].strip().lower(),
            item["owner"],
            item["due"]
        ))

    # Return the normalized list of tuples
    return normalized

def evaluate(pred: Dict[str, Any], gold: Dict[str, Any]):
    # Normalize the predicted and gold action items for comparison
    pred_items = normalize_action_items(pred["action_items"])
    gold_items = normalize_action_items(gold["action_items"])

    # Calculate true positives, false positives, and false negatives based on the normalized items
    true_positives = pred_items & gold_items
    false_positives = pred_items - gold_items
    false_negatives = gold_items - pred_items

    # Calculate precision and recall, handling division by zero
    precision = len(true_positives) / len(pred_items) if pred_items else 0
    recall = len(true_positives) / len(gold_items) if gold_items else 0

    #Return all the data
    return {
        "precision": precision,
        "recall": recall,
        "true_positives": list(true_positives),
        "false_positives": list(false_positives),
        "false_negatives": list(false_negatives)
    }

    