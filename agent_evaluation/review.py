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

    def run(self, log_file=None):
        """
        Executes the review according to the review plan.
        """
        for reviewer in self.review_plan.reviewers:
            for hypothesis_a in self.review_plan.test.hypotheses:
                for hypothesis_b in self.review_plan.test.hypotheses:
                    if hypothesis_a != hypothesis_b and hypothesis_a.dataset == hypothesis_b.dataset:
                        comparison = reviewer.generate_comparison(hypothesis_a, 
                                                                  hypothesis_b, 
                                                                  hypothesis_a.dataset, 
                                                                  log_file)
                        self.comparisons.append(comparison) 
        self.time = datetime.now()
