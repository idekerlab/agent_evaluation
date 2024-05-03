from app.ae import load_tests, load_hypotheses

def test_retrieve_tests(test_db):
    # Retrieve all tests from the standard test data 
    tests = load_tests(test_db)
    # tests should be a list with at least one element
    assert isinstance(tests, list)
    assert len(tests) > 0
    # each element in tests should be a dictionary
    for test in tests:
        assert isinstance(test, dict)
        # the label of each test should start with "Test"
        assert test["label"].startswith("Test")
        # the test should have test_plan_id that is a string
        assert test["properties"] is not None
        assert isinstance(test["properties"], dict)
        assert isinstance(test["properties"]["test_plan_id"], str)
        # the test should have hypothesis_ids that is a list of strings
        assert isinstance(test["properties"]["hypothesis_ids"], list)
        for hypothesis_id in test["properties"]["hypothesis_ids"]:
            assert isinstance(hypothesis_id, str)


def test_retrieve_hypotheses(test_db):
    tests = load_tests(test_db)
    test = tests[0]
    test_id = test["id"]
    # Retrieve hypotheses for the selected test
    hypotheses = load_hypotheses(test_db, test_id)
    
    # Assert that the retrieved hypotheses are well formed
    for hypothesis in hypotheses:
        assert isinstance(hypothesis, dict)
        assert hypothesis["label"] == "Hypothesis"
        assert hypothesis["properties"] is not None
        assert isinstance(hypothesis["properties"], dict)
        assert isinstance(hypothesis["properties"]["analyst_id"], str)
        assert isinstance(hypothesis["properties"]["dataset_id"], str)
        assert isinstance(hypothesis["properties"]["hypothesis_text"], str)
