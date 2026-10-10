"""
Player state and actions for World Magnates.
"""


from resource import Resource
from resource_pool import ResourcePool


class Player:
    """
    A player with money, board position, owned resources, and jokers.
    """

    def __init__(self, name: str, money: int = 200_000_000):
        """
        Create a player with default starting cash and empty holdings.

        Args:
            name: Display name of the player.
            money: Starting capital in game currency.
        """
        self.name: str = name
        self.money: int = money

        self.position: int = 0
        self.inventory: dict[str, int] = {}
        self.resource_pool: ResourcePool = ResourcePool({})
        self.jokers: int = 0

    def earn(self, amount: int) -> None:
        """
        Increase the player's money by a non-negative amount.
        """

        self._validate_amount(amount)
        self.money += amount

    def pay(self, amount: int) -> None:
        """Decrease the player's money if they can afford the payment.

        Raises:
            ValueError: If the amount exceeds available money.
        """
        self._validate_amount(amount)

        if amount > self.money:
            raise ValueError(
                f"{self.name} doesn't have enough money! "
                f"({self.money} < {amount})"
            )

        self.money -= amount

    def can_afford(self, amount: int) -> bool:
        """
        Return whether the player has at least the given amount.
        """

        self._validate_amount(amount)
        return self.money >= amount

    # Movement

    def move(self, amount: int, board_size: int) -> int:
        """Advance position on a circular board and return spaces moved.

        Args:
            amount: Number of spaces to move forward (non-negative).
            board_size: Number of spaces on the board (strictly positive).

        Returns:
            Net change in position (may differ from amount when wrapping).

        Raises:
            ValueError: If board_size or amount is invalid.
        """
        if board_size <= 0:
            raise ValueError("Board size must be strictly positive!")

        if amount < 0:
            raise ValueError("Movement amount cannot be negative!")

        old_position = self.position
        self.position = (self.position + amount) % board_size

        return self.position - old_position

    # Inventory (percent by resource type)

    def get_inventory_percent(self, resource_type: str) -> int:
        """
        Return total owned world-production percent for a resource type.
        """

        return self.inventory.get(resource_type, 0)

    def _change_inventory_percent(self, resource_type: str, delta: int
                                  ) -> None:
        """
        Apply a delta to inventory; remove the key when percent reaches zero.
        """

        if delta == 0:
            return

        total = self.inventory.get(resource_type, 0) + delta
        if total < 0:
            raise ValueError(
                f"{self.name} cannot reduce '{resource_type}' inventory "
                f"below zero ({self.inventory.get(resource_type, 0)}"
                f" + {delta})."
            )

        if total == 0:
            self.inventory.pop(resource_type, None)
        else:
            self.inventory[resource_type] = total

    # Resource pool (owned instances by location)

    def add_resource(self, continent: str, country: str, resource: Resource
                     ) -> None:
        """
        Take ownership of a resource instance and update inventory percent.
        """

        self.resource_pool.add_resource(
            continent,
            country,
            resource,
        )
        self._change_inventory_percent(resource.name, resource.percentage)

    def remove_resource(self, continent: str, country: str, resource: Resource
                        ) -> Resource:
        """
        Relinquish a resource instance and subtract its percent from inventory.
        """

        removed = self.resource_pool.remove_resource(
            continent,
            country,
            resource,
        )
        self._change_inventory_percent(removed.name, -removed.percentage)
        return removed

    def owns(self, continent: str, country: str, resource: Resource) -> bool:
        """
        Return whether the player owns the given resource instance.
        """

        return self.resource_pool.has_resource(
            continent,
            country,
            resource,
        )

    def get_resources(self, continent: str, country: str, resource_name: str
                      ) -> list[Resource]:
        """
        Return all owned instances of a resource type in a country.
        """

        return self.resource_pool.get_resources(
            continent,
            country,
            resource_name,
        )

    # Jokers

    def add_joker(self) -> None:
        """
        Grant one joker card to the player.
        """

        self.jokers += 1

    def use_joker(self) -> None:
        """Spend one joker.

        Raises:
            ValueError: If the player has no jokers left.
        """

        if self.jokers <= 0:
            raise ValueError(
                f"{self.name} has no jokers!"
            )

        self.jokers -= 1

    def has_joker(self) -> bool:
        """
        Return whether the player has at least one joker.
        """

        return self.jokers >= 1

    # Helpers

    @staticmethod
    def _validate_amount(amount: int) -> None:
        """
        Reject negative monetary amounts.

        Raises:
            ValueError: If amount is negative.
        """

        if amount < 0:
            raise ValueError("Amount cannot be negative!")

    def __str__(self) -> str:
        """
        Return a short summary for display.
        """

        return (
            f"{self.name} - "
            f"{self.money}€ - "
            f"{self.jokers} joker(s)"
        )
