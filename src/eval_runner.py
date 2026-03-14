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
