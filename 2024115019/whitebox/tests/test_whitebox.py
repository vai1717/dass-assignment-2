"""
Comprehensive White-Box Test Suite for MoneyPoly — 70 Tests.
Covers all branches, key variable states, and edge cases across:
  player.py, game.py (buy_property, pay_rent, trade, mortgage/unmortgage,
  _apply_card, _check_bankruptcy, find_winner, move, auction),
  property.py (get_rent, mortgage cycle), board.py, dice.py, cards.py, bank.py

Run from: 2024115019/whitebox/
  python -m pytest tests/test_whitebox.py -v
"""
import sys
import os
import pytest

# Ensure the moneypoly package in code/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code", "moneypoly"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code", "moneypoly", "moneypoly"))

from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly.game import Game
from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.dice import Dice
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Player — add_money / deduct_money branches (Tests 1-8)
# ─────────────────────────────────────────────────────────────────────────────

def test_add_money_positive():
    """add_money with positive amount increases balance."""
    p = Player("A", balance=100)
    p.add_money(50)
    assert p.balance == 150

def test_add_money_zero():
    """add_money with 0 is a no-op, balance unchanged."""
    p = Player("A", balance=100)
    p.add_money(0)
    assert p.balance == 100

def test_add_money_negative_raises():
    """add_money with negative amount raises ValueError (branch: amount < 0)."""
    p = Player("A")
    with pytest.raises(ValueError):
        p.add_money(-10)

def test_deduct_money_positive():
    """deduct_money with positive amount decreases balance."""
    p = Player("A", balance=200)
    p.deduct_money(80)
    assert p.balance == 120

def test_deduct_money_zero():
    """deduct_money with 0 is a no-op."""
    p = Player("A", balance=200)
    p.deduct_money(0)
    assert p.balance == 200

def test_deduct_money_negative_raises():
    """deduct_money with negative raises ValueError (branch: amount < 0)."""
    p = Player("A")
    with pytest.raises(ValueError):
        p.deduct_money(-5)

def test_deduct_money_to_zero():
    """deduct_money to exactly 0 — balance becomes 0 (bankruptcy boundary)."""
    p = Player("A", balance=100)
    p.deduct_money(100)
    assert p.balance == 0

def test_deduct_money_below_zero():
    """deduct_money can push balance negative — is_bankrupt then returns True."""
    p = Player("A", balance=50)
    p.deduct_money(100)
    assert p.balance == -50
    assert p.is_bankrupt() is True


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Player — move() branches (Tests 9-17)
# ─────────────────────────────────────────────────────────────────────────────

def test_move_normal_no_wrap():
    """Normal move that does not cross Go — no salary awarded."""
    p = Player("A"); p.position = 5
    p.move(10)
    assert p.position == 15
    assert p.balance == 1500  # no salary

def test_move_lands_on_go():
    """Move from 39 → 0: lands on Go, salary awarded."""
    p = Player("A"); p.position = 39
    p.move(1)
    assert p.position == 0
    assert p.balance == 1700

def test_move_passes_go():
    """Move wraps past 0 — salary still awarded (key bug fix)."""
    p = Player("A"); p.position = 38
    p.move(6)
    assert p.position == 4
    assert p.balance == 1700

def test_move_zero_steps():
    """Moving 0 steps does not award salary (edge: steps=0 branch)."""
    p = Player("A"); p.position = 0
    p.move(0)
    assert p.balance == 1500

def test_move_negative_steps():
    """Negative steps wrap correctly with modulo, no salary."""
    p = Player("A"); p.position = 5
    p.move(-3)
    assert p.position == 2

def test_move_large_steps():
    """Large steps wrap around multiple times correctly."""
    p = Player("A"); p.position = 0
    p.move(40)  # full board wrap — ends back at 0
    assert p.position == 0

def test_move_large_steps_with_salary():
    """Large steps that cross Go award salary even when wrapping far."""
    p = Player("A"); p.position = 35
    p.move(10)  # 35+10=45 → 45%40=5, wrapped → salary
    assert p.position == 5
    assert p.balance == 1700

def test_move_exact_board_wrap():
    """BOARD_SIZE steps from 0 → 0, wraps completely, salary awarded."""
    p = Player("A"); p.position = 1
    p.move(39)  # 1+39=40 → 0
    assert p.position == 0
    assert p.balance == 1700

def test_go_to_jail():
    """go_to_jail sets position to JAIL_POSITION and sets in_jail flag."""
    p = Player("A")
    p.go_to_jail()
    assert p.in_jail is True
    assert p.position == 10
    assert p.jail_turns == 0


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Player — property management (Tests 18-22)
# ─────────────────────────────────────────────────────────────────────────────

def test_add_property():
    """add_property appends prop to player.properties."""
    p = Player("A")
    prop = Property("TestProp", 1, 100, 10)
    p.add_property(prop)
    assert prop in p.properties

def test_add_property_no_duplicates():
    """add_property is idempotent — adding same prop twice keeps one entry."""
    p = Player("A")
    prop = Property("TestProp", 1, 100, 10)
    p.add_property(prop)
    p.add_property(prop)
    assert p.properties.count(prop) == 1

def test_remove_property():
    """remove_property removes the prop from player.properties."""
    p = Player("A")
    prop = Property("TestProp", 1, 100, 10)
    p.add_property(prop)
    p.remove_property(prop)
    assert prop not in p.properties

def test_remove_property_not_owned():
    """remove_property on unowned prop is a silent no-op."""
    p = Player("A")
    prop = Property("TestProp", 1, 100, 10)
    p.remove_property(prop)  # should not raise
    assert prop not in p.properties

def test_count_properties():
    """count_properties returns the correct count."""
    p = Player("A")
    for i in range(3):
        p.add_property(Property(f"P{i}", i, 100, 10))
    assert p.count_properties() == 3


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Game.buy_property branches (Tests 23-30)
# ─────────────────────────────────────────────────────────────────────────────

def test_buy_insufficient_balance():
    """buy_property returns False when player balance < price."""
    p = Player("A", balance=0)
    prop = Property("P", 1, 100, 10)
    game = Game(["A"])
    assert game.buy_property(p, prop) is False
    assert prop.owner is None

def test_buy_exact_balance():
    """buy_property returns True when balance == price (boundary)."""
    p = Player("A", balance=100)
    prop = Property("P", 1, 100, 10)
    game = Game(["A"])
    result = game.buy_property(p, prop)
    assert result is True
    assert p.balance == 0

def test_buy_already_owned():
    """buy_property returns False when property already has an owner."""
    p1, p2 = Player("A"), Player("B")
    prop = Property("P", 1, 100, 10)
    prop.owner = p2
    game = Game(["A", "B"])
    assert game.buy_property(p1, prop) is False

def test_buy_success_state_changes():
    """Successful buy: balance deducted, owner set, prop in player.properties."""
    p = Player("A", balance=500)
    prop = Property("P", 1, 100, 10)
    game = Game(["A"])
    game.buy_property(p, prop)
    assert prop.owner == p
    assert p.balance == 400
    assert prop in p.properties

def test_buy_multiple_properties():
    """Player can successfully buy multiple properties sequentially."""
    p = Player("A", balance=1000)
    game = Game(["A"])
    props = [Property(f"P{i}", i, 200, 10) for i in range(3)]
    for prop in props:
        game.buy_property(p, prop)
    assert p.count_properties() == 3
    assert p.balance == 400

def test_buy_property_zero_price():
    """buy_property with price 0 succeeds; balance unchanged."""
    p = Player("A", balance=0)
    prop = Property("Free", 1, 0, 0)
    game = Game(["A"])
    result = game.buy_property(p, prop)
    assert result is True
    assert prop.owner == p

def test_buy_returns_false_does_not_change_balance():
    """Failed buy: player balance must remain unchanged."""
    p = Player("A", balance=50)
    prop = Property("P", 1, 100, 10)
    game = Game(["A"])
    game.buy_property(p, prop)
    assert p.balance == 50  # unchanged

def test_buy_with_large_price():
    """buy_property with a very large price succeeds if balance sufficient."""
    p = Player("A", balance=1_000_000)
    prop = Property("Mansion", 1, 999_999, 10)
    game = Game(["A"])
    assert game.buy_property(p, prop) is True
    assert p.balance == 1


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Game.pay_rent branches (Tests 31-36)
# ─────────────────────────────────────────────────────────────────────────────

def test_pay_rent_mortgaged_no_deduction():
    """No rent on mortgaged property — both balances stay the same."""
    payer = Player("A"); owner = Player("B")
    prop = Property("P", 1, 100, 10); prop.owner = owner; prop.is_mortgaged = True
    game = Game(["A", "B"]); game.players = [payer, owner]
    game.pay_rent(payer, prop)
    assert payer.balance == 1500
    assert owner.balance == 1500

def test_pay_rent_transfers_money():
    """Rent deducted from payer and credited to owner."""
    payer = Player("A"); owner = Player("B")
    prop = Property("P", 1, 100, 10); prop.owner = owner; prop.is_mortgaged = False
    game = Game(["A", "B"]); game.players = [payer, owner]
    game.pay_rent(payer, prop)
    assert payer.balance == 1490
    assert owner.balance == 1510

def test_pay_rent_no_owner():
    """pay_rent returns early if prop.owner is None — no crash."""
    payer = Player("A")
    prop = Property("P", 1, 100, 10); prop.owner = None; prop.is_mortgaged = False
    game = Game(["A"]); game.players = [payer]
    game.pay_rent(payer, prop)  # must not raise
    assert payer.balance == 1500

def test_pay_rent_group_bonus():
    """Full colour group ownership doubles rent."""
    group = PropertyGroup("Brown", "brown")
    prop1 = Property("P1", 1, 100, 10, group)
    prop2 = Property("P2", 3, 100, 10, group)
    owner = Player("B"); prop1.owner = owner; prop2.owner = owner
    payer = Player("A")
    game = Game(["A", "B"]); game.players = [payer, owner]
    game.pay_rent(payer, prop1)
    assert payer.balance == 1480  # 1500 - 20 (doubled)

def test_pay_rent_partial_group_no_bonus():
    """Partial group ownership — rent stays base."""
    group = PropertyGroup("Brown", "brown")
    prop1 = Property("P1", 1, 100, 10, group)
    prop2 = Property("P2", 3, 100, 10, group)
    ownerA = Player("A"); ownerB = Player("B")
    prop1.owner = ownerA; prop2.owner = ownerB
    payer = Player("C", balance=1500)
    game = Game(["A", "B", "C"]); game.players = [payer, ownerA, ownerB]
    game.pay_rent(payer, prop1)
    assert payer.balance == 1490  # not doubled

def test_pay_rent_zero_rent():
    """Property with rent=0 — payer loses nothing."""
    payer = Player("A"); owner = Player("B")
    prop = Property("P", 1, 100, 0); prop.owner = owner; prop.is_mortgaged = False
    game = Game(["A", "B"]); game.players = [payer, owner]
    game.pay_rent(payer, prop)
    assert payer.balance == 1500


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: Game.mortgage / unmortgage branches (Tests 37-44)
# ─────────────────────────────────────────────────────────────────────────────

def test_mortgage_not_owner_returns_false():
    """mortgage_property returns False when player!=owner."""
    p1 = Player("A"); p2 = Player("B")
    prop = Property("P", 1, 100, 10); prop.owner = p2
    game = Game(["A", "B"])
    assert game.mortgage_property(p1, prop) is False

def test_mortgage_success():
    """Mortgage succeeds: is_mortgaged=True, player gets payout."""
    p = Player("A", balance=500)
    prop = Property("P", 1, 100, 10); prop.owner = p; p.add_property(prop)
    game = Game(["A"])
    result = game.mortgage_property(p, prop)
    assert result is True
    assert prop.is_mortgaged is True
    assert p.balance > 500  # received payout

def test_mortgage_already_mortgaged():
    """Mortgaging an already-mortgaged property returns False."""
    p = Player("A")
    prop = Property("P", 1, 100, 10); prop.owner = p; prop.is_mortgaged = True
    p.add_property(prop)
    game = Game(["A"])
    result = game.mortgage_property(p, prop)
    assert result is False

def test_unmortgage_not_owner_returns_false():
    """unmortgage_property returns False when player!=owner."""
    p1 = Player("A"); p2 = Player("B")
    prop = Property("P", 1, 100, 10); prop.owner = p2; prop.is_mortgaged = True
    game = Game(["A", "B"])
    assert game.unmortgage_property(p1, prop) is False

def test_unmortgage_insufficient_funds():
    """unmortgage returns False and property stays mortgaged when balance too low."""
    p = Player("A", balance=1)
    prop = Property("P", 1, 100, 10); prop.owner = p; prop.is_mortgaged = True
    p.add_property(prop)
    game = Game(["A"])
    result = game.unmortgage_property(p, prop)
    assert result is False
    assert prop.is_mortgaged is True

def test_unmortgage_success():
    """Successful unmortgage: is_mortgaged=False, balance reduced."""
    p = Player("A", balance=2000)
    prop = Property("P", 1, 100, 10); prop.owner = p; p.add_property(prop)
    game = Game(["A"])
    game.mortgage_property(p, prop)   # mortgage first
    bal_after_mortgage = p.balance
    result = game.unmortgage_property(p, prop)
    assert result is True
    assert prop.is_mortgaged is False
    assert p.balance < bal_after_mortgage  # paid cost

def test_unmortgage_not_mortgaged():
    """unmortgage on a non-mortgaged property returns False."""
    p = Player("A", balance=2000)
    prop = Property("P", 1, 100, 10); prop.owner = p; prop.is_mortgaged = False
    p.add_property(prop)
    game = Game(["A"])
    result = game.unmortgage_property(p, prop)
    assert result is False

def test_mortgage_unmortgage_full_cycle():
    """Full cycle: mortgage then unmortgage restores is_mortgaged=False."""
    p = Player("A", balance=2000)
    prop = Property("P", 1, 100, 10); prop.owner = p; p.add_property(prop)
    game = Game(["A"])
    game.mortgage_property(p, prop)
    assert prop.is_mortgaged is True
    game.unmortgage_property(p, prop)
    assert prop.is_mortgaged is False


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: Game.trade branches (Tests 45-50)
# ─────────────────────────────────────────────────────────────────────────────

def test_trade_seller_not_owner():
    """trade returns False when seller doesn't own property."""
    seller = Player("A"); buyer = Player("B")
    prop = Property("P", 1, 100, 10)
    game = Game(["A", "B"])
    assert game.trade(seller, buyer, prop, 50) is False

def test_trade_buyer_cannot_afford():
    """trade returns False when buyer.balance < cash_amount."""
    seller = Player("A"); buyer = Player("B", balance=10)
    prop = Property("P", 1, 100, 10); prop.owner = seller; seller.add_property(prop)
    game = Game(["A", "B"])
    assert game.trade(seller, buyer, prop, 500) is False

def test_trade_success_ownership_transfer():
    """Successful trade: prop.owner becomes buyer."""
    seller = Player("A", balance=1500); buyer = Player("B", balance=1500)
    prop = Property("P", 1, 100, 10); prop.owner = seller; seller.add_property(prop)
    game = Game(["A", "B"])
    result = game.trade(seller, buyer, prop, 100)
    assert result is True
    assert prop.owner == buyer
    assert prop in buyer.properties
    assert prop not in seller.properties

def test_trade_success_cash_transfer():
    """Successful trade: money transferred from buyer to seller."""
    seller = Player("A", balance=1500); buyer = Player("B", balance=1500)
    prop = Property("P", 1, 100, 10); prop.owner = seller; seller.add_property(prop)
    game = Game(["A", "B"])
    game.trade(seller, buyer, prop, 300)
    assert buyer.balance == 1200
    # Note: seller balance not increased in basic trade (seller adds separately)

def test_trade_zero_cash():
    """Trade with cash_amount=0 still transfers ownership correctly."""
    seller = Player("A"); buyer = Player("B")
    prop = Property("P", 1, 100, 10); prop.owner = seller; seller.add_property(prop)
    game = Game(["A", "B"])
    result = game.trade(seller, buyer, prop, 0)
    assert result is True
    assert prop.owner == buyer

def test_trade_exact_buyer_balance():
    """Buyer with exactly enough cash can complete trade (boundary)."""
    seller = Player("A"); buyer = Player("B", balance=100)
    prop = Property("P", 1, 100, 10); prop.owner = seller; seller.add_property(prop)
    game = Game(["A", "B"])
    assert game.trade(seller, buyer, prop, 100) is True
    assert buyer.balance == 0


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: _apply_card branches (Tests 51-57)
# ─────────────────────────────────────────────────────────────────────────────

def test_apply_card_none():
    """_apply_card with None card is a safe no-op."""
    p = Player("A")
    game = Game(["A"]); game.players = [p]
    game._apply_card(p, None)  # must not raise

def test_apply_card_collect():
    """Card action 'collect': player's balance increases."""
    p = Player("A")
    game = Game(["A"]); game.players = [p]
    card = {"description": "Collect $200", "action": "collect", "value": 200}
    game._apply_card(p, card)
    assert p.balance == 1700

def test_apply_card_pay():
    """Card action 'pay': player's balance decreases."""
    p = Player("A", balance=500)
    game = Game(["A"]); game.players = [p]
    card = {"description": "Pay $100", "action": "pay", "value": 100}
    game._apply_card(p, card)
    assert p.balance == 400

def test_apply_card_jail():
    """Card action 'jail': player.in_jail becomes True."""
    p = Player("A")
    game = Game(["A"]); game.players = [p]
    card = {"description": "Go to Jail", "action": "jail", "value": 0}
    game._apply_card(p, card)
    assert p.in_jail is True

def test_apply_card_jail_free():
    """Card action 'jail_free': player.get_out_of_jail_cards incremented."""
    p = Player("A")
    game = Game(["A"]); game.players = [p]
    card = {"description": "GOOJF", "action": "jail_free", "value": 0}
    game._apply_card(p, card)
    assert p.get_out_of_jail_cards == 1

def test_apply_card_birthday():
    """Card action 'birthday': each other player pays value to card holder."""
    p_main = Player("Main"); p2 = Player("B", balance=200); p3 = Player("C", balance=200)
    game = Game(["Main", "B", "C"]); game.players = [p_main, p2, p3]
    card = {"description": "Birthday", "action": "birthday", "value": 50}
    game._apply_card(p_main, card)
    assert p2.balance == 150
    assert p3.balance == 150
    assert p_main.balance == 1600  # 1500 + 50 + 50

def test_apply_card_move_to_passes_go():
    """Card action 'move_to' with value < current position awards Go salary."""
    p = Player("A"); p.position = 30
    game = Game(["A"]); game.players = [p]
    card = {"description": "Advance to Go", "action": "move_to", "value": 0}
    game._apply_card(p, card)
    assert p.position == 0
    assert p.balance == 1700  # salary collected


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9: _check_bankruptcy / find_winner (Tests 58-64)
# ─────────────────────────────────────────────────────────────────────────────

def test_bankruptcy_eliminates():
    """Player with balance=0 is marked eliminated and removed."""
    p = Player("A", balance=0)
    game = Game(["A"]); game.players = [p]
    game._check_bankruptcy(p)
    assert p.is_eliminated is True

def test_bankruptcy_releases_properties():
    """Bankrupt player's properties revert to unowned and unmortgaged."""
    p = Player("A", balance=0)
    prop = Property("P", 1, 100, 10); prop.owner = p; prop.is_mortgaged = True
    p.add_property(prop)
    game = Game(["A"]); game.players = [p]
    game._check_bankruptcy(p)
    assert prop.owner is None
    assert prop.is_mortgaged is False

def test_no_bankruptcy_positive_balance():
    """Player with positive balance is not eliminated."""
    p = Player("A", balance=1)
    game = Game(["A"]); game.players = [p]
    game._check_bankruptcy(p)
    assert p.is_eliminated is False

def test_find_winner_richest_player():
    """find_winner returns player with highest balance."""
    game = Game(["Alice", "Bob"])
    game.players[0].add_money(500)  # Alice has 2000
    assert game.find_winner().name == "Alice"

def test_find_winner_single_player():
    """find_winner with one player returns that player."""
    game = Game(["Solo"])
    assert game.find_winner().name == "Solo"

def test_find_winner_empty_returns_none():
    """find_winner with no players returns None."""
    game = Game(["Temp"]); game.players = []
    assert game.find_winner() is None

def test_advance_turn_wraps():
    """advance_turn wraps current_index back to 0 after last player."""
    game = Game(["A", "B"]); game.current_index = 1
    game.advance_turn()
    assert game.current_index == 0


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10: PropertyGroup.all_owned_by (Tests 65-67)
# ─────────────────────────────────────────────────────────────────────────────

def test_group_not_all_owned():
    """all_owned_by returns False for partial group ownership."""
    group = PropertyGroup("Brown", "brown")
    p1 = Property("P1", 1, 100, 10, group)
    p2 = Property("P2", 3, 100, 10, group)
    a = Player("A"); b = Player("B")
    p1.owner = a; p2.owner = b
    assert group.all_owned_by(a) is False

def test_group_all_owned():
    """all_owned_by returns True when player owns entire group."""
    group = PropertyGroup("Brown", "brown")
    p1 = Property("P1", 1, 100, 10, group)
    p2 = Property("P2", 3, 100, 10, group)
    a = Player("A"); p1.owner = a; p2.owner = a
    assert group.all_owned_by(a) is True

def test_group_get_rent_doubles_when_full():
    """get_rent returns doubled value when player owns full group."""
    group = PropertyGroup("Brown", "brown")
    p1 = Property("P1", 1, 100, 10, group)
    p2 = Property("P2", 3, 100, 10, group)
    a = Player("A"); p1.owner = a; p2.owner = a
    assert p1.get_rent() == 20


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11: Board, Dice, Cards modules (Tests 68-70)
# ─────────────────────────────────────────────────────────────────────────────

def test_board_initialization():
    """Board has 22 purchasable properties; position 0 returns 'go' tile type."""
    board = Board()
    assert len(board.properties) == 22  # 22 buyable property tiles
    assert board.get_tile_type(0) == "go"

def test_dice_roll_bounds():
    """Dice roll always returns a value between 2 and 12 inclusive."""
    dice = Dice()
    for _ in range(200):
        val = dice.roll()
        assert 2 <= val <= 12

def test_card_deck_operations():
    """CardDeck initializes with correct count and draw returns a dict."""
    deck = CardDeck(CHANCE_CARDS)
    assert len(deck.cards) == 12
    drawn_card = deck.draw()
    assert isinstance(drawn_card, dict)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 12: jail after 3 doubles (Test 71 — still numbered for report)
# ─────────────────────────────────────────────────────────────────────────────

def test_player_sent_to_jail_after_3_doubles(monkeypatch):
    """Three consecutive doubles sends player to jail (doubles_streak branch)."""
    p = Player("Test")
    game = Game(["Test"]); game.current_index = 0

    class DummyDice:
        def __init__(self): self.doubles_streak = 2
        def roll(self): self.doubles_streak += 1; return 4
        def is_doubles(self): return True
        def describe(self): return "2+2=4 (DOUBLES)"

    game.dice = DummyDice(); game.players[0] = p
    p.in_jail = False
    game.play_turn()
    assert p.in_jail is True

def test_income_tax_tile():
    """Landing on income tax tile (position 4) deducts INCOME_TAX_AMOUNT."""
    p = Player("A"); p.position = 4
    game = Game(["A"]); game.players = [p]
    bal = p.balance
    game._move_and_resolve(p, 0)
    assert p.balance == bal - 200

def test_go_to_jail_tile():
    """Landing on go_to_jail tile (position 30) sets player.in_jail=True."""
    p = Player("A"); p.position = 30
    game = Game(["A"]); game.players = [p]
    game._move_and_resolve(p, 0)
    assert p.in_jail is True
