class Dataset:
    def __init__(self, genes_of_interest, data=None, experiment_description=None):
        """
        Initializes a new Dataset instance.

        :param data: A list of tuples, each representing (gene/protein, property, value).
        :param experiment_description: A string describing the experiment.
        """
        self.genes_of_interest = genes_of_interest
        self.data = data
        self.experiment_description = experiment_description
