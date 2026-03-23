"""
WhiteBox Test Suite for MoneyPoly
Covers: all control-flow branches, key variable states, edge cases,
        and all 5 bugs discovered during analysis.
Run from: 2024115019/whitebox/
  pytest tests/
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
# SECTION 1: buy_property
# ─────────────────────────────────────────────────────────────────────────────

# Test 1: Player cannot buy property if balance is strictly insufficient
def test_player_cannot_buy_property_if_insufficient_balance():
    """Branch: balance < price → return False (balance 0, price 100)."""
    player = Player("Test", balance=0)
    prop = Property("TestProp", 1, 100, 10)
    game = Game([player.name])
    result = game.buy_property(player, prop)
    assert result is False
    assert prop.owner is None

# Test 2 (Bug #1): Player CAN buy property when balance exactly equals price
def test_player_can_buy_property_with_exact_balance():
    """Bug fix: balance == price must be allowed (was blocked by <= bug)."""
    player = Player("Test", balance=100)
    prop = Property("TestProp", 1, 100, 10)
    game = Game([player.name])
    result = game.buy_property(player, prop)
    assert result is True
    assert prop.owner == player
    assert player.balance == 0

# Test 3: Player cannot buy property already owned
def test_buy_property_already_owned():
    """Branch: prop.owner is not None → return False."""
    player = Player("A")
    other = Player("B")
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = other
    game = Game([player.name, other.name])
    result = game.buy_property(player, prop)
    assert result is False

# Test 4: Successful purchase deducts balance and sets owner
def test_buy_property_success_updates_state():
    """Buy property: verify balance deducted and owner set correctly."""
    player = Player("Test", balance=500)
    prop = Property("TestProp", 1, 100, 10)
    game = Game([player.name])
    result = game.buy_property(player, prop)
    assert result is True
    assert prop.owner == player
    assert player.balance == 400
    assert prop in player.properties


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: pay_rent
# ─────────────────────────────────────────────────────────────────────────────

# Test 5: No rent collected on mortgaged property
def test_no_rent_on_mortgaged_property():
    """Branch: is_mortgaged → return early, balances unchanged."""
    payer = Player("A")
    owner = Player("B")
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = owner
    prop.is_mortgaged = True
    game = Game([payer.name, owner.name])
    game.players = [payer, owner]
    game.pay_rent(payer, prop)
    assert payer.balance == 1500
    assert owner.balance == 1500

# Test 6 (Bug #4): Rent IS transferred to owner on unmortgaged property
def test_pay_rent_transfers_to_owner():
    """Bug fix: rent money must be credited to owner (was lost)."""
    payer = Player("A")
    owner = Player("B")
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = owner
    prop.is_mortgaged = False
    game = Game([payer.name, owner.name])
    game.players = [payer, owner]
    game.pay_rent(payer, prop)
    assert payer.balance == 1490   # 1500 - 10 rent
    assert owner.balance == 1510   # 1500 + 10 rent


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Player.move() & Go salary
# ─────────────────────────────────────────────────────────────────────────────

# Test 7: Landing exactly on Go awards salary
def test_landing_on_go_awards_salary():
    """Player moves from 39 → 0: lands on Go, should receive $200."""
    player = Player("Test")
    player.position = 39
    player.move(1)
    assert player.position == 0
    assert player.balance == 1700   # 1500 + 200

# Test 8 (Bug #5): Passing Go (not landing) also awards salary
def test_passing_go_mid_board_awards_salary():
    """Bug fix: player at 38 rolls 6 → lands on 4, must still get $200."""
    player = Player("Test")
    player.position = 38
    initial_balance = player.balance
    player.move(6)
    assert player.position == 4
    assert player.balance == initial_balance + 200

# Test 9: Moving with zero steps does not award Go salary
def test_zero_steps_no_go_salary():
    """Edge case: steps=0, no wrap possible, no salary."""
    player = Player("Test")
    player.position = 0
    initial_balance = player.balance
    player.move(0)
    assert player.position == 0
    assert player.balance == initial_balance   # no salary for steps=0

# Test 10: Negative steps (if ever supplied) handle position mod correctly
def test_negative_steps_wrap():
    """Edge case: negative steps wrap position using modulo."""
    player = Player("Test")
    player.position = 5
    player.move(-3)
    assert player.position == (5 - 3) % 40   # 2


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: PropertyGroup.all_owned_by
# ─────────────────────────────────────────────────────────────────────────────

# Test 11 (Bug #3): Rent NOT doubled with partial group ownership
def test_no_group_bonus_rent_if_partial_ownership():
    """Bug fix: only partial ownership → rent stays at base, not doubled."""
    group = PropertyGroup("Brown", "brown")
    prop1 = Property("Prop1", 1, 100, 10, group)
    prop2 = Property("Prop2", 3, 100, 10, group)
    playerA = Player("A")
    playerB = Player("B")
    prop1.owner = playerA
    prop2.owner = playerB
    assert prop1.get_rent() == 10   # must NOT be doubled to 20

# Test 12: Rent IS doubled when one player owns full group
def test_group_bonus_rent_full_ownership():
    """All properties in group owned by same player → rent doubled."""
    group = PropertyGroup("Brown", "brown")
    prop1 = Property("Prop1", 1, 100, 10, group)
    prop2 = Property("Prop2", 3, 100, 10, group)
    playerA = Player("A")
    prop1.owner = playerA
    prop2.owner = playerA
    assert prop1.get_rent() == 20   # doubled


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: find_winner
# ─────────────────────────────────────────────────────────────────────────────

# Test 13 (Bug #2): find_winner returns RICHEST player
def test_find_winner_returns_richest_player():
    """Bug fix: winner must have highest net worth (was returning lowest)."""
    game = Game(["Alice", "Bob"])
    game.players[0].add_money(500)   # Alice: 2000
    # Bob stays at 1500
    winner = game.find_winner()
    assert winner.name == "Alice"

# Test 14: find_winner with single player returns that player
def test_find_winner_single_player():
    """Edge case: only one player left → they are the winner."""
    game = Game(["Solo"])
    winner = game.find_winner()
    assert winner.name == "Solo"

# Test 15: find_winner with no players returns None
def test_find_winner_no_players():
    """Edge case: empty game → find_winner returns None."""
    game = Game(["Temp"])
    game.players = []
    assert game.find_winner() is None


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: Mortgage / Unmortgage
# ─────────────────────────────────────────────────────────────────────────────

# Test 16: Successful mortgage and unmortgage cycle
def test_mortgage_and_unmortgage_cycle():
    """Mortgage then unmortgage: flags toggle correctly, balances updated."""
    player = Player("Test", balance=2000)
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = player
    player.add_property(prop)
    game = Game([player.name])
    game.mortgage_property(player, prop)
    assert prop.is_mortgaged is True
    game.unmortgage_property(player, prop)
    assert prop.is_mortgaged is False

# Test 17: Cannot mortgage property you do not own
def test_mortgage_property_not_owner():
    """Branch: prop.owner != player → return False."""
    player = Player("A")
    other = Player("B")
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = other
    game = Game([player.name, other.name])
    result = game.mortgage_property(player, prop)
    assert result is False

# Test 18: Cannot unmortgage with insufficient funds
def test_unmortgage_property_insufficient_funds():
    """Branch: balance < cost → return False, property stays mortgaged."""
    player = Player("Test", balance=10)
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = player
    prop.is_mortgaged = True
    player.add_property(prop)
    game = Game([player.name])
    result = game.unmortgage_property(player, prop)
    assert result is False
    assert prop.is_mortgaged is True


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: Trade
# ─────────────────────────────────────────────────────────────────────────────

# Test 19: Trade fails if seller does not own the property
def test_trade_property_not_owned():
    """Branch: prop.owner != seller → return False."""
    seller = Player("A")
    buyer = Player("B")
    prop = Property("TestProp", 1, 100, 10)
    game = Game([seller.name, buyer.name])
    result = game.trade(seller, buyer, prop, 50)
    assert result is False

# Test 20: Trade fails if buyer cannot afford the price
def test_trade_buyer_cannot_afford():
    """Branch: buyer.balance < cash_amount → return False."""
    seller = Player("A")
    buyer = Player("B", balance=10)
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = seller
    seller.add_property(prop)
    game = Game([seller.name, buyer.name])
    result = game.trade(seller, buyer, prop, 500)
    assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: Jail / Bankruptcy / Card actions
# ─────────────────────────────────────────────────────────────────────────────

# Test 21: Bankruptcy eliminates player
def test_bankruptcy_eliminates_player():
    """Branch: balance <= 0 → player.is_eliminated set to True."""
    player = Player("Test", balance=0)
    game = Game([player.name])
    game.players = [player]
    game._check_bankruptcy(player)
    assert player.is_eliminated is True

# Test 22: Get Out of Jail Free card applied correctly
def test_get_out_of_jail_free_card():
    """Card action 'jail_free': player's card count increments by 1."""
    player = Player("Test")
    game = Game([player.name])
    card = {"description": "Get Out of Jail Free.", "action": "jail_free", "value": 0}
    game._apply_card(player, card)
    assert player.get_out_of_jail_cards == 1

# Test 23: Income tax tile deducts correct amount
def test_income_tax_payment():
    """Tile 'income_tax': player's balance decreases by INCOME_TAX_AMOUNT ($200)."""
    player = Player("Test")
    game = Game([player.name])
    player.position = 4  # INCOME_TAX_POSITION
    balance_before = player.balance
    game._move_and_resolve(player, 0)
    assert player.balance == balance_before - 200

# Test 24: Go To Jail tile sends player to jail
def test_go_to_jail_tile():
    """Tile 'go_to_jail': player.in_jail becomes True."""
    player = Player("Test")
    game = Game([player.name])
    player.position = 30  # GO_TO_JAIL_POSITION
    game._move_and_resolve(player, 0)
    assert player.in_jail is True

# Test 25: Player sent to jail after 3 consecutive doubles
def test_player_sent_to_jail_after_3_doubles(monkeypatch):
    """Branch: doubles_streak >= 3 → go_to_jail called."""
    player = Player("Test")
    game = Game([player.name])
    game.current_index = 0

    class DummyDice:
        def __init__(self):
            self.doubles_streak = 2

        def roll(self):
            self.doubles_streak += 1
            return 4

        def is_doubles(self):
            return True

        def describe(self):
            return "2 + 2 = 4 (DOUBLES)"

    game.dice = DummyDice()
    player.in_jail = False
    game.players[0] = player
    game.play_turn()
    assert player.in_jail is True

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: Explicit Individual Module Coverage (Board, Dice, Cards)
# ─────────────────────────────────────────────────────────────────────────────

# Test 26: Board initializes correctly
def test_board_initialization():
    """Validates Board setup and property distribution directly."""
    board = Board()
    assert len(board.properties) == 22
    assert board.get_tile_type(0) == "go"

# Test 27: Dice roll mechanics
def test_dice_roll_bounds():
    """Validates Dice rolls strictly within expected bounds."""
    dice = Dice()
    roll_val = dice.roll()
    assert 2 <= roll_val <= 12
    assert type(dice.is_doubles()) is bool

# Test 28: Card logic parsing
def test_card_deck_operations():
    """Validates Card Deck initialization and draw functionality."""
    deck = CardDeck(CHANCE_CARDS)
    assert len(deck.cards) == 12
    drawn_card = deck.draw()
    assert isinstance(drawn_card, dict)
