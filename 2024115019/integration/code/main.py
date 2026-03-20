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
    race = RaceManagement(crew, inventory)
    results = Results(race, inventory)
    missions = MissionPlanning(crew, garage=None)  # Garage to be injected if needed
    sponsorship = Sponsorship()
    garage = Garage()

    # Example: Register a crew member
    member_id = registration.register_member("Alice")
    crew.assign_role(member_id, "driver")

    # Example: Enter a race
    if crew.is_driver(member_id):
        race.enter_race(member_id, car_id=1)

    # Example: Race result updates inventory
    results.update_after_race(race_id=1, winner_id=member_id)

    # Example: Mission requiring mechanic
    if crew.has_available_role("mechanic"):
        missions.start_mission("Repair Car", required_role="mechanic")

    # Example: Sponsorship
    sponsorship.apply_for_sponsorship(team_id=1)

    # Example: Garage
    garage.repair_car(car_id=1)

if __name__ == "__main__":
    main()
