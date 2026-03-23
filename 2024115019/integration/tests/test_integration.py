"""
Integration Test Suite for StreetRace Manager.
Validates each module individually and then cross-module interactions
as illustrated in the Call Graph.

Run from: 2024115019/integration/
  pytest tests/
"""
import pytest
from code.registration import Registration
from code.crew_management import CrewManagement
from code.inventory import Inventory
from code.race_management import RaceManagement
from code.results import Results
from code.mission_planning import MissionPlanning
from code.sponsorship import Sponsorship
from code.garage import Garage


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Registration module — individual verification
# ─────────────────────────────────────────────────────────────────────────────

def test_register_member_success():
    """Registration: registering a new member stores name and role correctly."""
    reg = Registration()
    member = reg.register_member("Alice", "driver")
    assert member.name == "Alice"
    assert member.role == "driver"

def test_register_duplicate_member_raises():
    """Registration: re-registering the same name raises ValueError."""
    reg = Registration()
    reg.register_member("Eve", "driver")
    with pytest.raises(ValueError):
        reg.register_member("Eve", "mechanic")

def test_get_registered_member():
    """Registration: get_member returns the correct member object."""
    reg = Registration()
    reg.register_member("Bob", "mechanic")
    member = reg.get_member("Bob")
    assert member is not None
    assert member.role == "mechanic"

def test_get_unregistered_member_returns_none():
    """Registration: get_member returns None for an unknown member name."""
    reg = Registration()
    assert reg.get_member("Ghost") is None

def test_register_multiple_roles():
    """Registration: different members can hold different roles."""
    reg = Registration()
    reg.register_member("Alice", "driver")
    reg.register_member("Bob", "mechanic")
    reg.register_member("Carol", "strategist")
    assert reg.get_member("Alice").role == "driver"
    assert reg.get_member("Bob").role == "mechanic"
    assert reg.get_member("Carol").role == "strategist"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: CrewManagement module — individual verification
# ─────────────────────────────────────────────────────────────────────────────

def test_assign_role_to_registered_member():
    """CrewManagement: role update propagates back to the Registration store."""
    reg = Registration()
    crew = CrewManagement(reg)
    reg.register_member("Charlie", "driver")
    crew.assign_role("Charlie", "mechanic")
    assert reg.get_member("Charlie").role == "mechanic"

def test_assign_role_to_unregistered_member_raises():
    """CrewManagement: assigning a role to an unknown member raises ValueError."""
    reg = Registration()
    crew = CrewManagement(reg)
    with pytest.raises(ValueError):
        crew.assign_role("Dana", "mechanic")

def test_set_and_get_skill():
    """CrewManagement: skill levels for a member are stored and retrieved correctly."""
    reg = Registration()
    crew = CrewManagement(reg)
    reg.register_member("Alice", "driver")
    crew.set_skill("Alice", "driving", 9)
    assert crew.get_skills("Alice")["driving"] == 9

def test_get_skills_unknown_member_returns_empty():
    """CrewManagement: get_skills returns empty dict for unknown member."""
    reg = Registration()
    crew = CrewManagement(reg)
    assert crew.get_skills("Nobody") == {}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Inventory module — individual verification
# ─────────────────────────────────────────────────────────────────────────────

def test_add_car_to_inventory():
    """Inventory: added car appears in the cars list."""
    inv = Inventory()
    inv.add_car("Car1")
    assert "Car1" in inv.cars

def test_inventory_cash_starts_at_zero():
    """Inventory: initial cash balance is 0."""
    inv = Inventory()
    assert inv.cash == 0

def test_inventory_add_parts_and_tools():
    """Inventory: parts and tools can be added and retrieved."""
    inv = Inventory()
    inv.add_part("Brake Pad")
    inv.add_tool("Wrench")
    assert "Brake Pad" in inv.parts
    assert "Wrench" in inv.tools

def test_inventory_cash_update():
    """Inventory: update_cash correctly increments the cash balance."""
    inv = Inventory()
    inv.update_cash(500)
    inv.update_cash(300)
    assert inv.cash == 800


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: RaceManagement — cross-module (Registration + Inventory)
# Requirement: Only registered drivers with valid cars may race.
# ─────────────────────────────────────────────────────────────────────────────

def test_registering_a_driver_and_entering_a_race():
    """
    Scenario: Register a driver then enter them into a race.
    Modules: Registration → Inventory → RaceManagement
    Expected: Race object created with correct driver name and car.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    reg.register_member("Alice", "driver")
    inv.add_car("Car1")
    race = race_mgmt.create_race("Grand Prix", "Alice", "Car1")
    assert race.driver.name == "Alice"
    assert race.car == "Car1"

def test_attempting_race_without_registered_driver():
    """
    Scenario: Attempt to enter an unregistered person into a race.
    Modules: Registration → RaceManagement
    Expected: ValueError is raised — no unregistered drivers allowed.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    inv.add_car("Car1")
    with pytest.raises(ValueError):
        race_mgmt.create_race("Grand Prix", "UnknownDriver", "Car1")

def test_create_race_with_non_driver_role_raises():
    """
    Scenario: A registered mechanic tries to enter a race.
    Modules: Registration → RaceManagement
    Expected: ValueError — only driver-role members may race.
    Error 1 (Integration): race_management lacked role check; fixed.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    reg.register_member("Frank", "mechanic")
    inv.add_car("Car1")
    with pytest.raises(ValueError):
        race_mgmt.create_race("Grand Prix", "Frank", "Car1")

def test_create_race_with_car_not_in_inventory():
    """
    Scenario: Driver tries to race with a car not in the inventory.
    Modules: Registration → Inventory → RaceManagement
    Expected: ValueError — car must exist in inventory.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    reg.register_member("Grace", "driver")
    with pytest.raises(ValueError):
        race_mgmt.create_race("Grand Prix", "Grace", "CarX")

def test_multiple_drivers_can_enter_separate_races():
    """
    Scenario: Two drivers each enter separate races independently.
    Modules: Registration → Inventory → RaceManagement
    Expected: Two distinct Race objects created correctly.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    reg.register_member("Alice", "driver")
    reg.register_member("Bob", "driver")
    inv.add_car("Car1")
    inv.add_car("Car2")
    race1 = race_mgmt.create_race("Race1", "Alice", "Car1")
    race2 = race_mgmt.create_race("Race2", "Bob", "Car2")
    assert race1.driver.name == "Alice"
    assert race2.driver.name == "Bob"
    assert len(race_mgmt.races) == 2


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Results module — cross-module (Results + Inventory)
# Requirement: Race results must update cash balance in Inventory.
# ─────────────────────────────────────────────────────────────────────────────

def test_completing_race_updates_inventory_cash():
    """
    Scenario: Complete a race and verify prize money flows to inventory.
    Modules: RaceManagement → Results → Inventory
    Expected: inventory.cash increases by the prize amount.
    Error 2 (Integration): results.py omitted inventory.update_cash(); fixed.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    results = Results(inv)
    reg.register_member("Alice", "driver")
    inv.add_car("Car1")
    race = race_mgmt.create_race("Grand Prix", "Alice", "Car1")
    results.record_result(race, "Alice", 1000)
    assert inv.cash == 1000

def test_multiple_race_results_accumulate_cash():
    """
    Scenario: Two consecutive race wins by same driver.
    Modules: RaceManagement → Results → Inventory
    Expected: cash sums both prizes (500 + 300 = 800).
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    results = Results(inv)
    reg.register_member("Alice", "driver")
    inv.add_car("Car1")
    race1 = race_mgmt.create_race("Race1", "Alice", "Car1")
    results.record_result(race1, "Alice", 500)
    race2 = race_mgmt.create_race("Race2", "Alice", "Car1")
    results.record_result(race2, "Alice", 300)
    assert inv.cash == 800

def test_results_tracks_rankings():
    """
    Scenario: Recording results updates the rankings dictionary.
    Modules: Results
    Expected: winner's win count increments correctly.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    results = Results(inv)
    reg.register_member("Alice", "driver")
    inv.add_car("Car1")
    race1 = race_mgmt.create_race("R1", "Alice", "Car1")
    race2 = race_mgmt.create_race("R2", "Alice", "Car1")
    results.record_result(race1, "Alice", 100)
    results.record_result(race2, "Alice", 100)
    assert results.rankings["Alice"] == 2

def test_results_history_records_all_races():
    """
    Scenario: Race history log contains all recorded results.
    Modules: Results
    Expected: history list has correct number of entries.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    results = Results(inv)
    reg.register_member("Alice", "driver")
    inv.add_car("Car1")
    for i in range(3):
        race = race_mgmt.create_race(f"Race{i}", "Alice", "Car1")
        results.record_result(race, "Alice", 100)
    assert len(results.history) == 3


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: MissionPlanning — cross-module (Registration + MissionPlanning)
# Requirement: Missions cannot start if required roles are unavailable.
# ─────────────────────────────────────────────────────────────────────────────

def test_assigning_mission_with_correct_role():
    """
    Scenario: Assign a mission when a crew member with the required role exists.
    Modules: Registration → MissionPlanning
    Expected: mission.assigned == True.
    """
    reg = Registration()
    mp = MissionPlanning(reg)
    reg.register_member("Bob", "mechanic")
    mission = mp.assign_mission("Repair Car1", ["mechanic"])
    assert mission.assigned is True

def test_assigning_mission_without_required_role_raises():
    """
    Scenario: Assign a mission when no crew member has the required role.
    Modules: Registration → MissionPlanning
    Expected: ValueError raised — cannot start mission.
    """
    reg = Registration()
    mp = MissionPlanning(reg)
    with pytest.raises(ValueError):
        mp.assign_mission("Repair Car1", ["mechanic"])

def test_mission_fails_when_wrong_role_present():
    """
    Scenario: A driver exists but the mission needs a mechanic.
    Modules: Registration → MissionPlanning
    Expected: ValueError — wrong role cannot fulfil requirement.
    """
    reg = Registration()
    mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")
    with pytest.raises(ValueError):
        mp.assign_mission("Repair Car1", ["mechanic"])

def test_mission_requiring_multiple_roles():
    """
    Scenario: Mission needs both a driver and a mechanic.
    Modules: Registration → MissionPlanning
    Expected: succeeds when both roles exist in crew.
    """
    reg = Registration()
    mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")
    reg.register_member("Bob", "mechanic")
    mission = mp.assign_mission("Rescue Run", ["driver", "mechanic"])
    assert mission.assigned is True

def test_mission_multi_role_fails_if_one_missing():
    """
    Scenario: Multi-role mission when only one role is present.
    Modules: Registration → MissionPlanning
    Expected: ValueError — partially fulfilled mission must not start.
    """
    reg = Registration()
    mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")
    with pytest.raises(ValueError):
        mp.assign_mission("Rescue Run", ["driver", "mechanic"])


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: Garage module — cross-module (Garage + Inventory)
# Requirement: Damaged car repair requires mechanic and valid car in inventory.
# ─────────────────────────────────────────────────────────────────────────────

def test_repair_car_in_inventory():
    """
    Scenario: Garage repairs a car that exists in inventory.
    Modules: Inventory → Garage
    Expected: repair_car returns success string.
    """
    inv = Inventory()
    garage = Garage(inv)
    inv.add_car("Car1")
    result = garage.repair_car("Car1")
    assert result == "Car1 repaired"

def test_repair_car_not_in_inventory_raises():
    """
    Scenario: Garage tries to repair a car not in inventory.
    Modules: Inventory → Garage
    Expected: ValueError — cannot repair a non-existent car.
    """
    inv = Inventory()
    garage = Garage(inv)
    with pytest.raises(ValueError):
        garage.repair_car("CarX")

def test_repair_adds_to_repair_log():
    """
    Scenario: Each repaired car is logged in the garage repair history.
    Modules: Inventory → Garage
    Expected: garage.repairs list grows on each repair.
    """
    inv = Inventory()
    garage = Garage(inv)
    inv.add_car("Car1")
    inv.add_car("Car2")
    garage.repair_car("Car1")
    garage.repair_car("Car2")
    assert "Car1" in garage.repairs
    assert "Car2" in garage.repairs


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: Sponsorship module — individual verification
# ─────────────────────────────────────────────────────────────────────────────

def test_add_sponsor_and_total_funds():
    """Sponsorship: total_funds sums all sponsor contributions."""
    sp = Sponsorship()
    sp.add_sponsor("SpeedyOil", 5000)
    sp.add_sponsor("TurboFuel", 3000)
    assert sp.total_funds() == 8000

def test_sponsorship_starts_at_zero():
    """Sponsorship: initial total is 0."""
    sp = Sponsorship()
    assert sp.total_funds() == 0

def test_sponsor_overwrite():
    """Sponsorship: adding same sponsor again overwrites previous amount."""
    sp = Sponsorship()
    sp.add_sponsor("SpeedyOil", 5000)
    sp.add_sponsor("SpeedyOil", 7000)
    assert sp.total_funds() == 7000


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9: Full end-to-end multi-module scenarios
# ─────────────────────────────────────────────────────────────────────────────

def test_full_workflow_all_modules():
    """
    Scenario: Complete workflow: register crew, race, record results,
              assign mission, repair car, add sponsor.
    Modules: ALL (Registration, CrewManagement, Inventory, RaceManagement,
             Results, MissionPlanning, Garage, Sponsorship)
    Expected: all steps succeed, cash and sponsorship updated correctly.
    """
    reg = Registration()
    crew = CrewManagement(reg)
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    results = Results(inv)
    mp = MissionPlanning(reg)
    sp = Sponsorship()
    garage = Garage(inv)

    reg.register_member("Alice", "driver")
    reg.register_member("Bob", "mechanic")
    crew.assign_role("Bob", "mechanic")
    crew.set_skill("Alice", "driving", 10)
    inv.add_car("Car1")
    inv.add_part("Brake Pad")

    race = race_mgmt.create_race("Championship", "Alice", "Car1")
    results.record_result(race, "Alice", 2000)
    mission = mp.assign_mission("Repair Car1", ["mechanic"])
    repair = garage.repair_car("Car1")
    sp.add_sponsor("BigSponsor", 10000)

    assert inv.cash == 2000
    assert mission.assigned is True
    assert repair == "Car1 repaired"
    assert sp.total_funds() == 10000
    assert results.rankings["Alice"] == 1

def test_sponsor_and_race_funds_are_independent():
    """
    Scenario: Sponsorship funds and race prize money track separately.
    Modules: Sponsorship, Results, Inventory
    Expected: inv.cash reflects only prizes; sp.total_funds reflects only sponsors.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    results = Results(inv)
    sp = Sponsorship()
    reg.register_member("Alice", "driver")
    inv.add_car("Car1")
    race = race_mgmt.create_race("SponsorRace", "Alice", "Car1")
    results.record_result(race, "Alice", 500)
    sp.add_sponsor("SponsorA", 1500)
    assert inv.cash == 500
    assert sp.total_funds() == 1500

def test_role_restrictions_driver_and_mechanic():
    """
    Scenario: Drivers race; mechanics fix cars — wrong roles are rejected.
    Modules: Registration, RaceManagement, MissionPlanning
    Expected: Bob (driver) races; Alice (mechanic) cannot race but can do repair mission.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    mp = MissionPlanning(reg)
    reg.register_member("Alice", "mechanic")
    reg.register_member("Bob", "driver")
    inv.add_car("Car1")
    race = race_mgmt.create_race("Race1", "Bob", "Car1")
    assert race.driver.name == "Bob"
    with pytest.raises(ValueError):
        race_mgmt.create_race("Race2", "Alice", "Car1")
    mission = mp.assign_mission("Repair Car1", ["mechanic"])
    assert mission.assigned is True

def test_damaged_car_mission_requires_mechanic():
    """
    Scenario: After a race, car is damaged; repair mission checks mechanic availability.
    Modules: Registration, RaceManagement, Results, MissionPlanning, Garage, Inventory
    Expected: If mechanic available, mission assigned and car repaired.
              If no mechanic, mission raises ValueError.
    """
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    results = Results(inv)
    mp = MissionPlanning(reg)
    garage = Garage(inv)

    reg.register_member("Alice", "driver")
    reg.register_member("Bob", "mechanic")
    inv.add_car("Car1")

    # Race completes, car may need repair
    race = race_mgmt.create_race("NightRace", "Alice", "Car1")
    results.record_result(race, "Alice", 800)

    # Mission requires mechanic — Bob is available
    mission = mp.assign_mission("Fix Car1 damage", ["mechanic"])
    assert mission.assigned is True
    repair = garage.repair_car("Car1")
    assert repair == "Car1 repaired"

    # Now scenario without mechanic
    reg2 = Registration()
    mp2 = MissionPlanning(reg2)
    reg2.register_member("Dave", "driver")
    with pytest.raises(ValueError):
        mp2.assign_mission("Fix Car1 damage", ["mechanic"])

def test_crew_role_change_affects_mission_eligibility():
    """
    Scenario: A driver's role is changed to mechanic; they can now fulfil mechanic missions.
    Modules: Registration → CrewManagement → MissionPlanning
    Expected: After role change, member satisfies mechanic mission requirement.
    """
    reg = Registration()
    crew = CrewManagement(reg)
    mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")

    # Alice is a driver — mechanic mission should fail
    with pytest.raises(ValueError):
        mp.assign_mission("Fix car", ["mechanic"])

    # Change role to mechanic
    crew.assign_role("Alice", "mechanic")
    mission = mp.assign_mission("Fix car", ["mechanic"])
    assert mission.assigned is True

def test_duplicate_car_addition_allowed_but_noted():
    """
    Scenario: Adding the same car twice to inventory.
    Modules: Inventory
    Expected: Both entries exist — known design behavior documented in report.
    """
    inv = Inventory()
    inv.add_car("Car1")
    inv.add_car("Car1")
    assert inv.cars.count("Car1") == 2
