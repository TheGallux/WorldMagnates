"""Unit tests for the ResourcePool class."""

# The tests package is named ``unittest``, which shadows the stdlib module.
# pylint: disable=invalid-name,protected-access,too-many-public-methods,no-member

import json
import os
import tempfile
import unittest

from src.resource import Resource
from src.resource_pool import ResourcePool


class TestResourcePool(unittest.TestCase):
    """Tests for the ResourcePool class."""

    def setUp(self):
        """Create an empty pool and some resources."""
        self.pool = ResourcePool({})

        self.oil = Resource("Oil", 20, 5000)
        self.gold = Resource("Gold", 10, 8000)

        self.continent = "Europe"
        self.country = "France"

    def test_initialization_with_data(self):
        """The pool should retain the provided data."""
        data = {"Europe": {"France": {}}}
        pool = ResourcePool(data)

        self.assertIs(pool._data, data)

    def test_initialization_without_data(self):
        """Initializing without data should produce an empty pool."""
        pool = ResourcePool()

        self.assertEqual(pool._data, {})

    def test_add_resource(self):
        """A resource should be registered at the specified location."""
        self.pool.add_resource(
            self.continent,
            self.country,
            self.oil,
        )

        self.assertTrue(
            self.pool.has_resource(
                self.continent,
                self.country,
                self.oil,
            )
        )

    def test_add_resource_creates_nested_structure(self):
        """Adding a resource should create missing dictionary levels."""
        self.pool.add_resource("Europe", "France", self.oil)

        self.assertIn("Europe", self.pool._data)
        self.assertIn("France", self.pool._data["Europe"])
        self.assertIn("Oil", self.pool._data["Europe"]["France"])
        self.assertIn(
            self.oil.id,
            self.pool._data["Europe"]["France"]["Oil"],
        )

    def test_add_multiple_resources_of_same_type(self):
        """Different instances of one resource type should coexist."""
        another_oil = Resource("Oil", 15, 4000)

        self.pool.add_resource("Europe", "France", self.oil)
        self.pool.add_resource("Europe", "France", another_oil)

        resources = self.pool.get_resources("Europe", "France", "Oil")

        self.assertEqual(len(resources), 2)
        self.assertIn(self.oil, resources)
        self.assertIn(another_oil, resources)

    def test_add_resource_with_duplicate_id_raises_error(self):
        """Adding the same resource ID twice should raise ValueError."""
        self.pool.add_resource("Europe", "France", self.oil)

        with self.assertRaisesRegex(ValueError, "already exists"):
            self.pool.add_resource("Europe", "France", self.oil)

    def test_remove_resource(self):
        """Removing a resource should return it and remove it from the pool."""
        self.pool.add_resource("Europe", "France", self.oil)

        removed = self.pool.remove_resource(
            "Europe",
            "France",
            self.oil,
        )

        self.assertIs(removed, self.oil)
        self.assertFalse(
            self.pool.has_resource("Europe", "France", self.oil)
        )

    def test_remove_missing_resource_raises_key_error(self):
        """Removing a nonexistent resource should raise KeyError."""
        with self.assertRaisesRegex(KeyError, "not found"):
            self.pool.remove_resource(
                "Europe",
                "France",
                self.oil,
            )

    def test_get_resource(self):
        """A resource should be retrievable by type and ID."""
        self.pool.add_resource("Europe", "France", self.oil)

        result = self.pool.get_resource(
            "Europe",
            "France",
            "Oil",
            self.oil.id,
        )

        self.assertIs(result, self.oil)

    def test_get_missing_resource_raises_key_error(self):
        """Retrieving a nonexistent resource ID should raise KeyError."""
        self.pool.add_resource("Europe", "France", self.oil)

        with self.assertRaisesRegex(KeyError, "not found"):
            self.pool.get_resource(
                "Europe",
                "France",
                "Oil",
                -1,
            )

    def test_get_missing_resource_type_raises_key_error(self):
        """Retrieving a nonexistent resource type should raise KeyError."""
        with self.assertRaisesRegex(KeyError, "Resource type"):
            self.pool.get_resources(
                "Europe",
                "France",
                "Gold",
            )

    def test_get_resources(self):
        """All instances of a resource type should be returned."""
        another_oil = Resource("Oil", 15, 4000)

        self.pool.add_resource("Europe", "France", self.oil)
        self.pool.add_resource("Europe", "France", another_oil)

        resources = self.pool.get_resources("Europe", "France", "Oil")

        self.assertEqual(len(resources), 2)
        self.assertIn(self.oil, resources)
        self.assertIn(another_oil, resources)

    def test_has_resource(self):
        """has_resource should identify a registered resource."""
        self.pool.add_resource("Europe", "France", self.oil)

        self.assertTrue(
            self.pool.has_resource("Europe", "France", self.oil)
        )

    def test_has_resource_returns_false_for_missing_resource(self):
        """has_resource should return False for an unknown resource."""
        self.assertFalse(
            self.pool.has_resource("Europe", "France", self.oil)
        )

    def test_has_resource_returns_false_for_missing_continent(self):
        """has_resource should handle an unknown continent."""
        self.assertFalse(
            self.pool.has_resource("Asia", "France", self.oil)
        )

    def test_has_resource_returns_false_for_missing_country(self):
        """has_resource should handle an unknown country."""
        self.assertFalse(
            self.pool.has_resource("Europe", "Germany", self.oil)
        )

    def test_empty_copy(self):
        """An empty copy should preserve the location hierarchy."""
        self.pool.add_resource("Europe", "France", self.oil)
        self.pool.add_resource("Asia", "China", self.gold)

        copied_pool = self.pool.empty_copy()

        self.assertEqual(
            copied_pool._data,
            {
                "Europe": {"France": {}},
                "Asia": {"China": {}},
            },
        )

        self.assertFalse(
            copied_pool.has_resource("Europe", "France", self.oil)
        )

    def test_copy(self):
        """A deep copy should preserve resources without sharing objects."""
        self.pool.add_resource("Europe", "France", self.oil)

        copied_pool = self.pool.copy()

        copied_resource = copied_pool.get_resource(
            "Europe",
            "France",
            "Oil",
            self.oil.id,
        )

        self.assertIsNot(copied_pool, self.pool)
        self.assertIsNot(copied_resource, self.oil)
        self.assertEqual(copied_resource.name, self.oil.name)
        self.assertEqual(copied_resource.percentage, self.oil.percentage)
        self.assertEqual(copied_resource.price, self.oil.price)
        self.assertEqual(copied_resource.id, self.oil.id)

    def test_copy_is_independent(self):
        """Removing a resource from a copy should not affect the original."""
        self.pool.add_resource("Europe", "France", self.oil)

        copied_pool = self.pool.copy()
        copied_pool.remove_resource("Europe", "France", self.oil)

        self.assertTrue(
            self.pool.has_resource("Europe", "France", self.oil)
        )

    def test_repr(self):
        """The representation should include the underlying data."""
        self.pool.add_resource("Europe", "France", self.oil)

        self.assertEqual(
            repr(self.pool),
            f"ResourcePool({self.pool._data})",
        )

    def test_from_json(self):
        """Resources should be loaded from a JSON catalog."""
        data = {
            "Europe": {
                "France": {
                    "Oil1": {
                        "percentage": 20,
                        "price": 5000,
                    },
                    "Gold2": {
                        "percentage": 10,
                        "price": 8000,
                    },
                }
            }
        }

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            delete=False,
        ) as file:
            json.dump(data, file)
            path = file.name

        try:
            pool = ResourcePool.from_json(path)

            oil_resources = pool.get_resources(
                "Europe",
                "France",
                "Oil",
            )
            gold_resources = pool.get_resources(
                "Europe",
                "France",
                "Gold",
            )

            self.assertEqual(len(oil_resources), 1)
            self.assertEqual(oil_resources[0].percentage, 20)
            self.assertEqual(oil_resources[0].price, 5000)

            self.assertEqual(len(gold_resources), 1)
            self.assertEqual(gold_resources[0].percentage, 10)
            self.assertEqual(gold_resources[0].price, 8000)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
