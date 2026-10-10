"""Unit tests for the Player class."""

# The tests package is named ``unittest``, which shadows the stdlib module.
# pylint: disable=invalid-name,no-member

import unittest

from src.player import Player
from src.resource import Resource


class TestPlayer(unittest.TestCase):
    """Tests for the Player class."""

    def setUp(self):
        """Create a player and sample resources before each test."""
        Resource.INSTANCE_COUNT = 0
        self.player = Player("Alice")
        self.continent = "Europe"
        self.country = "France"
        self.oil = Resource("Oil", 20, 5000)

    def test_initialization(self):
        """A new player should start with default money and empty holdings."""
        self.assertEqual(self.player.name, "Alice")
        self.assertEqual(self.player.money, 200_000_000)
        self.assertEqual(self.player.position, 0)
        self.assertEqual(self.player.inventory, {})
        self.assertEqual(self.player.jokers, 0)
        self.assertFalse(
            self.player.owns(self.continent, self.country, self.oil)
        )

    def test_earn_and_pay(self):
        """Earn and pay should update money when affordable."""
        self.player.earn(1_000)
        self.assertEqual(self.player.money, 200_001_000)

        self.player.pay(1_000)
        self.assertEqual(self.player.money, 200_000_000)

    def test_pay_insufficient_funds_raises(self):
        """Paying more than available money should raise ValueError."""
        with self.assertRaisesRegex(ValueError, "enough money"):
            self.player.pay(self.player.money + 1)

    def test_can_afford(self):
        """can_afford should reflect current money."""
        self.assertTrue(self.player.can_afford(100))
        self.assertFalse(self.player.can_afford(self.player.money + 1))

    def test_move(self):
        """move should advance position on a circular board."""
        delta = self.player.move(3, board_size=10)
        self.assertEqual(delta, 3)
        self.assertEqual(self.player.position, 3)

    def test_move_wraps_around_board(self):
        """Position should wrap when moving past the last space."""
        self.player.position = 8
        self.player.move(5, board_size=10)
        self.assertEqual(self.player.position, 3)

    def test_add_resource_updates_inventory_and_pool(self):
        """Acquiring a resource should update both pool and inventory."""
        self.player.add_resource(self.continent, self.country, self.oil)

        self.assertTrue(
            self.player.owns(self.continent, self.country, self.oil)
        )
        self.assertEqual(self.player.inventory, {"Oil": 20})
        self.assertEqual(self.player.get_inventory_percent("Oil"), 20)

    def test_remove_resource_clears_inventory_at_zero(self):
        """Removing the last instance should drop the inventory key."""
        self.player.add_resource(self.continent, self.country, self.oil)
        self.player.remove_resource(self.continent, self.country, self.oil)

        self.assertEqual(self.player.inventory, {})
        self.assertEqual(self.player.get_inventory_percent("Oil"), 0)

    def test_inventory_sums_same_resource_type(self):
        """Multiple instances of one type should aggregate in inventory."""
        another_oil = Resource("Oil", 15, 4000)
        self.player.add_resource(self.continent, self.country, self.oil)
        self.player.add_resource(self.continent, self.country, another_oil)

        self.assertEqual(self.player.inventory, {"Oil": 35})

    def test_jokers(self):
        """Jokers should be added, spent, and queried correctly."""
        self.assertFalse(self.player.has_joker())

        self.player.add_joker()
        self.assertTrue(self.player.has_joker())

        self.player.use_joker()
        self.assertFalse(self.player.has_joker())

    def test_use_joker_without_stock_raises(self):
        """Using a joker with none left should raise ValueError."""
        with self.assertRaisesRegex(ValueError, "no jokers"):
            self.player.use_joker()

    def test_str(self):
        """String form should include name, money, and jokers."""
        self.player.add_joker()
        self.assertEqual(
            str(self.player),
            "Alice - 200000000€ - 1 joker(s)",
        )


if __name__ == "__main__":
    unittest.main()
