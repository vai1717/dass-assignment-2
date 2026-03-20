class Inventory:
    def __init__(self):
        self.cars = []
        self.parts = []
        self.tools = []
        self.cash = 0

    def add_car(self, car):
        self.cars.append(car)

    def add_part(self, part):
        self.parts.append(part)

    def add_tool(self, tool):
        self.tools.append(tool)

    def update_cash(self, amount):
        self.cash += amount
