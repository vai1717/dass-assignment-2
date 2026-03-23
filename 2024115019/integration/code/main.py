# Entry point for StreetRace Manager integration
# This will be filled in after all modules are implemented and tested
"""
Main entry point for the StreetRace Manager system.
Handles high-level coordination and enforces business rules.
"""


from registration import Registration
from crew_management import CrewManagement
from inventory import Inventory
from race_management import RaceManagement
from results import Results
from mission_planning import MissionPlanning
from sponsorship import Sponsorship
from garage import Garage


def main():
    # Initialize modules

    registration = Registration()
    crew = CrewManagement(registration)
    inventory = Inventory()
    race_management = RaceManagement(registration, inventory)
    results = Results(inventory)
    missions = MissionPlanning(registration)
    sponsorship = Sponsorship()
    garage = Garage(inventory)

    # Register crew members
    registration.register_member("Alice", "driver")
    registration.register_member("Bob", "mechanic")

    # Assign skills
    crew.set_skill("Alice", "driving", 5)
    crew.set_skill("Bob", "repair", 5)

    # Add cars to inventory
    inventory.add_car("Car1")
    inventory.add_car("Car2")

    # Create a race
    race = race_management.create_race("Grand Prix", "Alice", "Car1")

    # Record race result
    results.record_result(race, "Alice", 1000)

    # Assign a mission requiring a mechanic
    missions.assign_mission("Repair Car1", ["mechanic"])

    # Repair a car
    garage.repair_car("Car1")

    # Add a sponsor
    sponsorship.add_sponsor("SpeedyOil", 5000)

if __name__ == "__main__":
    # For call graph generation, wrap main in pycallgraph2 if available
    try:
        from pycallgraph2 import PyCallGraph
        from pycallgraph2.output import GraphvizOutput
        graphviz = GraphvizOutput()
        graphviz.output_file = 'callgraph.png'
        with PyCallGraph(output=graphviz):
            main()
    except ImportError:
        main()
