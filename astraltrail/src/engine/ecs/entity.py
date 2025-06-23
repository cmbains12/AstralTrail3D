"""
entity.py

Provides the EntityManager class, which handles efficient allocation,
tracking, and recycling of entity IDs in a simulation or game engine
using a fixed-capacity freelist allocator backed by NumPy.

This module forms the foundation of a data-oriented ECS (Entity-Component-System),
enabling scalable real-time entity management with predictable memory use.
"""

import numpy as np
from numpy.typing import NDArray


class EntityManager:
    """
    A high-performance entity ID allocator and tracker for ECS systems.

    EntityManager assigns unique integer IDs to entities, supports constant-time
    allocation and deallocation, and reuses freed IDs using a LIFO (stack-based) freelist.

    Attributes:
        max_entities (int): Maximum number of entities that can exist simultaneously.
        next_id (int): The next fresh ID to be allocated (if freelist is empty).
        free_ids (NDArray[np.uint32]): Stack of recycled entity IDs.
        free_count (int): Number of available IDs in the freelist.
        alive_mask (NDArray[np.bool_]): Boolean mask indicating alive entity status.
    """

    def __init__(self, max_entities: int = 1_000_000) -> None:
        """
        Initialize the EntityManager with a fixed capacity.

        Args:
            max_entities (int): Maximum number of entities allowed.
        """
        self.max_entities: int = max_entities
        self.next_id: int = 0
        self.free_ids: NDArray[np.uint32] = np.empty(max_entities, dtype=np.uint32)
        self.free_count: int = 0
        self.alive_mask: NDArray[np.bool_] = np.zeros(max_entities, dtype=np.bool_)

    def create_entity(self) -> int:
        """
        Create a new entity and return its unique ID.

        Returns:
            int: The entity ID assigned.

        Raises:
            RuntimeError: If the maximum number of entities has been reached.
        """
        if self.free_count > 0:
            self.free_count -= 1
            eid: int = int(self.free_ids[self.free_count])
        elif self.next_id < self.max_entities:
            eid = self.next_id
            self.next_id += 1
        else:
            raise RuntimeError("Entity limit reached")

        self.alive_mask[eid] = True
        return eid

    def destroy_entity(self, eid: int) -> None:
        """
        Mark an entity as destroyed and recycle its ID.

        Args:
            eid (int): The ID of the entity to destroy.

        Raises:
            ValueError: If the entity is already destroyed or invalid.
        """
        if not self.is_alive(eid):
            raise ValueError(f"Entity {eid} is not alive")
        self.alive_mask[eid] = False
        self.free_ids[self.free_count] = eid
        self.free_count += 1

    def is_alive(self, eid: int) -> bool:
        """
        Check if a given entity ID is currently active.

        Args:
            eid (int): The entity ID to check.

        Returns:
            bool: True if the entity is alive, False otherwise.
        """
        return bool(self.alive_mask[eid])

    def reset(self) -> None:
        """
        Reset the EntityManager to its initial state.

        All entity IDs are invalidated, and all counters are cleared.
        This is useful for restarting a simulation or scene.
        """
        self.next_id = 0
        self.free_count = 0
        self.alive_mask.fill(False)
