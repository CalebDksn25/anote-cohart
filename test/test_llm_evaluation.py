import json
from src.llm_extractor import LLMExtractor
from src.evaluator import evaluate

def test_llm_against_gold():
    # Load the extractor
    extractor = LLMExtractor()

    # Open the sample transcript
    with open("data/sample_transcript_1.txt", "r") as f:
        transcript = f.read()
    
    # Open the gold file and load it as JSON
    with open("data/sample_transcript.gold.json", "r") as f:
        gold = json.load(f)

    # Extract structured information from the transcript using the LLM
    pred = extractor.extract(transcript)

    # Evaluate the predicted output against the gold standard and print the results
    results = evaluate(pred, gold)
    print("Results:", results)

    # Assert that the precision and recall are above a certain threshold
    assert results["recall"] > 0.3