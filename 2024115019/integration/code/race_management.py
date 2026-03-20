class Race:
    def __init__(self, name, driver, car):
        self.name = name
        self.driver = driver
        self.car = car
        self.completed = False

class RaceManagement:
    def __init__(self, registration, inventory):
        self.registration = registration
        self.inventory = inventory
        self.races = []

    def create_race(self, race_name, driver_name, car):
        member = self.registration.get_member(driver_name)
        if not member or member.role != "driver":
            raise ValueError("Driver not registered or not a driver")
        if car not in self.inventory.cars:
            raise ValueError("Car not in inventory")
        race = Race(race_name, member, car)
        self.races.append(race)
        return race
