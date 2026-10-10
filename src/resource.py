"""
Resource model for World Magnates board game assets.
"""


class Resource:
    """
    A purchasable resource with market share and price.
    """

    # pylint: disable=too-few-public-methods

    INSTANCE_COUNT = 0

    def __init__(self, name: str, percentage: int, price: int):
        """
        Create a resource and assign it a unique instance id.

        Args:
            name: Resource type name (trailing digits in JSON are stripped
                                      upstream).
            percentage: Share of world production, in percent.
            price: Purchase price in game currency.
        """

        self.name = name
        self.percentage = percentage
        self.price = price
        self.id = Resource.INSTANCE_COUNT

        Resource.INSTANCE_COUNT += 1

    def __repr__(self) -> str:
        """
        Return a debug representation of this resource.
        """

        return (
            "Resource("
            f"name={self.name}, "
            f"percentage={self.percentage}, "
            f"price={self.price}"
            ")"
        )
