class BaseExtractor:
    def __init__(self):
        self.rules = []

    def extract(self, log_data):
        raise NotImplementedError("Subclasses should implement this method.")

    def load_rules(self, rules_source):
        raise NotImplementedError("Subclasses should implement this method.")