# anote-cohart

`anote-cohart` is a meeting-to-action extraction prototype. It takes a meeting transcript and turns it into structured output with:

- action items
- decisions
- follow-ups
- owners when explicitly stated
- deadlines when explicitly stated
- review flags when details are vague or ambiguous

The current `v1` focus is transcript -> structured output plus lightweight evaluation. Automatically sending follow-ups, scheduling meetings, or executing tasks is intentionally out of scope for now.

## Submission-ready summary

This repository is ready to demo as a focused `v1` because it can:

- extract structured meeting outputs from a transcript
- capture `action_items`, `decisions`, and `follow_ups`
- assign owners and deadlines when explicitly stated
- flag ambiguous details for human review
- evaluate extraction quality against labeled gold data

## Current status

The project currently supports:

- LLM-based extraction from plain-text meeting transcripts
- strict schema validation on model output with automatic retry on invalid responses
- relative due date normalization when the transcript includes a `Date:` header
- ambiguity handling for vague due dates such as `next week` or `ASAP`
- section-level evaluation for `action_items`, `decisions`, and `follow_ups`
- an evaluation CLI for comparing extracted output against labeled gold data

## Repository layout

```text
main.py                  CLI for transcript -> structured meeting notes
eval.py                  CLI for transcript -> extraction -> evaluation report
src/
  llm_extractor.py       extraction pipeline, schema validation, retry logic
  date_normalizer.py     relative date parsing and ambiguity handling
  evaluator.py           token-F1 matching and section scoring
  eval_runner.py         end-to-end evaluation runner and report formatter
lib/
  openai_client.py       OpenAI API wrapper
  prompts.py             extraction prompt
data/
  sample_transcript_1.txt
  sample_transcript.gold.json
  sample_transcript_*.txt
test/
  test_*.py
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from the example and add your OpenAI API key:

```bash
cp .env.example .env
```

Then set:

```bash
OPENAI_API_KEY=sk-...
```

## Quick demo

If you only need the shortest path for a final presentation, run these three commands:

```bash
python main.py data/sample_transcript_1.txt
python eval.py data/sample_transcript_1.txt data/sample_transcript.gold.json
pytest -q
```

That demonstrates:

- extraction
- evaluation
- passing tests

## Run extraction

Use `main.py` to turn a transcript into a readable task list:

```bash
python main.py data/sample_transcript_1.txt
```

Example output:

```text
Action Items
============
[ ] Update the onboarding screens and share mocks (Priya) - due 2026-01-23
[ ] Investigate caching strategies and provide a recommendation (Jordan) - due 2026-01-28
[ ] Finish the customer feedback summary and send it out (Priya) - due 2026-01-26
[ ] Schedule a follow-up meeting once onboarding mocks are ready (Sam) - needs review

Decisions
=========
- Assign investigation of caching strategies to Jordan
- Park looping in design for the new dashboard for now

Follow-ups
==========
- Hold a follow-up meeting after onboarding mocks are ready (Sam)
```

## Transcript expectations

The extractor works on plain-text transcripts. Relative due dates are normalized only when the transcript includes a meeting date header in this format:

```text
Date: Jan 22, 2026
```

Example transcript shape:

```text
Meeting: Weekly Product Sync
Date: Jan 22, 2026
Attendees: Alex, Priya, Jordan, Sam

Alex: Let's get started.
Priya: I'll update the onboarding screens by Friday.
```

If no `Date:` header is present, extraction still runs, but relative dates will not be resolved into ISO dates.

## Run evaluation

Use `eval.py` to compare extracted output against a labeled gold file:

```bash
python eval.py data/sample_transcript_1.txt data/sample_transcript.gold.json
```

You can also tune the match threshold:

```bash
python eval.py data/sample_transcript_1.txt data/sample_transcript.gold.json --threshold 0.8
```

The evaluation report includes:

- overall precision and recall
- per-section precision and recall
- hallucination counts
- missed-item counts
- owner and due accuracy on matched `action_items` and `follow_ups`
- matched, hallucinated, and missed item details for debugging

## Evaluation metric

The evaluator uses token-based `F1` similarity over extracted text fields:

- strings are lowercased and tokenized
- overlap is computed as bag-of-words token overlap
- each predicted item is matched to the best unused gold item
- a match only counts if the similarity is at least the configured threshold

This scoring is applied separately to:

- `action_items`
- `decisions`
- `follow_ups`

## Testing

Run the full test suite with:

```bash
pytest -q
```

The test suite currently covers:

- due-date normalization
- token similarity scoring
- evaluator behavior
- extractor schema validation and retry behavior
- evaluation runner/report formatting

## Known limitations

This is still a focused `v1`. It does not yet:

- ask clarifying questions when owners or deadlines are missing
- ingest transcripts directly from Zoom or Google Meet APIs
- output JSON from the CLI
- execute follow-up actions such as drafting emails or scheduling meetings

## Presentation framing

If you need a concise way to describe the project in a demo:

- `Problem:` meetings create next steps that are easy to lose
- `Approach:` use an LLM to extract structured outputs from transcripts, then score the results against labeled data
- `What works now:` extraction, ambiguity flagging, and evaluation
- `What comes next:` clarification questions and downstream automation

## Suggested next steps

The most valuable next improvements are:

1. add a clarification loop for vague or missing details
2. expand the labeled transcript dataset
3. add machine-friendly JSON output for downstream integrations
4. improve transcript ingestion beyond local `.txt` files
