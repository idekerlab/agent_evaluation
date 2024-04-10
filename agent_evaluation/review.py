from datetime import datetime

class ReviewPlan:
    def __init__(self, test, reviewers):
        """
        Initializes a new ReviewPlan instance.

        :param test: A Test instance that will be reviewed.
        :param reviewers: A list of Reviewer instances.
        """
        self.test = test
        self.reviewers = reviewers

class Review:
    def __init__(self, review_plan):
        """
        Initializes a new Review instance.

        :param review_plan: A ReviewPlan instance specifying the review configuration.
        """
        self.review_plan = review_plan
        self.comparisons = []
        self.time = None

    def old_run(self, log_file=None):
        """
        Executes the review according to the review plan.
        """
        for reviewer in self.review_plan.reviewers:
            for hypothesis_a in self.review_plan.test.hypotheses:
                for hypothesis_b in self.review_plan.test.hypotheses:
                    if hypothesis_a != hypothesis_b and hypothesis_a.dataset == hypothesis_b.dataset:
                        print(f"Generating comparison by {reviewer.name}...")
                        comparison = reviewer.generate_comparison(hypothesis_a, 
                                                                  hypothesis_b, 
                                                                  hypothesis_a.dataset, 
                                                                  log_file)
                        self.comparisons.append(comparison) 
        self.time = datetime.now()

    def run(self, comparison_order='AB', reverse=False, log_file=None):
        """
        Executes the review according to the review plan.

        Parameters:
        - comparison_order: str, optional (default='Both')
            Controls the order of comparisons: 'AB', 'BA', or 'Both'.
        - reverse: bool, optional (default=False)
            Specifies whether hypotheses are reviewed in reverse order.
        - log_file: str, optional
            Path to a log file where the review log will be written.
        """
        hypotheses = self.review_plan.test.hypotheses
        if reverse:
            hypotheses = reversed(hypotheses)

        for reviewer in self.review_plan.reviewers:
            for i, hypothesis_a in enumerate(hypotheses):
                for hypothesis_b in (list(hypotheses)[i + 1:] if comparison_order != 'Both' else hypotheses):
                    if hypothesis_a != hypothesis_b and hypothesis_a.dataset == hypothesis_b.dataset:
                        # Perform A-B comparison
                        if comparison_order in ('AB', 'Both'):
                            print(f"Generating A-B comparison by {reviewer.name}...")
                            comparison = reviewer.generate_comparison(hypothesis_a, hypothesis_b, hypothesis_a.dataset, log_file)
                            self.comparisons.append(comparison)
                        # Perform B-A comparison if needed
                        if comparison_order in ('BA', 'Both'):
                            print(f"Generating B-A comparison by {reviewer.name}...")
                            comparison = reviewer.generate_comparison(hypothesis_b, hypothesis_a, hypothesis_a.dataset, log_file)
                            self.comparisons.append(comparison)
        self.time = datetime.now()
