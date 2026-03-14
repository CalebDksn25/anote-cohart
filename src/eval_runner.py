import json
from pathlib import Path
from typing import Any, Dict

from src.evaluator import evaluate
from src.llm_extractor import LLMExtractor


SECTION_NAMES = ("action_items", "decisions", "follow_ups")


def _load_text(path: str) -> str:
    return Path(path).read_text()


def _load_json(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text())


def _compute_overall_metrics(result: Dict[str, Any]) -> Dict[str, float]:
    matched = 0
    hallucinations = 0
    missed = 0

    for section_name in SECTION_NAMES:
        section = result[section_name]
        matched += len(section["matched"])
        hallucinations += len(section["hallucinations"])
        missed += len(section["missed"])

    precision = matched / (matched + hallucinations) if (matched + hallucinations) else 0.0
    recall = matched / (matched + missed) if (matched + missed) else 0.0

    return {
        "matched": matched,
        "hallucinations": hallucinations,
        "missed": missed,
        "precision": precision,
        "recall": recall,
    }


def run_evaluation(
    transcript_path: str,
    gold_path: str,
    text_threshold: float = 0.75,
    extractor: LLMExtractor | None = None,
) -> Dict[str, Any]:
    transcript = _load_text(transcript_path)
    if not transcript.strip():
        raise ValueError("Transcript file is empty.")

    gold = _load_json(gold_path)
    extractor = extractor or LLMExtractor()
    pred = extractor.extract(transcript)
    result = evaluate(pred, gold, text_threshold=text_threshold)
    result["overall"] = _compute_overall_metrics(result)
    result["transcript_path"] = str(Path(transcript_path))
    result["gold_path"] = str(Path(gold_path))
    return result


def _format_section(section_name: str, metrics: Dict[str, Any]) -> list[str]:
    title = section_name.replace("_", " ").title()
    lines = [
        title,
        "-" * len(title),
        f"precision: {metrics['precision']:.2f}",
        f"recall: {metrics['recall']:.2f}",
        f"matched: {len(metrics['matched'])}",
        f"hallucinations: {len(metrics['hallucinations'])}",
        f"missed: {len(metrics['missed'])}",
    ]
    if "owner_accuracy_on_matched" in metrics:
        lines.append(f"owner accuracy on matched: {metrics['owner_accuracy_on_matched']:.2f}")
    if "due_accuracy_on_matched" in metrics:
        lines.append(f"due accuracy on matched: {metrics['due_accuracy_on_matched']:.2f}")

    lines.extend(_format_match_details(metrics["matched"]))
    lines.extend(_format_hallucination_details(metrics["hallucinations"]))
    lines.extend(_format_missed_details(metrics["missed"]))
    return lines


def _format_item_summary(item: Dict[str, Any]) -> str:
    text = item.get("text", "<missing text>")
    owner = item.get("owner")
    due = item.get("due")

    parts = [f"text='{text}'"]
    if owner is not None:
        parts.append(f"owner='{owner}'")
    if due is not None:
        parts.append(f"due='{due}'")
    return ", ".join(parts)


def _format_match_details(matches: list[Dict[str, Any]]) -> list[str]:
    if not matches:
        return []

    lines = ["", "matched details:"]
    for match in matches:
        pred_summary = _format_item_summary(match["pred"])
        gold_summary = _format_item_summary(match["gold"])
        lines.append(f"- score={match['text_score']:.2f} pred[{pred_summary}]")
        lines.append(f"  gold[{gold_summary}]")
    return lines


def _format_hallucination_details(hallucinations: list[Dict[str, Any]]) -> list[str]:
    if not hallucinations:
        return []

    lines = ["", "hallucinations:"]
    for item in hallucinations:
        pred_summary = _format_item_summary(item["pred"])
        lines.append(f"- best_score={item['best_score']:.2f} pred[{pred_summary}]")
    return lines


def _format_missed_details(missed: list[Dict[str, Any]]) -> list[str]:
    if not missed:
        return []

    lines = ["", "missed gold items:"]
    for item in missed:
        lines.append(f"- gold[{_format_item_summary(item)}]")
    return lines


def format_evaluation_report(result: Dict[str, Any]) -> str:
    overall = result["overall"]
    lines = [
        "Evaluation Report",
        "=================",
        f"transcript: {result['transcript_path']}",
        f"gold: {result['gold_path']}",
        f"text threshold: {result['text_threshold']:.2f}",
        "",
        "Overall",
        "-------",
        f"precision: {overall['precision']:.2f}",
        f"recall: {overall['recall']:.2f}",
        f"matched: {overall['matched']}",
        f"hallucinations: {overall['hallucinations']}",
        f"missed: {overall['missed']}",
    ]

    for section_name in SECTION_NAMES:
        lines.append("")
        lines.extend(_format_section(section_name, result[section_name]))

    return "\n".join(lines)
