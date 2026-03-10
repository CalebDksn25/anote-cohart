# anote-cohart

A CLI tool that extracts structured meeting notes from raw transcripts using an LLM. Given a transcript file, it identifies action items, decisions, and follow-ups — with owners, due dates, and evidence quotes.

## What it does

- **Extracts** action items, decisions, and follow-up items from meeting transcripts
- **Normalizes** relative due dates (e.g. "by Friday", "next Wednesday") into ISO dates using the meeting date as a reference
- **Flags** ambiguous due phrases (e.g. "ASAP", "next week") for human review
- **Validates** LLM output against a strict JSON schema, with up to 3 retry attempts on failure
- **Evaluates** extraction quality against gold-standard annotations using token-based F1 scoring

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv pytest
```

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

## Usage

```bash
python main.py <transcript_file>
```

**Example:**

```bash
python main.py data/sample_transcript_1.txt
```

**Output:**

```
Action Items
============
[ ] Update the onboarding screens and share mocks (Priya) — due 2026-01-23
[ ] Investigate caching strategies and provide a recommendation (Jordan) — due 2026-01-28
[ ] Finish the customer feedback summary and send it out (Priya) — due 2026-01-26
[ ] Schedule a follow-up meeting once onboarding mocks are ready (Sam) — ⚠ needs review

Decisions
=========
- Assign investigation of caching strategies to Jordan
- Park looping in design for the new dashboard for now

Follow-ups
==========
- Hold a follow-up meeting after onboarding mocks are ready (Sam)
```

## Transcript format

The tool looks for a `Date:` header to anchor relative due dates:

```
Meeting: Weekly Product Sync
Date: Jan 22, 2026
Attendees: Alex, Priya, Jordan, Sam

Alex: Let's get started...
```

Without a `Date:` header, due dates are still extracted as raw phrases but not normalized to ISO format.

## Project structure

```
main.py              # CLI entrypoint and output formatter
src/
  llm_extractor.py   # LLM call, schema validation, date normalization orchestration
  date_normalizer.py # Converts relative due phrases to ISO dates
  evaluator.py       # Evaluates predictions against gold annotations (token F1)
lib/
  openai_client.py   # OpenAI API wrapper (gpt-4o-mini, temperature=0)
  prompts.py         # System prompt for extraction
data/
  sample_transcript_1.txt      # Example meeting transcript
  sample_transcript.gold.json  # Gold-standard annotations for evaluation
test/
  test_llm_extractor.py
  test_date_normalizer.py
  test_token_similarity.py
  test_gold_loading.py
```

## Running tests

```bash
pytest
```
