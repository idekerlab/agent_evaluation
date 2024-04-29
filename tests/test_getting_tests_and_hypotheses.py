from app.ae import load_tests, load_hypotheses

def test_retrieve_tests():
    db = test_db()
    # Retrieve all tests from the standard test data 
    tests = load_tests(db)
    # tests should be a list
    assert isinstance(tests, list)
    # each element in tests should be a dictionary
    for test in tests:
        assert isinstance(test, dict)
        # the label of each test should start with "Test"
        assert test["label"].startswith("Test")
        # the test should have test_plan_id that is a string
        assert isinstance(test["test_plan_id"], str)
        # the test should have hypotheses_ids that is a list of strings
        assert isinstance(test["hypotheses_ids"], list)
        for hypothesis_id in test["hypotheses_ids"]:
            assert isinstance(hypothesis_id, str)


def test_retrieve_hypotheses():
    # Select a test ID from the test data
    test_id = test_data["tests"][0]["id"]
    
    # Retrieve hypotheses for the selected test
    hypotheses = load_hypotheses(test_id)
    
    # Assert that the retrieved hypotheses match the expected test data
    expected_hypotheses = [
        hypothesis
        for hypothesis in test_data["hypotheses"]
        if hypothesis["test_id"] == test_id
    ]
    assert len(hypotheses) == len(expected_hypotheses)
    for hypothesis in hypotheses:
        assert hypothesis in expected_hypotheses