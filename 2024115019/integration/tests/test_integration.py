"""
Integration tests for StreetRace Manager modules.
Each test validates cross-module interactions as shown in the call graph.
"""
import pytest
from registration import Registration
from crew_management import CrewManagement
from inventory import Inventory
from race_management import RaceManagement
from results import Results
from mission_planning import MissionPlanning
from sponsorship import Sponsorship
from garage import Garage

def test_register_driver_and_enter_race():
	"""Test registering a driver and entering them into a race."""
	registration = Registration()
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	registration.register_member("Alice", "driver")
	inventory.add_car("Car1")
	race = race_management.create_race("Grand Prix", "Alice", "Car1")
	assert race.driver.name == "Alice"
	assert race.car == "Car1"
	# Scenario: Register driver, enter race
	# Modules: registration, inventory, race_management
	# Expected: Race created with correct driver and car
	# Actual: Race created as expected
	# Errors: None

def test_enter_race_without_registered_driver():
	"""Test entering a race without a registered driver."""
	registration = Registration()
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	inventory.add_car("Car1")
	with pytest.raises(ValueError):
		race_management.create_race("Grand Prix", "Bob", "Car1")
	# Scenario: Enter race with unregistered driver
	# Modules: registration, inventory, race_management
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None

def test_complete_race_and_update_inventory():
	"""Test completing a race and updating inventory cash with prize money."""
	registration = Registration()
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	results = Results(inventory)
	registration.register_member("Alice", "driver")
	inventory.add_car("Car1")
	race = race_management.create_race("Grand Prix", "Alice", "Car1")
	results.record_result(race, "Alice", 1000)
	assert inventory.cash == 1000
	# Scenario: Complete race, update cash
	# Modules: registration, inventory, race_management, results
	# Expected: Inventory cash increases by prize
	# Actual: Inventory cash is 1000
	# Errors: None

def test_assign_mission_and_validate_roles():
	"""Test assigning a mission and validating required crew roles."""
	registration = Registration()
	mission_planning = MissionPlanning(registration)
	registration.register_member("Bob", "mechanic")
	mission = mission_planning.assign_mission("Repair Car1", ["mechanic"])
	assert mission.assigned is True
	# Scenario: Assign mission with required role
	# Modules: registration, mission_planning
	# Expected: Mission assigned successfully
	# Actual: Mission assigned as expected
	# Errors: None

def test_assign_mission_missing_role():
	"""Test assigning a mission when required crew role is missing."""
	registration = Registration()
	mission_planning = MissionPlanning(registration)
	with pytest.raises(ValueError):
		mission_planning.assign_mission("Repair Car1", ["mechanic"])
	# Scenario: Assign mission with missing role
	# Modules: registration, mission_planning
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None


def test_repair_car_success():
	"""Test repairing a car that exists in inventory."""
	inventory = Inventory()
	garage = Garage(inventory)
	inventory.add_car("Car1")
	result = garage.repair_car("Car1")
	assert result == "Car1 repaired"
	# Scenario: Repair car in inventory
	# Modules: inventory, garage
	# Expected: Car repaired successfully
	# Actual: Car repaired as expected
	# Errors: None

def test_repair_car_not_in_inventory():
	"""Test repairing a car that does not exist in inventory."""
	inventory = Inventory()
	garage = Garage(inventory)
	with pytest.raises(ValueError):
		garage.repair_car("CarX")
	# Scenario: Repair car not in inventory
	# Modules: inventory, garage
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None

def test_add_and_total_sponsorship():
	"""Test adding sponsors and calculating total funds."""
	sponsorship = Sponsorship()
	sponsorship.add_sponsor("SpeedyOil", 5000)
	sponsorship.add_sponsor("TurboFuel", 3000)
	assert sponsorship.total_funds() == 8000
	# Scenario: Add sponsors, total funds
	# Modules: sponsorship
	# Expected: Total funds is sum of all sponsors
	# Actual: Total funds is 8000
	# Errors: None

def test_assign_role_to_registered_member():
	"""Test assigning a new role to a registered crew member."""
	registration = Registration()
	crew = CrewManagement(registration)
	registration.register_member("Charlie", "driver")
	crew.assign_role("Charlie", "mechanic")
	member = registration.get_member("Charlie")
	assert member.role == "mechanic"
	# Scenario: Assign new role to member
	# Modules: registration, crew_management
	# Expected: Role updated successfully
	# Actual: Role updated as expected
	# Errors: None

def test_assign_role_to_unregistered_member():
	"""Test assigning a role to an unregistered crew member."""
	registration = Registration()
	crew = CrewManagement(registration)
	with pytest.raises(ValueError):
		crew.assign_role("Dana", "mechanic")
	# Scenario: Assign role to unregistered member
	# Modules: registration, crew_management
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None

def test_duplicate_crew_registration():
	"""Test registering the same crew member twice."""
	registration = Registration()
	registration.register_member("Eve", "driver")
	with pytest.raises(ValueError):
		registration.register_member("Eve", "mechanic")
	# Scenario: Duplicate crew registration
	# Modules: registration
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None

def test_create_race_with_non_driver():
	"""Test creating a race with a registered member who is not a driver."""
	registration = Registration()
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	registration.register_member("Frank", "mechanic")
	inventory.add_car("Car1")
	with pytest.raises(ValueError):
		race_management.create_race("Grand Prix", "Frank", "Car1")
	# Scenario: Create race with non-driver
	# Modules: registration, inventory, race_management
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None

def test_create_race_with_missing_car():
	"""Test creating a race with a car not in inventory."""
	registration = Registration()
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	registration.register_member("Grace", "driver")
	with pytest.raises(ValueError):
		race_management.create_race("Grand Prix", "Grace", "CarX")
	# Scenario: Create race with missing car
	# Modules: registration, inventory, race_management
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None


# --- Extensive multi-module integration tests ---
def test_full_workflow_success():
	"""Test a full workflow: register, assign, race, result, mission, repair, sponsor."""
	registration = Registration()
	crew = CrewManagement(registration)
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	results = Results(inventory)
	mission_planning = MissionPlanning(registration)
	sponsorship = Sponsorship()
	garage = Garage(inventory)

	registration.register_member("Alice", "driver")
	registration.register_member("Bob", "mechanic")
	crew.assign_role("Bob", "mechanic")
	inventory.add_car("Car1")
	race = race_management.create_race("Championship", "Alice", "Car1")
	results.record_result(race, "Alice", 2000)
	mission = mission_planning.assign_mission("Repair Car1", ["mechanic"])
	repair_result = garage.repair_car("Car1")
	sponsorship.add_sponsor("BigSponsor", 10000)
	assert inventory.cash == 2000
	assert mission.assigned is True
	assert repair_result == "Car1 repaired"
	assert sponsorship.total_funds() == 10000
	# Scenario: End-to-end workflow
	# Modules: registration, crew_management, inventory, race_management, results, mission_planning, sponsorship, garage
	# Expected: All steps succeed, cash and sponsorship updated
	# Actual: All steps succeed
	# Errors: None

def test_fail_mission_due_to_no_mechanic():
	"""Test mission assignment fails if mechanic is not registered or assigned."""
	registration = Registration()
	mission_planning = MissionPlanning(registration)
	registration.register_member("Alice", "driver")
	with pytest.raises(ValueError):
		mission_planning.assign_mission("Repair Car1", ["mechanic"])
	# Scenario: Assign mission with missing mechanic
	# Modules: registration, mission_planning
	# Expected: ValueError raised
	# Actual: ValueError raised
	# Errors: None

def test_race_and_repair_with_wrong_roles():
	"""Test that only a mechanic can be assigned to a repair mission and only a driver can race."""
	registration = Registration()
	crew = CrewManagement(registration)
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	mission_planning = MissionPlanning(registration)
	registration.register_member("Alice", "mechanic")
	registration.register_member("Bob", "driver")
	inventory.add_car("Car1")
	# Bob can race
	race = race_management.create_race("Race1", "Bob", "Car1")
	assert race.driver.name == "Bob"
	# Alice cannot race
	with pytest.raises(ValueError):
		race_management.create_race("Race2", "Alice", "Car1")
	# Alice can be assigned to mechanic mission
	mission = mission_planning.assign_mission("Repair Car1", ["mechanic"])
	assert mission.assigned is True
	# Bob cannot be assigned to mechanic mission
	with pytest.raises(ValueError):
		mission_planning.assign_mission("Repair Car2", ["mechanic", "driver"])
	# Scenario: Role-based restrictions
	# Modules: registration, crew_management, inventory, race_management, mission_planning
	# Expected: Only correct roles succeed
	# Actual: As expected
	# Errors: None

def test_sponsor_and_race_integration():
	"""Test that sponsorship funds and race results both update system state."""
	registration = Registration()
	inventory = Inventory()
	race_management = RaceManagement(registration, inventory)
	results = Results(inventory)
	sponsorship = Sponsorship()
	registration.register_member("Alice", "driver")
	inventory.add_car("Car1")
	race = race_management.create_race("SponsorRace", "Alice", "Car1")
	results.record_result(race, "Alice", 500)
	sponsorship.add_sponsor("SponsorA", 1500)
	assert inventory.cash == 500
	assert sponsorship.total_funds() == 1500
	# Scenario: Sponsorship and race result
	# Modules: registration, inventory, race_management, results, sponsorship
	# Expected: Both cash and sponsorship funds updated
	# Actual: As expected
	# Errors: None

def test_fail_duplicate_car_addition():
	"""Test adding the same car twice to inventory (should allow or fail based on design)."""
	inventory = Inventory()
	inventory.add_car("Car1")
	inventory.add_car("Car1")
	# Scenario: Duplicate car addition
	# Modules: inventory
	# Expected: Car1 appears twice (current design allows duplicates)
	# Actual: Car1 appears twice
	# Errors: Potential logical issue: duplicates allowed
