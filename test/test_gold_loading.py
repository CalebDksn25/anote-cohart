import json

def test_gold_file_loads():

    # Open the gold file and load it as JSON
    with open("data/sample_transcript.gold.json", "r") as f:
        data = json.load(f)

    # Check that the data has the expected values and structure
    assert "action_items" in data
    assert "decisions" in data
    assert "follow_ups" in data