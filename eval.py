#!/usr/bin/env python3
import argparse

from src.eval_runner import format_evaluation_report, run_evaluation


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run extraction against a labeled transcript and report evaluation metrics."
    )
    parser.add_argument("transcript_path", help="Path to the transcript text file.")
    parser.add_argument("gold_path", help="Path to the gold JSON file.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Minimum text similarity threshold for a match. Defaults to 0.75.",
    )
    args = parser.parse_args()

    result = run_evaluation(
        transcript_path=args.transcript_path,
        gold_path=args.gold_path,
        text_threshold=args.threshold,
    )
    print(format_evaluation_report(result))


if __name__ == "__main__":
    main()
