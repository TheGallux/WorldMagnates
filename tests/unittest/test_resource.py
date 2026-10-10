"""Unit tests for the Resource model."""

# The tests package is named ``unittest``, which shadows the stdlib module.
# pylint: disable=invalid-name,no-member

import unittest

from src.resource import Resource


class TestResource(unittest.TestCase):
    """Tests for the Resource class."""

    def setUp(self):
        """Record the instance counter before each test."""
        self.initial_count = Resource.INSTANCE_COUNT

    def test_initialization(self):
        """A resource should store its attributes correctly."""
        resource = Resource("Oil", 20, 5000)

        self.assertEqual(resource.name, "Oil")
        self.assertEqual(resource.percentage, 20)
        self.assertEqual(resource.price, 5000)

    def test_unique_ids(self):
        """Each resource should receive a unique ID."""
        resource1 = Resource("Oil", 20, 5000)
        resource2 = Resource("Oil", 30, 6000)

        self.assertNotEqual(resource1.id, resource2.id)
        self.assertEqual(resource2.id, resource1.id + 1)

    def test_id_starts_at_instance_count(self):
        """The resource ID should match the current instance counter."""
        resource = Resource("Gold", 10, 1000)

        self.assertEqual(resource.id, self.initial_count)

    def test_instance_count_increments(self):
        """Creating a resource should increment the instance counter."""
        Resource("Coal", 15, 2000)

        self.assertEqual(
            Resource.INSTANCE_COUNT,
            self.initial_count + 1,
        )

    def test_repr(self):
        """The representation should contain the resource attributes."""
        resource = Resource("Oil", 20, 5000)

        expected = (
            "Resource("
            "name=Oil, "
            "percentage=20, "
            "price=5000"
            ")"
        )

        self.assertEqual(repr(resource), expected)


if __name__ == "__main__":
    unittest.main()
