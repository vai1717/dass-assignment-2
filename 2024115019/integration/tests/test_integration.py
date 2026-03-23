"""
Comprehensive Integration Test Suite for StreetRace Manager — 55 Tests.
Tests individual module correctness AND all cross-module interactions.

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
# SECTION 1: Registration — 9 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_register_member_success():
    reg = Registration()
    m = reg.register_member("Alice", "driver")
    assert m.name == "Alice" and m.role == "driver"

def test_register_duplicate_raises():
    reg = Registration()
    reg.register_member("Eve", "driver")
    with pytest.raises(ValueError):
        reg.register_member("Eve", "mechanic")

def test_get_registered_member():
    reg = Registration()
    reg.register_member("Bob", "mechanic")
    assert reg.get_member("Bob").role == "mechanic"

def test_get_unregistered_returns_none():
    reg = Registration()
    assert reg.get_member("Ghost") is None

def test_multiple_members_different_roles():
    reg = Registration()
    reg.register_member("A", "driver")
    reg.register_member("B", "mechanic")
    reg.register_member("C", "strategist")
    assert reg.get_member("A").role == "driver"
    assert reg.get_member("B").role == "mechanic"
    assert reg.get_member("C").role == "strategist"

def test_register_and_retrieve_all_members():
    reg = Registration()
    names = ["X", "Y", "Z"]
    for n in names:
        reg.register_member(n, "driver")
    for n in names:
        assert reg.get_member(n) is not None

def test_register_member_name_stored():
    reg = Registration()
    m = reg.register_member("Carol", "strategist")
    assert m.name == "Carol"

def test_register_member_role_stored():
    reg = Registration()
    m = reg.register_member("Dave", "mechanic")
    assert m.role == "mechanic"

def test_registration_members_dict_populated():
    reg = Registration()
    reg.register_member("Alice", "driver")
    assert "Alice" in reg.members


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: CrewManagement — 7 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_assign_role_updates_registration():
    reg = Registration(); crew = CrewManagement(reg)
    reg.register_member("Charlie", "driver")
    crew.assign_role("Charlie", "mechanic")
    assert reg.get_member("Charlie").role == "mechanic"

def test_assign_role_unregistered_raises():
    reg = Registration(); crew = CrewManagement(reg)
    with pytest.raises(ValueError):
        crew.assign_role("Dana", "mechanic")

def test_set_and_get_skill():
    reg = Registration(); crew = CrewManagement(reg)
    reg.register_member("Alice", "driver")
    crew.set_skill("Alice", "speed", 9)
    assert crew.get_skills("Alice")["speed"] == 9

def test_multiple_skills_stored():
    reg = Registration(); crew = CrewManagement(reg)
    reg.register_member("Alice", "driver")
    crew.set_skill("Alice", "speed", 9)
    crew.set_skill("Alice", "control", 7)
    skills = crew.get_skills("Alice")
    assert skills["speed"] == 9 and skills["control"] == 7

def test_get_skills_unknown_returns_empty():
    reg = Registration(); crew = CrewManagement(reg)
    assert crew.get_skills("Nobody") == {}

def test_assign_role_then_check():
    reg = Registration(); crew = CrewManagement(reg)
    reg.register_member("Frank", "driver")
    crew.assign_role("Frank", "strategist")
    assert reg.get_member("Frank").role == "strategist"

def test_skills_for_two_members_independent():
    reg = Registration(); crew = CrewManagement(reg)
    reg.register_member("A", "driver"); reg.register_member("B", "mechanic")
    crew.set_skill("A", "speed", 10); crew.set_skill("B", "speed", 5)
    assert crew.get_skills("A")["speed"] == 10
    assert crew.get_skills("B")["speed"] == 5


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Inventory — 6 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_add_car():
    inv = Inventory(); inv.add_car("Car1")
    assert "Car1" in inv.cars

def test_cash_starts_zero():
    inv = Inventory()
    assert inv.cash == 0

def test_add_parts_and_tools():
    inv = Inventory()
    inv.add_part("Brake Pad"); inv.add_tool("Wrench")
    assert "Brake Pad" in inv.parts and "Wrench" in inv.tools

def test_update_cash_accumulates():
    inv = Inventory()
    inv.update_cash(300); inv.update_cash(200)
    assert inv.cash == 500

def test_multiple_cars():
    inv = Inventory()
    for i in range(5):
        inv.add_car(f"Car{i}")
    assert len(inv.cars) == 5

def test_duplicate_car_added_twice():
    inv = Inventory(); inv.add_car("X"); inv.add_car("X")
    assert inv.cars.count("X") == 2


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: RaceManagement cross-module (Registration + Inventory) — 7 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_register_driver_then_enter_race():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    race = rm.create_race("Grand Prix", "Alice", "Car1")
    assert race.driver.name == "Alice" and race.car == "Car1"

def test_race_without_registered_driver_raises():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    inv.add_car("Car1")
    with pytest.raises(ValueError):
        rm.create_race("GP", "Unknown", "Car1")

def test_non_driver_role_cannot_race():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    reg.register_member("Frank", "mechanic"); inv.add_car("Car1")
    with pytest.raises(ValueError):
        rm.create_race("GP", "Frank", "Car1")

def test_race_car_not_in_inventory_raises():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    reg.register_member("Grace", "driver")
    with pytest.raises(ValueError):
        rm.create_race("GP", "Grace", "Phantom")

def test_multiple_drivers_separate_races():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    reg.register_member("A", "driver"); reg.register_member("B", "driver")
    inv.add_car("C1"); inv.add_car("C2")
    r1 = rm.create_race("R1", "A", "C1"); r2 = rm.create_race("R2", "B", "C2")
    assert r1.driver.name == "A" and r2.driver.name == "B"
    assert len(rm.races) == 2

def test_race_stored_in_race_list():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    rm.create_race("GP", "Alice", "Car1")
    assert len(rm.races) == 1

def test_race_completed_flag_starts_false():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    race = rm.create_race("GP", "Alice", "Car1")
    assert race.completed is False


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Results cross-module (Results + Inventory) — 7 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_complete_race_updates_cash():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    race = rm.create_race("GP", "Alice", "Car1")
    res.record_result(race, "Alice", 1000)
    assert inv.cash == 1000

def test_two_races_accumulate_cash():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    r1 = rm.create_race("R1", "Alice", "Car1"); res.record_result(r1, "Alice", 500)
    r2 = rm.create_race("R2", "Alice", "Car1"); res.record_result(r2, "Alice", 300)
    assert inv.cash == 800

def test_results_rankings_tracked():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    r1 = rm.create_race("R1", "Alice", "Car1"); res.record_result(r1, "Alice", 100)
    r2 = rm.create_race("R2", "Alice", "Car1"); res.record_result(r2, "Alice", 100)
    assert res.rankings["Alice"] == 2

def test_results_history_length():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    for i in range(4):
        race = rm.create_race(f"Race{i}", "Alice", "Car1")
        res.record_result(race, "Alice", 50)
    assert len(res.history) == 4

def test_two_drivers_independent_rankings():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); reg.register_member("Bob", "driver")
    inv.add_car("C1"); inv.add_car("C2")
    r1 = rm.create_race("R1", "Alice", "C1"); res.record_result(r1, "Alice", 100)
    r2 = rm.create_race("R2", "Bob", "C2"); res.record_result(r2, "Bob", 200)
    assert res.rankings["Alice"] == 1 and res.rankings.get("Bob", 0) == 1

def test_zero_prize_does_not_change_cash():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    race = rm.create_race("GP", "Alice", "Car1"); res.record_result(race, "Alice", 0)
    assert inv.cash == 0

def test_results_history_stores_correct_data():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    race = rm.create_race("ChampionRace", "Alice", "Car1")
    res.record_result(race, "Alice", 999)
    assert res.history[0] == ("ChampionRace", "Alice", 999)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: MissionPlanning cross-module (Registration + Mission) — 8 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_mission_with_correct_role():
    reg = Registration(); mp = MissionPlanning(reg)
    reg.register_member("Bob", "mechanic")
    mission = mp.assign_mission("Fix Car", ["mechanic"])
    assert mission.assigned is True

def test_mission_no_required_role_raises():
    reg = Registration(); mp = MissionPlanning(reg)
    with pytest.raises(ValueError):
        mp.assign_mission("Fix Car", ["mechanic"])

def test_mission_wrong_role_raises():
    reg = Registration(); mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")
    with pytest.raises(ValueError):
        mp.assign_mission("Fix Car", ["mechanic"])

def test_mission_multi_role_success():
    reg = Registration(); mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver"); reg.register_member("Bob", "mechanic")
    mission = mp.assign_mission("Rescue Run", ["driver", "mechanic"])
    assert mission.assigned is True

def test_mission_multi_role_one_missing():
    reg = Registration(); mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")
    with pytest.raises(ValueError):
        mp.assign_mission("Rescue Run", ["driver", "mechanic"])

def test_mission_stored_in_list():
    reg = Registration(); mp = MissionPlanning(reg)
    reg.register_member("Bob", "mechanic")
    mp.assign_mission("Fix Car", ["mechanic"])
    assert len(mp.missions) == 1

def test_mission_name_stored():
    reg = Registration(); mp = MissionPlanning(reg)
    reg.register_member("Bob", "mechanic")
    m = mp.assign_mission("Secret Delivery", ["mechanic"])
    assert m.name == "Secret Delivery"

def test_mission_requires_strategist():
    reg = Registration(); mp = MissionPlanning(reg)
    reg.register_member("Carol", "strategist")
    mission = mp.assign_mission("Plan Route", ["strategist"])
    assert mission.assigned is True


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: Garage cross-module (Inventory + Garage) — 5 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_repair_car_in_inventory():
    inv = Inventory(); garage = Garage(inv)
    inv.add_car("Car1")
    assert garage.repair_car("Car1") == "Car1 repaired"

def test_repair_car_not_in_inventory_raises():
    inv = Inventory(); garage = Garage(inv)
    with pytest.raises(ValueError):
        garage.repair_car("CarX")

def test_repair_log_populated():
    inv = Inventory(); garage = Garage(inv)
    inv.add_car("Car1"); inv.add_car("Car2")
    garage.repair_car("Car1"); garage.repair_car("Car2")
    assert "Car1" in garage.repairs and "Car2" in garage.repairs

def test_multiple_repairs_tracked():
    inv = Inventory(); garage = Garage(inv)
    inv.add_car("Car1")
    garage.repair_car("Car1"); garage.repair_car("Car1")
    assert len(garage.repairs) == 2

def test_repair_empty_inventory_raises():
    inv = Inventory(); garage = Garage(inv)
    with pytest.raises(ValueError):
        garage.repair_car("Car1")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: Sponsorship — 4 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_add_and_sum_sponsors():
    sp = Sponsorship()
    sp.add_sponsor("A", 5000); sp.add_sponsor("B", 3000)
    assert sp.total_funds() == 8000

def test_sponsorship_zero_initial():
    assert Sponsorship().total_funds() == 0

def test_sponsor_overwrite():
    sp = Sponsorship(); sp.add_sponsor("A", 5000); sp.add_sponsor("A", 7000)
    assert sp.total_funds() == 7000

def test_many_sponsors():
    sp = Sponsorship()
    for i in range(10):
        sp.add_sponsor(f"Sponsor{i}", 1000)
    assert sp.total_funds() == 10000


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9: Multi-module end-to-end scenarios — 7 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_full_workflow_all_modules():
    reg = Registration(); crew = CrewManagement(reg); inv = Inventory()
    rm = RaceManagement(reg, inv); res = Results(inv); mp = MissionPlanning(reg)
    sp = Sponsorship(); garage = Garage(inv)

    reg.register_member("Alice", "driver"); reg.register_member("Bob", "mechanic")
    crew.set_skill("Alice", "speed", 10)
    inv.add_car("Car1"); inv.add_part("Brake Pad")

    race = rm.create_race("Championship", "Alice", "Car1")
    res.record_result(race, "Alice", 2000)
    mission = mp.assign_mission("Fix Car1", ["mechanic"])
    repair = garage.repair_car("Car1")
    sp.add_sponsor("BigSponsor", 10000)

    assert inv.cash == 2000
    assert mission.assigned is True
    assert repair == "Car1 repaired"
    assert sp.total_funds() == 10000

def test_sponsor_and_prize_independent():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    res = Results(inv); sp = Sponsorship()
    reg.register_member("Alice", "driver"); inv.add_car("Car1")
    race = rm.create_race("R", "Alice", "Car1"); res.record_result(race, "Alice", 500)
    sp.add_sponsor("X", 1500)
    assert inv.cash == 500 and sp.total_funds() == 1500

def test_role_restrictions_in_race_and_mission():
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); mp = MissionPlanning(reg)
    reg.register_member("Alice", "mechanic"); reg.register_member("Bob", "driver")
    inv.add_car("Car1")
    race = rm.create_race("R1", "Bob", "Car1")
    assert race.driver.name == "Bob"
    with pytest.raises(ValueError):
        rm.create_race("R2", "Alice", "Car1")
    mission = mp.assign_mission("Fix Car1", ["mechanic"])
    assert mission.assigned is True

def test_damaged_car_mission_requires_mechanic():
    """Assignment requirement: damaged car mission must check mechanic availability."""
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    res = Results(inv); mp = MissionPlanning(reg); garage = Garage(inv)
    reg.register_member("Alice", "driver"); reg.register_member("Bob", "mechanic")
    inv.add_car("Car1")
    race = rm.create_race("Night Race", "Alice", "Car1")
    res.record_result(race, "Alice", 800)
    mission = mp.assign_mission("Fix Car1 Damage", ["mechanic"])
    assert mission.assigned is True
    assert garage.repair_car("Car1") == "Car1 repaired"

    # Without mechanic — mission must fail
    reg2 = Registration(); mp2 = MissionPlanning(reg2)
    reg2.register_member("Dave", "driver")
    with pytest.raises(ValueError):
        mp2.assign_mission("Fix damage", ["mechanic"])

def test_crew_role_change_affects_mission():
    """Role change propagates to mission eligibility."""
    reg = Registration(); crew = CrewManagement(reg); mp = MissionPlanning(reg)
    reg.register_member("Alice", "driver")
    with pytest.raises(ValueError):
        mp.assign_mission("Fix car", ["mechanic"])
    crew.assign_role("Alice", "mechanic")
    mission = mp.assign_mission("Fix car", ["mechanic"])
    assert mission.assigned is True

def test_multi_race_multi_driver_results():
    """Multiple drivers race; results tracked independently per driver."""
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv); res = Results(inv)
    reg.register_member("Alice", "driver"); reg.register_member("Bob", "driver")
    inv.add_car("C1"); inv.add_car("C2")
    for _ in range(3):
        r = rm.create_race("Race", "Alice", "C1"); res.record_result(r, "Alice", 100)
    for _ in range(2):
        r = rm.create_race("Race", "Bob", "C2"); res.record_result(r, "Bob", 200)
    assert res.rankings["Alice"] == 3
    assert res.rankings.get("Bob", 0) == 2

def test_combined_sponsorship_and_prize_total():
    """Sponsorship + prize money represents total team revenue."""
    reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
    res = Results(inv); sp = Sponsorship()
    reg.register_member("Alice", "driver"); inv.add_car("C1")
    race = rm.create_race("GP", "Alice", "C1"); res.record_result(race, "Alice", 1000)
    sp.add_sponsor("A", 500); sp.add_sponsor("B", 500)
    total_revenue = inv.cash + sp.total_funds()
    assert total_revenue == 2000
