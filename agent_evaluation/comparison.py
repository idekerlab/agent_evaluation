class Comparison:
    def __init__(self, hypothesis_a, hypothesis_b, reviewer, 
                 factuality=None, 
                 novelty=None, 
                 significance=None, 
                 plausibility=None, 
                 logic=None, 
                 combined=None,
                 comment=""):
        """
        Initializes a new Comparison instance, representing the evaluation of two hypotheses.

        :param hypothesis_a: The first Hypothesis instance being compared.
        :param hypothesis_b: The second Hypothesis instance being compared.
        :param reviewer: The Reviewer instance that performed the comparison.
        :param factuality: A score or evaluation of the factuality of the comparison.
        :param novelty: A score or evaluation of the novelty.
        :param significance: A score or evaluation of the significance.
        :param plausibility: A score or evaluation of the plausibility.
        :param logic: A score or evaluation of the logical coherence.
        :param combined: A combined score or evaluation of the comparison.
        :param comment: Additional comments provided by the reviewer.
        """
        self.hypothesis_a = hypothesis_a
        self.hypothesis_b = hypothesis_b
        self.reviewer = reviewer
        self.factuality = factuality
        self.novelty = novelty
        self.significance = significance
        self.plausibility = plausibility
        self.logic = logic
        self.combined = combined
        self.comment = comment
