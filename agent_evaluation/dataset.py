class Dataset:
    def __init__(self, data, experiment_description):
        """
        Initializes a new Dataset instance.

        :param data: A list of tuples, each representing (gene/protein, property, value).
        :param experiment_description: A string describing the experiment.
        """
        self.data = data
        self.experiment_description = experiment_description
