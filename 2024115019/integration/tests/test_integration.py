"""
Progressive Integration Test Suite for StreetRace Manager — 60 Tests.

Layer 1: Unit tests — each module tested in isolation (24 tests)
Layer 2: Two-module integration (12 tests)
Layer 3: Three-module integration (8 tests)
Layer 4: Four-module integration (6 tests)
Layer 5: Full system integration — all 8 modules (10 tests)

Run from: 2024115019/integration/
  pytest tests/test_integration.py -v
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


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 1: UNIT TESTS — Individual Module (24 tests)
# ═════════════════════════════════════════════════════════════════════════════

# ── Registration (4) ─────────────────────────────────────────────────────────

class TestUnitRegistration:
    """Unit tests for Registration module in isolation."""

    def test_register_member(self):
        """Scenario: Register a new member. Expected: member stored with name and role."""
        reg = Registration()
        m = reg.register_member("Alice", "driver")
        assert m.name == "Alice" and m.role == "driver"

    def test_register_duplicate_raises(self):
        """Scenario: Register same name twice. Expected: ValueError raised."""
        reg = Registration()
        reg.register_member("Eve", "driver")
        with pytest.raises(ValueError):
            reg.register_member("Eve", "mechanic")

    def test_get_member_exists(self):
        """Scenario: Retrieve registered member. Expected: correct member returned."""
        reg = Registration()
        reg.register_member("Bob", "mechanic")
        assert reg.get_member("Bob").role == "mechanic"

    def test_get_member_not_exists(self):
        """Scenario: Retrieve unregistered member. Expected: None returned."""
        reg = Registration()
        assert reg.get_member("Ghost") is None


# ── Crew Management (4) ─────────────────────────────────────────────────────

class TestUnitCrewManagement:
    """Unit tests for CrewManagement module (with minimal Registration stub)."""

    def test_set_skill(self):
        """Scenario: Set a skill for a member. Expected: skill stored."""
        reg = Registration(); crew = CrewManagement(reg)
        reg.register_member("Alice", "driver")
        crew.set_skill("Alice", "speed", 9)
        assert crew.get_skills("Alice")["speed"] == 9

    def test_multiple_skills(self):
        """Scenario: Set multiple skills. Expected: all skills stored independently."""
        reg = Registration(); crew = CrewManagement(reg)
        reg.register_member("Alice", "driver")
        crew.set_skill("Alice", "speed", 9)
        crew.set_skill("Alice", "control", 7)
        skills = crew.get_skills("Alice")
        assert skills["speed"] == 9 and skills["control"] == 7

    def test_get_skills_unknown(self):
        """Scenario: Get skills for unknown member. Expected: empty dict."""
        reg = Registration(); crew = CrewManagement(reg)
        assert crew.get_skills("Nobody") == {}

    def test_skills_independent_per_member(self):
        """Scenario: Two members have separate skill stores. Expected: no cross-talk."""
        reg = Registration(); crew = CrewManagement(reg)
        reg.register_member("A", "driver"); reg.register_member("B", "mechanic")
        crew.set_skill("A", "speed", 10); crew.set_skill("B", "speed", 5)
        assert crew.get_skills("A")["speed"] == 10
        assert crew.get_skills("B")["speed"] == 5


# ── Inventory (4) ────────────────────────────────────────────────────────────

class TestUnitInventory:
    """Unit tests for Inventory module in isolation."""

    def test_add_car(self):
        """Scenario: Add a car. Expected: car in cars list."""
        inv = Inventory(); inv.add_car("Car1")
        assert "Car1" in inv.cars

    def test_add_parts_and_tools(self):
        """Scenario: Add part and tool. Expected: both stored."""
        inv = Inventory()
        inv.add_part("Brake Pad"); inv.add_tool("Wrench")
        assert "Brake Pad" in inv.parts and "Wrench" in inv.tools

    def test_cash_starts_zero(self):
        """Scenario: New inventory. Expected: cash starts at 0."""
        assert Inventory().cash == 0

    def test_update_cash_accumulates(self):
        """Scenario: Multiple cash updates. Expected: cash sums correctly."""
        inv = Inventory()
        inv.update_cash(300); inv.update_cash(200)
        assert inv.cash == 500


# ── Sponsorship (4) ──────────────────────────────────────────────────────────

class TestUnitSponsorship:
    """Unit tests for Sponsorship module in isolation."""

    def test_add_sponsor(self):
        """Scenario: Add a sponsor. Expected: funds recorded."""
        sp = Sponsorship(); sp.add_sponsor("BigCo", 5000)
        assert sp.total_funds() == 5000

    def test_zero_initial(self):
        """Scenario: No sponsors. Expected: total_funds is 0."""
        assert Sponsorship().total_funds() == 0

    def test_sponsor_overwrite(self):
        """Scenario: Same sponsor updated. Expected: latest amount used."""
        sp = Sponsorship(); sp.add_sponsor("A", 5000); sp.add_sponsor("A", 7000)
        assert sp.total_funds() == 7000

    def test_many_sponsors(self):
        """Scenario: 10 sponsors. Expected: total is sum of all."""
        sp = Sponsorship()
        for i in range(10):
            sp.add_sponsor(f"S{i}", 1000)
        assert sp.total_funds() == 10000


# ── Garage (4) ───────────────────────────────────────────────────────────────

class TestUnitGarage:
    """Unit tests for Garage module (with minimal Inventory)."""

    def test_repair_car_success(self):
        """Scenario: Repair a car in inventory. Expected: success message."""
        inv = Inventory(); inv.add_car("Car1"); garage = Garage(inv)
        assert garage.repair_car("Car1") == "Car1 repaired"

    def test_repair_car_not_in_inventory(self):
        """Scenario: Repair car not in inventory. Expected: ValueError."""
        inv = Inventory(); garage = Garage(inv)
        with pytest.raises(ValueError):
            garage.repair_car("Phantom")

    def test_repair_log(self):
        """Scenario: Repair two cars. Expected: both in repairs list."""
        inv = Inventory(); inv.add_car("A"); inv.add_car("B"); garage = Garage(inv)
        garage.repair_car("A"); garage.repair_car("B")
        assert "A" in garage.repairs and "B" in garage.repairs

    def test_repair_same_car_twice(self):
        """Scenario: Repair same car twice. Expected: 2 entries in log."""
        inv = Inventory(); inv.add_car("A"); garage = Garage(inv)
        garage.repair_car("A"); garage.repair_car("A")
        assert len(garage.repairs) == 2


# ── MissionPlanning (4) ──────────────────────────────────────────────────────

class TestUnitMissionPlanning:
    """Unit tests for MissionPlanning module."""

    def test_assign_mission_success(self):
        """Scenario: Assign mission with available role. Expected: mission.assigned=True."""
        reg = Registration(); reg.register_member("Bob", "mechanic")
        mp = MissionPlanning(reg)
        m = mp.assign_mission("Fix Car", ["mechanic"])
        assert m.assigned is True

    def test_assign_mission_no_role(self):
        """Scenario: No crew with required role. Expected: ValueError."""
        reg = Registration(); mp = MissionPlanning(reg)
        with pytest.raises(ValueError):
            mp.assign_mission("Fix Car", ["mechanic"])

    def test_assign_mission_wrong_role(self):
        """Scenario: Crew exists but wrong role. Expected: ValueError."""
        reg = Registration(); reg.register_member("Alice", "driver")
        mp = MissionPlanning(reg)
        with pytest.raises(ValueError):
            mp.assign_mission("Fix Car", ["mechanic"])

    def test_mission_stored(self):
        """Scenario: Assign mission. Expected: missions list has 1 entry."""
        reg = Registration(); reg.register_member("Bob", "mechanic")
        mp = MissionPlanning(reg)
        mp.assign_mission("Fix", ["mechanic"])
        assert len(mp.missions) == 1


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 2: TWO-MODULE INTEGRATION (12 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestTwoModuleIntegration:
    """Tests involving exactly two modules interacting."""

    # Registration + CrewManagement
    def test_reg_crew_assign_role(self):
        """Modules: Registration + CrewManagement.
        Scenario: Register member then assign a new role.
        Expected: Role updated in registration."""
        reg = Registration(); crew = CrewManagement(reg)
        reg.register_member("Charlie", "driver")
        crew.assign_role("Charlie", "mechanic")
        assert reg.get_member("Charlie").role == "mechanic"

    def test_reg_crew_assign_unregistered_raises(self):
        """Modules: Registration + CrewManagement.
        Scenario: Assign role to unregistered member.
        Expected: ValueError from CrewManagement."""
        reg = Registration(); crew = CrewManagement(reg)
        with pytest.raises(ValueError):
            crew.assign_role("Dana", "mechanic")

    # Registration + RaceManagement
    def test_reg_race_driver_enters_race(self):
        """Modules: Registration + RaceManagement.
        Scenario: Register driver, add car, create race.
        Expected: Race created with correct driver."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        reg.register_member("Alice", "driver"); inv.add_car("Car1")
        race = rm.create_race("GP", "Alice", "Car1")
        assert race.driver.name == "Alice"

    def test_reg_race_non_driver_rejected(self):
        """Modules: Registration + RaceManagement.
        Scenario: Mechanic tries to enter race.
        Expected: ValueError (only drivers can race)."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        reg.register_member("Frank", "mechanic"); inv.add_car("Car1")
        with pytest.raises(ValueError):
            rm.create_race("GP", "Frank", "Car1")

    def test_reg_race_unregistered_driver(self):
        """Modules: Registration + RaceManagement.
        Scenario: Create race with unregistered driver.
        Expected: ValueError."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        inv.add_car("Car1")
        with pytest.raises(ValueError):
            rm.create_race("GP", "Ghost", "Car1")

    # Inventory + RaceManagement
    def test_inv_race_car_not_in_inventory(self):
        """Modules: Inventory + RaceManagement.
        Scenario: Create race with car not in inventory.
        Expected: ValueError."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        reg.register_member("Alice", "driver")
        with pytest.raises(ValueError):
            rm.create_race("GP", "Alice", "Phantom")

    # Inventory + Garage
    def test_inv_garage_repair(self):
        """Modules: Inventory + Garage.
        Scenario: Add car to inventory then repair it.
        Expected: Repair succeeds, logged."""
        inv = Inventory(); inv.add_car("Car1"); garage = Garage(inv)
        result = garage.repair_car("Car1")
        assert result == "Car1 repaired" and len(garage.repairs) == 1

    def test_inv_garage_repair_missing_car(self):
        """Modules: Inventory + Garage.
        Scenario: Repair car not in inventory.
        Expected: ValueError."""
        inv = Inventory(); garage = Garage(inv)
        with pytest.raises(ValueError):
            garage.repair_car("X")

    # Registration + MissionPlanning
    def test_reg_mission_valid(self):
        """Modules: Registration + MissionPlanning.
        Scenario: Register mechanic, assign mechanic mission.
        Expected: Mission assigned successfully."""
        reg = Registration(); reg.register_member("Bob", "mechanic")
        mp = MissionPlanning(reg)
        m = mp.assign_mission("Fix Car", ["mechanic"])
        assert m.assigned is True

    def test_reg_mission_missing_role(self):
        """Modules: Registration + MissionPlanning.
        Scenario: Only driver registered, mechanic mission.
        Expected: ValueError (mechanic unavailable)."""
        reg = Registration(); reg.register_member("Alice", "driver")
        mp = MissionPlanning(reg)
        with pytest.raises(ValueError):
            mp.assign_mission("Fix Car", ["mechanic"])

    # Inventory + Results
    def test_inv_results_prize_updates_cash(self):
        """Modules: Inventory + Results.
        Scenario: Record race result with prize.
        Expected: Prize added to inventory cash."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        reg.register_member("Alice", "driver"); inv.add_car("C1")
        race = rm.create_race("R1", "Alice", "C1")
        res = Results(inv)
        res.record_result(race, "Alice", 1000)
        assert inv.cash == 1000

    # Registration + Sponsorship (independent — verify no conflict)
    def test_reg_sponsor_independent(self):
        """Modules: Registration + Sponsorship.
        Scenario: Both used side by side.
        Expected: No interference between modules."""
        reg = Registration(); sp = Sponsorship()
        reg.register_member("Alice", "driver")
        sp.add_sponsor("BigCo", 5000)
        assert reg.get_member("Alice").name == "Alice"
        assert sp.total_funds() == 5000


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 3: THREE-MODULE INTEGRATION (8 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestThreeModuleIntegration:
    """Tests involving exactly three modules interacting."""

    def test_reg_inv_race_full_flow(self):
        """Modules: Registration + Inventory + RaceManagement.
        Scenario: Register driver, add car, create race.
        Expected: Race object has correct driver and car."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        reg.register_member("Alice", "driver"); inv.add_car("Car1")
        race = rm.create_race("Championship", "Alice", "Car1")
        assert race.driver.name == "Alice" and race.car == "Car1"

    def test_reg_inv_race_two_drivers(self):
        """Modules: Registration + Inventory + RaceManagement.
        Scenario: Two drivers in separate races.
        Expected: Both races created, stored in list."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        reg.register_member("A", "driver"); reg.register_member("B", "driver")
        inv.add_car("C1"); inv.add_car("C2")
        rm.create_race("R1", "A", "C1"); rm.create_race("R2", "B", "C2")
        assert len(rm.races) == 2

    def test_reg_inv_results_prize(self):
        """Modules: Registration + Inventory + Results.
        Scenario: Complete race, record result with prize.
        Expected: Cash updated in inventory."""
        reg = Registration(); inv = Inventory(); rm = RaceManagement(reg, inv)
        reg.register_member("Alice", "driver"); inv.add_car("C1")
        race = rm.create_race("GP", "Alice", "C1")
        res = Results(inv); res.record_result(race, "Alice", 500)
        assert inv.cash == 500

    def test_reg_crew_mission(self):
        """Modules: Registration + CrewManagement + MissionPlanning.
        Scenario: Register driver, change role to mechanic, assign mission.
        Expected: Mission assigned after role change."""
        reg = Registration(); crew = CrewManagement(reg); mp = MissionPlanning(reg)
        reg.register_member("Alice", "driver")
        crew.assign_role("Alice", "mechanic")
        m = mp.assign_mission("Fix Car", ["mechanic"])
        assert m.assigned is True

    def test_reg_crew_mission_role_change_unlocks(self):
        """Modules: Registration + CrewManagement + MissionPlanning.
        Scenario: Mission fails before role change, succeeds after.
        Expected: ValueError first, then success."""
        reg = Registration(); crew = CrewManagement(reg); mp = MissionPlanning(reg)
        reg.register_member("Alice", "driver")
        with pytest.raises(ValueError):
            mp.assign_mission("Fix", ["mechanic"])
        crew.assign_role("Alice", "mechanic")
        m = mp.assign_mission("Fix", ["mechanic"])
        assert m.assigned is True

    def test_reg_inv_garage(self):
        """Modules: Registration + Inventory + Garage.
        Scenario: Add car, repair it, verify log.
        Expected: Repair logged for existing car."""
        inv = Inventory(); inv.add_car("Car1"); garage = Garage(inv)
        result = garage.repair_car("Car1")
        assert result == "Car1 repaired" and len(garage.repairs) == 1

    def test_reg_mission_multi_role(self):
        """Modules: Registration + MissionPlanning (multi-role).
        Scenario: Mission needs driver AND mechanic.
        Expected: Succeeds when both registered."""
        reg = Registration(); mp = MissionPlanning(reg)
        reg.register_member("Alice", "driver"); reg.register_member("Bob", "mechanic")
        m = mp.assign_mission("Rescue", ["driver", "mechanic"])
        assert m.assigned is True

    def test_reg_mission_multi_role_one_missing(self):
        """Modules: Registration + MissionPlanning (multi-role).
        Scenario: Mission needs driver+mechanic, only driver exists.
        Expected: ValueError."""
        reg = Registration(); mp = MissionPlanning(reg)
        reg.register_member("Alice", "driver")
        with pytest.raises(ValueError):
            mp.assign_mission("Rescue", ["driver", "mechanic"])


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 4: FOUR-MODULE INTEGRATION (6 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestFourModuleIntegration:
    """Tests involving exactly four modules interacting."""

    def test_reg_inv_race_results(self):
        """Modules: Registration + Inventory + RaceManagement + Results.
        Scenario: Full race lifecycle — register, add car, race, record result.
        Expected: Rankings updated, cash reflects prize."""
        reg = Registration(); inv = Inventory()
        rm = RaceManagement(reg, inv); res = Results(inv)
        reg.register_member("Alice", "driver"); inv.add_car("C1")
        race = rm.create_race("GP", "Alice", "C1")
        res.record_result(race, "Alice", 2000)
        assert res.rankings["Alice"] == 1
        assert inv.cash == 2000

    def test_reg_inv_race_results_multi_race(self):
        """Modules: Registration + Inventory + RaceManagement + Results.
        Scenario: Three races by same driver.
        Expected: Rankings count=3, cash accumulated."""
        reg = Registration(); inv = Inventory()
        rm = RaceManagement(reg, inv); res = Results(inv)
        reg.register_member("Alice", "driver"); inv.add_car("C1")
        for i in range(3):
            r = rm.create_race(f"Race{i}", "Alice", "C1")
            res.record_result(r, "Alice", 100)
        assert res.rankings["Alice"] == 3
        assert inv.cash == 300

    def test_reg_crew_inv_race(self):
        """Modules: Registration + CrewManagement + Inventory + RaceManagement.
        Scenario: Register as mechanic, change to driver, then race.
        Expected: Role change allows racing."""
        reg = Registration(); crew = CrewManagement(reg); inv = Inventory()
        rm = RaceManagement(reg, inv)
        reg.register_member("Alice", "mechanic"); inv.add_car("C1")
        with pytest.raises(ValueError):
            rm.create_race("GP", "Alice", "C1")  # mechanic can't race
        crew.assign_role("Alice", "driver")
        race = rm.create_race("GP", "Alice", "C1")
        assert race.driver.name == "Alice"

    def test_reg_inv_garage_mission(self):
        """Modules: Registration + Inventory + Garage + MissionPlanning.
        Scenario: Car damaged, mechanic needed for mission, then repair.
        Expected: Mission assigned, car repaired."""
        reg = Registration(); inv = Inventory(); garage = Garage(inv)
        mp = MissionPlanning(reg)
        reg.register_member("Bob", "mechanic"); inv.add_car("Car1")
        m = mp.assign_mission("Repair Mission", ["mechanic"])
        assert m.assigned is True
        assert garage.repair_car("Car1") == "Car1 repaired"

    def test_reg_inv_race_garage(self):
        """Modules: Registration + Inventory + RaceManagement + Garage.
        Scenario: Race then repair damaged car.
        Expected: Race created, then car repaired from same inventory."""
        reg = Registration(); inv = Inventory()
        rm = RaceManagement(reg, inv); garage = Garage(inv)
        reg.register_member("Alice", "driver"); inv.add_car("Car1")
        rm.create_race("GP", "Alice", "Car1")
        assert garage.repair_car("Car1") == "Car1 repaired"

    def test_reg_inv_results_sponsor(self):
        """Modules: Registration + Inventory + Results + Sponsorship.
        Scenario: Prize money + sponsorship = total team revenue.
        Expected: Both tracked independently."""
        reg = Registration(); inv = Inventory()
        rm = RaceManagement(reg, inv); res = Results(inv); sp = Sponsorship()
        reg.register_member("Alice", "driver"); inv.add_car("C1")
        race = rm.create_race("R1", "Alice", "C1")
        res.record_result(race, "Alice", 1000)
        sp.add_sponsor("BigCo", 2000)
        assert inv.cash == 1000
        assert sp.total_funds() == 2000
        assert inv.cash + sp.total_funds() == 3000


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 5: FULL SYSTEM INTEGRATION — ALL 8 MODULES (10 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestFullSystemIntegration:
    """End-to-end tests with all 8 modules working together."""

    def _setup_system(self):
        """Helper: create all 8 module instances wired together."""
        reg = Registration()
        crew = CrewManagement(reg)
        inv = Inventory()
        rm = RaceManagement(reg, inv)
        res = Results(inv)
        mp = MissionPlanning(reg)
        garage = Garage(inv)
        sp = Sponsorship()
        return reg, crew, inv, rm, res, mp, garage, sp

    def test_full_lifecycle(self):
        """All 8 modules. Scenario: Register crew, race, win prize,
        repair car, assign mission, add sponsor.
        Expected: All state updated correctly across all modules."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver")
        reg.register_member("Bob", "mechanic")
        crew.set_skill("Alice", "speed", 10)
        inv.add_car("Car1"); inv.add_part("Brake Pad")
        race = rm.create_race("Championship", "Alice", "Car1")
        res.record_result(race, "Alice", 2000)
        m = mp.assign_mission("Fix Car1", ["mechanic"])
        garage.repair_car("Car1")
        sp.add_sponsor("BigCo", 10000)
        assert inv.cash == 2000
        assert m.assigned is True
        assert sp.total_funds() == 10000
        assert res.rankings["Alice"] == 1

    def test_full_role_restriction_enforced(self):
        """All modules. Scenario: Mechanic cannot race; driver cannot do mechanic mission.
        Expected: Role restrictions enforced across modules."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "mechanic")
        reg.register_member("Bob", "driver")
        inv.add_car("Car1")
        with pytest.raises(ValueError):
            rm.create_race("GP", "Alice", "Car1")  # mechanic can't race
        race = rm.create_race("GP", "Bob", "Car1")
        assert race.driver.name == "Bob"
        m = mp.assign_mission("Repair", ["mechanic"])
        assert m.assigned is True

    def test_full_damaged_car_flow(self):
        """All modules. Scenario: Race → car damaged → check mechanic → repair.
        Expected: Full damage-repair pipeline works."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver")
        reg.register_member("Bob", "mechanic")
        inv.add_car("Car1")
        race = rm.create_race("Night Race", "Alice", "Car1")
        res.record_result(race, "Alice", 800)
        m = mp.assign_mission("Fix Damage", ["mechanic"])
        assert m.assigned is True
        assert garage.repair_car("Car1") == "Car1 repaired"
        assert inv.cash == 800

    def test_full_no_mechanic_mission_fails(self):
        """All modules. Scenario: Only drivers registered, mechanic mission fails.
        Expected: ValueError for missing mechanic role."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver")
        reg.register_member("Bob", "driver")
        with pytest.raises(ValueError):
            mp.assign_mission("Repair", ["mechanic"])

    def test_full_role_change_enables_mission(self):
        """All modules. Scenario: Change role from driver to mechanic, then assign mission.
        Expected: Role change propagates to mission eligibility."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver")
        with pytest.raises(ValueError):
            mp.assign_mission("Fix", ["mechanic"])
        crew.assign_role("Alice", "mechanic")
        m = mp.assign_mission("Fix", ["mechanic"])
        assert m.assigned is True

    def test_full_multi_driver_results(self):
        """All modules. Scenario: Two drivers, multiple races, independent rankings.
        Expected: Rankings tracked per driver, cash accumulated."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver")
        reg.register_member("Bob", "driver")
        inv.add_car("C1"); inv.add_car("C2")
        for _ in range(3):
            r = rm.create_race("R", "Alice", "C1")
            res.record_result(r, "Alice", 100)
        for _ in range(2):
            r = rm.create_race("R", "Bob", "C2")
            res.record_result(r, "Bob", 200)
        assert res.rankings["Alice"] == 3
        assert res.rankings["Bob"] == 2
        assert inv.cash == 700

    def test_full_sponsor_plus_prize(self):
        """All modules. Scenario: Sponsorship + prize = total team revenue.
        Expected: Both revenue streams tracked independently."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver"); inv.add_car("C1")
        race = rm.create_race("GP", "Alice", "C1")
        res.record_result(race, "Alice", 1000)
        sp.add_sponsor("A", 500); sp.add_sponsor("B", 500)
        assert inv.cash + sp.total_funds() == 2000

    def test_full_race_history_tracked(self):
        """All modules. Scenario: Multiple races recorded.
        Expected: Results history has all entries."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver"); inv.add_car("C1")
        for i in range(4):
            r = rm.create_race(f"Race{i}", "Alice", "C1")
            res.record_result(r, "Alice", 50)
        assert len(res.history) == 4
        assert inv.cash == 200

    def test_full_crew_skills_and_race(self):
        """All modules. Scenario: Set skills, then create race.
        Expected: Skills stored independently, race works."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        reg.register_member("Alice", "driver")
        crew.set_skill("Alice", "speed", 10)
        crew.set_skill("Alice", "handling", 8)
        inv.add_car("C1")
        race = rm.create_race("GP", "Alice", "C1")
        assert race.driver.name == "Alice"
        assert crew.get_skills("Alice")["speed"] == 10

    def test_full_complete_workflow_all_features(self):
        """All modules. Scenario: Complete end-to-end workflow exercising every module.
        Expected: All state consistent after full workflow."""
        reg, crew, inv, rm, res, mp, garage, sp = self._setup_system()
        # 1. Register crew
        reg.register_member("Alice", "driver")
        reg.register_member("Bob", "mechanic")
        reg.register_member("Carol", "strategist")
        # 2. Set skills
        crew.set_skill("Alice", "speed", 10)
        crew.set_skill("Bob", "repair", 9)
        # 3. Stock inventory
        inv.add_car("SpeedDemon"); inv.add_car("Thunder")
        inv.add_part("Nitro"); inv.add_tool("Wrench")
        # 4. Get sponsorship
        sp.add_sponsor("MegaCorp", 50000)
        # 5. Race
        race1 = rm.create_race("Grand Prix", "Alice", "SpeedDemon")
        res.record_result(race1, "Alice", 5000)
        # 6. Repair after race
        garage.repair_car("SpeedDemon")
        # 7. Mission requiring mechanic + strategist
        m = mp.assign_mission("Rescue Op", ["mechanic", "strategist"])
        # 8. Verify everything
        assert inv.cash == 5000
        assert sp.total_funds() == 50000
        assert res.rankings["Alice"] == 1
        assert len(res.history) == 1
        assert m.assigned is True
        assert len(garage.repairs) == 1
        assert crew.get_skills("Alice")["speed"] == 10
        assert reg.get_member("Carol").role == "strategist"
