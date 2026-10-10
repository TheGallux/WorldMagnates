"""
Hierarchical storage of resources by continent and country.
"""

import json
import re
from copy import deepcopy

from .resource import Resource


class ResourcePool:
    """
    Nested map of continent -> country -> resource name -> id -> Resource.
    """

    def __init__(self, data=None):
        """
        Initialize an empty resource pool.
        """

        self._data = data if data is not None else {}

    @classmethod
    def from_json(cls, path: str) -> "ResourcePool":
        """
        Load resources from a JSON file into a new pool.

        Args:
            path: Filesystem path to the JSON catalog.

        Returns:
            A pool populated with all resources from the file.
        """

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        pool = cls()

        for continent, countries in data.items():
            for country, resources in countries.items():
                for resource_name, values in resources.items():
                    # removes the trailing numbers
                    name = re.sub(r"\d+$", "", resource_name)

                    resource = Resource(
                        name=name,
                        percentage=values["percentage"],
                        price=values["price"],
                    )

                    pool.add_resource(
                        continent,
                        country,
                        resource,
                    )

        return pool

    def empty_copy(self) -> "ResourcePool":
        """
        Return a pool with the same structure but no resource instances.
        """

        return ResourcePool(
            {
                continent: {
                    country: {}
                    for country in countries
                }
                for continent, countries in self._data.items()
            }
        )

    def copy(self) -> "ResourcePool":
        """
        Return a deep copy of this pool and all contained resources.
        """

        return ResourcePool(deepcopy(self._data))

    def add_resource(self, continent: str, country: str, resource: Resource
                     ) -> None:
        """
        Register a resource under the given continent and country.

        Raises:
            ValueError: If a resource with the same id already exists there.
        """

        self._data.setdefault(continent, {})
        self._data[continent].setdefault(country, {})

        resources = self._data[continent][country]

        resources.setdefault(resource.name, {})

        if resource.id in resources[resource.name]:
            raise ValueError(
                f"Resource with ID {resource.id} already exists "
                f"in '{continent}/{country}'."
            )

        resources[resource.name][resource.id] = resource

    def remove_resource(self, continent: str, country: str, resource: Resource
                        ) -> Resource:
        """
        Remove and return a resource from the pool.

        Raises:
            KeyError: If the resource is not present at that location.
        """

        resources = self._get_resources(continent, country, resource.name)

        try:
            return resources.pop(resource.id)
        except KeyError as exc:
            raise KeyError(
                f"Resource with ID {resource.id} not found "
                f"in '{continent}/{country}'."
            ) from exc

    def get_resource(self, continent: str, country: str, resource_name: str,
                     resource_id: int) -> Resource:
        """
        Return a single resource by name and instance id.

        Raises:
            KeyError: If the resource type or id is missing.
        """

        resources = self._get_resources(
            continent,
            country,
            resource_name,
        )

        try:
            return resources[resource_id]
        except KeyError as exc:
            raise KeyError(
                f"Resource with ID {resource_id} not found "
                f"in '{continent}/{country}/{resource_name}'."
            ) from exc

    def get_resources(self, continent: str, country: str, resource_name: str
                      ) -> list[Resource]:
        """
        Return all resource instances of a given type in a country.
        """

        return list(
            self._get_resources(
                continent,
                country,
                resource_name,
            ).values()
        )

    def has_resource(self, continent: str, country: str, resource: Resource
                     ) -> bool:
        """
        Return whether the exact resource instance exists in the pool.
        """

        return (
            continent in self._data
            and country in self._data[continent]
            and resource.name in self._data[continent][country]
            and resource.id in self._data[continent][country][resource.name]
        )

    def _get_resources(self, continent: str, country: str, resource_name: str
                       ) -> dict[int, Resource]:
        """
        Return the id -> Resource map for a resource type in a country.

        Raises:
            KeyError: If continent, country, or resource type is missing.
        """

        try:
            return self._data[continent][country][resource_name]
        except KeyError as exc:
            raise KeyError(
                f"Resource type '{resource_name}' not found "
                f"in '{continent}/{country}'."
            ) from exc

    def __repr__(self) -> str:
        """
        Return a debug representation of the underlying data.
        """
        return f"ResourcePool({self._data})"
