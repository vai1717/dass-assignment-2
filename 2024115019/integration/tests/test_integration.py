"""
Integration Test Suite for StreetRace Manager.
Validates cross-module interactions as shown in the call graph.
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
# SECTION 1: Registration module
# ─────────────────────────────────────────────────────────────────────────────

def test_register_member_success():
    """Registration: registering a new member works and stores name/role."""
    reg = Registration()
    member = reg.register_member("Alice", "driver")
    assert member.name == "Alice"
    assert member.role == "driver"

def test_register_duplicate_member_raises():
    """Registration: registering same name twice raises ValueError."""
    reg = Registration()
    reg.register_member("Eve", "driver")
    with pytest.raises(ValueError):
        reg.register_member("Eve", "mechanic")

def test_get_registered_member():
    """Registration: get_member returns the correct member after registration."""
    reg = Registration()
    reg.register_member("Bob", "mechanic")
    member = reg.get_member("Bob")
    assert member is not None
    assert member.role == "mechanic"

def test_get_unregistered_member_returns_none():
    """Registration: get_member returns None for unknown name."""
    reg = Registration()
    assert reg.get_member("Ghost") is None


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: CrewManagement module
# ─────────────────────────────────────────────────────────────────────────────

def test_assign_role_to_registered_member():
    """CrewManagement: role can be updated for a registered member."""
    reg = Registration()
    crew = CrewManagement(reg)
    reg.register_member("Charlie", "driver")
    crew.assign_role("Charlie", "mechanic")
    assert reg.get_member("Charlie").role == "mechanic"

def test_assign_role_to_unregistered_member_raises():
    """CrewManagement: assigning role to unknown member raises ValueError."""
    reg = Registration()
    crew = CrewManagement(reg)
    with pytest.raises(ValueError):
        crew.assign_role("Dana", "mechanic")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Inventory module
# ─────────────────────────────────────────────────────────────────────────────

def test_add_car_to_inventory():
    """Inventory: added car appears in cars list."""
    inv = Inventory()
    inv.add_car("Car1")
    assert "Car1" in inv.cars

def test_inventory_cash_starts_at_zero():
    """Inventory: initial cash balance is 0."""
    inv = Inventory()
    assert inv.cash == 0


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: RaceManagement module (cross-module)
# ─────────────────────────────────────────────────────────────────────────────

def test_register_driver_and_enter_race():
    """Registration → RaceManagement: registered driver can enter race with valid car."""
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    reg.register_member("Alice", "driver")
    inv.add_car("Car1")
    race = race_mgmt.create_race("Grand Prix", "Alice", "Car1")
    assert race.driver.name == "Alice"
    assert race.car == "Car1"

def test_enter_race_without_registered_driver_raises():
    """RaceManagement: unregistered driver raises ValueError."""
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    inv.add_car("Car1")
    with pytest.raises(ValueError):
        race_mgmt.create_race("Grand Prix", "Bob", "Car1")

def test_create_race_with_non_driver_raises():
    """RaceManagement: only members with role=driver may race."""
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    reg.register_member("Frank", "mechanic")
    inv.add_car("Car1")
    with pytest.raises(ValueError):
        race_mgmt.create_race("Grand Prix", "Frank", "Car1")

def test_create_race_with_missing_car_raises():
    """RaceManagement: car not in inventory raises ValueError."""
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    reg.register_member("Grace", "driver")
    with pytest.raises(ValueError):
        race_mgmt.create_race("Grand Prix", "Grace", "CarX")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Results module (cross-module)
# ─────────────────────────────────────────────────────────────────────────────

def test_complete_race_updates_inventory_cash():
    """Results → Inventory: prize money is added to inventory cash."""
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
    """Results: running two races accumulates cash in inventory."""
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


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: MissionPlanning module (cross-module)
# ─────────────────────────────────────────────────────────────────────────────

def test_assign_mission_with_required_role():
    """MissionPlanning → Registration: mission assigned when required role present."""
    reg = Registration()
    mp = MissionPlanning(reg)
    reg.register_member("Bob", "mechanic")
    mission = mp.assign_mission("Repair Car1", ["mechanic"])
    assert mission.assigned is True

def test_assign_mission_missing_role_raises():
    """MissionPlanning: raises ValueError when required role is absent."""
    reg = Registration()
    mp = MissionPlanning(reg)
    with pytest.raises(ValueError):
        mp.assign_mission("Repair Car1", ["mechanic"])

def test_mission_fails_when_only_wrong_role_present():
    """MissionPlanning: driver present but mechanic needed → ValueError."""
    reg = Registration()
    mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")
    with pytest.raises(ValueError):
        mp.assign_mission("Repair Car1", ["mechanic"])


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: Garage module (cross-module with Inventory)
# ─────────────────────────────────────────────────────────────────────────────

def test_repair_car_in_inventory():
    """Garage → Inventory: car in inventory can be repaired."""
    inv = Inventory()
    garage = Garage(inv)
    inv.add_car("Car1")
    result = garage.repair_car("Car1")
    assert result == "Car1 repaired"

def test_repair_car_not_in_inventory_raises():
    """Garage → Inventory: car not in inventory raises ValueError."""
    inv = Inventory()
    garage = Garage(inv)
    with pytest.raises(ValueError):
        garage.repair_car("CarX")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: Sponsorship module
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


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9: Multi-module end-to-end scenarios
# ─────────────────────────────────────────────────────────────────────────────

def test_full_workflow_success():
    """End-to-end: all modules interact correctly in a full race workflow."""
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
    inv.add_car("Car1")
    race = race_mgmt.create_race("Championship", "Alice", "Car1")
    results.record_result(race, "Alice", 2000)
    mission = mp.assign_mission("Repair Car1", ["mechanic"])
    repair_result = garage.repair_car("Car1")
    sp.add_sponsor("BigSponsor", 10000)

    assert inv.cash == 2000
    assert mission.assigned is True
    assert repair_result == "Car1 repaired"
    assert sp.total_funds() == 10000

def test_sponsor_and_race_funds_are_independent():
    """Sponsorship funds and prize money are tracked separately."""
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

def test_race_and_repair_role_restrictions():
    """Only drivers race; only mechanics fix cars — wrong roles rejected."""
    reg = Registration()
    inv = Inventory()
    race_mgmt = RaceManagement(reg, inv)
    mp = MissionPlanning(reg)
    reg.register_member("Alice", "mechanic")
    reg.register_member("Bob", "driver")
    inv.add_car("Car1")
    # Bob (driver) can race
    race = race_mgmt.create_race("Race1", "Bob", "Car1")
    assert race.driver.name == "Bob"
    # Alice (mechanic) cannot race
    with pytest.raises(ValueError):
        race_mgmt.create_race("Race2", "Alice", "Car1")
    # Alice can be assigned to mechanic mission
    mission = mp.assign_mission("Repair Car1", ["mechanic"])
    assert mission.assigned is True

def test_duplicate_car_addition_allowed_but_noted():
    """Inventory: duplicate car addition is currently allowed (design decision)."""
    inv = Inventory()
    inv.add_car("Car1")
    inv.add_car("Car1")
    # Both entries exist — this is a known design issue logged in the report
    assert inv.cars.count("Car1") == 2
