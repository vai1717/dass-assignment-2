class Garage:
    def __init__(self, inventory):
        self.inventory = inventory
        self.repairs = []

    def repair_car(self, car):
        if car not in self.inventory.cars:
            raise ValueError("Car not in inventory")
        self.repairs.append(car)
        return f"{car} repaired"
