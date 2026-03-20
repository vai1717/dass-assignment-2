class Sponsorship:
    def __init__(self):
        self.sponsors = {}

    def add_sponsor(self, name, amount):
        self.sponsors[name] = amount

    def total_funds(self):
        return sum(self.sponsors.values())
