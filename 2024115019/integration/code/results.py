class Results:
    def __init__(self, inventory):
        self.inventory = inventory
        self.rankings = {}
        self.history = []

    def record_result(self, race, winner_name, prize):
        self.rankings[winner_name] = self.rankings.get(winner_name, 0) + 1
        self.history.append((race.name, winner_name, prize))
        self.inventory.update_cash(prize)
