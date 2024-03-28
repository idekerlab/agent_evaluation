from datetime import datetime

class TestPlan:
    def __init__(self, datasets, analysts):
        """
        Initializes a new TestPlan instance.

        :param datasets: A list of Dataset instances.
        :param analysts: A list of Analyst instances.
        """
        self.datasets = datasets
        self.analysts = analysts

class Test:
    def __init__(self, test_plan):
        """
        Initializes a new Test instance.

        :param test_plan: A TestPlan instance specifying the test configuration.
        """
        self.test_plan = test_plan
        self.hypotheses = []
        self.end_time = None

    def run(self, log_file=None):
        """
        Executes the test according to the test plan.
        """
        for dataset in self.test_plan.datasets:
            for analyst in self.test_plan.analysts:
                print(f"Generating hypothesis by {analyst.name} on {dataset.data}")
                hypothesis = analyst.generate_hypothesis(dataset, log_file)
                self.hypotheses.append(hypothesis)

        self.end_time = datetime.now()



