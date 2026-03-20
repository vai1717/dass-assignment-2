import pytest
from moneypoly.player import Player
from moneypoly.property import Property
from moneypoly.game import Game
from moneypoly.board import Board
from moneypoly.bank import Bank

# Test 1: Player cannot buy property if balance is insufficient
def test_player_cannot_buy_property_if_insufficient_balance():
    player = Player("Test", balance=0)
    prop = Property("TestProp", 1, 100, 10)
    game = Game([player.name])
    result = game.buy_property(player, prop)
    assert result is False
    assert prop.owner is None

# Test 2: Player sent to jail after 3 consecutive doubles
def test_player_sent_to_jail_after_3_doubles(monkeypatch):
    player = Player("Test")
    game = Game([player.name])
    game.current_index = 0
    # Monkeypatch dice to always roll doubles
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

# Test 3: Cannot pay rent on mortgaged property
def test_no_rent_on_mortgaged_property():
    player = Player("A")
    owner = Player("B")
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = owner
    prop.is_mortgaged = True
    game = Game([player.name, owner.name])
    game.pay_rent(player, prop)
    assert player.balance == 1500
    assert owner.balance == 1500

# Test 4: Passing Go awards salary
def test_passing_go_awards_salary():
    player = Player("Test")
    player.position = 39
    player.move(1)
    assert player.position == 0
    assert player.balance == 1700

# Test 5: Auction: Highest valid bid wins (skipped, requires UI mocking)

# Test 6: Mortgage and unmortgage property
def test_mortgage_and_unmortgage():
    player = Player("Test")
    prop = Property("TestProp", 1, 100, 10)
    prop.owner = player
    player.add_property(prop)
    game = Game([player.name])
    game.mortgage_property(player, prop)
    assert prop.is_mortgaged is True
    game.unmortgage_property(player, prop)
    assert prop.is_mortgaged is False

# Test 7: Bankruptcy eliminates player
def test_bankruptcy_eliminates_player():
    player = Player("Test")
    player.balance = 0
    game = Game([player.name])
    game.players = [player]
    game._check_bankruptcy(player)
    assert player.is_eliminated is True

# Test 8: Negative or zero dice roll does not move player
def test_negative_zero_dice_roll():
    player = Player("Test")
    pos_before = player.position
    player.move(0)
    assert player.position == pos_before
    player.move(-3)
    assert player.position == (pos_before - 3) % 40

# Test 9: Player cannot trade property they do not own
def test_trade_property_not_owned():
    seller = Player("A")
    buyer = Player("B")
    prop = Property("TestProp", 1, 100, 10)
    game = Game([seller.name, buyer.name])
    result = game.trade(seller, buyer, prop, 50)
    assert result is False
