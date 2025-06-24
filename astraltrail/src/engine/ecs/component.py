import numpy as np

class ComponentManager:
    """
    Manages component data for all entities using a Struct-of-Arrays (SoA) layout.
    Supports both sparse (opt-in) and dense (defaulted) storage modes.
    
    Responsibilities:
    - Registering and initializing component arrays
    - Adding/removing component data for specific entities
    - Tracking component ownership per entity
    - Querying entities with specific component combinations
    - Maintaining high-performance layout for simulation
    """

    def __init__(self, max_entities: int):
        self.max_entities = max_entities

        # Registered component arrays: {component_name: np.ndarray}
        self.components = {}

        # Sparse entity masks: {component_name: set(entity_id)}
        self.entity_masks = {}

        # Component metadata: {component_name: {"shape": ..., "dtype": ..., "sparse": ...}}
        self.meta = {}

    def register_component(self, name: str, shape: tuple, dtype=np.float32, sparse: bool = False):
        """
        Register a new component type with its shape, dtype, and sparsity mode.
        Allocates memory in a flat SoA-compatible format.
        """
        if name in self.components:
            raise ValueError(f"Component '{name}' is already registered.")
        
        self.meta[name] = {
            "shape": shape,
            "dtype": dtype,
            "sparse": sparse
        }

        # Allocate component storage array (always full size)
        self.components[name] = np.zeros((self.max_entities, *shape), dtype=dtype)

        # For sparse components, we need to track which entities actually use it
        if sparse:
            self.entity_masks[name] = set()

    def add_component(self, entity_id: int, name: str, value):
        """
        Assign a component value to an entity. For sparse components,
        registers the entity in the sparse set.
        """
        if name not in self.components:
            raise KeyError(f"Component '{name}' is not registered.")

        self.components[name][entity_id] = value

        if self.meta[name]["sparse"]:
            self.entity_masks[name].add(entity_id)

    def has_component(self, entity_id: int, name: str) -> bool:
        """
        Check whether an entity currently holds a given component.
        """
        if name not in self.components:
            return False

        if self.meta[name]["sparse"]:
            return entity_id in self.entity_masks[name]
        else:
            return True  # dense components always exist

    def remove_component(self, entity_id: int, name: str):
        """
        Remove a component from an entity. Only valid for sparse components.
        """
        if name not in self.components:
            raise KeyError(f"Component '{name}' is not registered.")

        if not self.meta[name]["sparse"]:
            raise ValueError(f"Cannot remove dense component '{name}'")

        self.entity_masks[name].discard(entity_id)
        self.components[name][entity_id] = 0  # optional: reset value

    def get_component_data(self, name: str) -> np.ndarray:
        """
        Access the full component array for direct manipulation or slicing.
        """
        if name not in self.components:
            raise KeyError(f"Component '{name}' is not registered.")
        return self.components[name]

    def query_entities_with(self, component_names: list[str]) -> set[int]:
        """
        Return a set of entity IDs that have all of the specified components.
        Used for system queries.
        """
        if not component_names:
            return set()

        # Start with all entity IDs if the first is dense
        first = component_names[0]
        if not self.meta[first]["sparse"]:
            candidate_set = set(range(self.max_entities))
        else:
            candidate_set = set(self.entity_masks[first])

        # Intersect with the other components
        for name in component_names[1:]:
            if name not in self.components:
                raise KeyError(f"Component '{name}' is not registered.")
            if self.meta[name]["sparse"]:
                candidate_set &= self.entity_masks[name]
            # Dense components are assumed to exist for all entities

        return candidate_set

    def cleanup_entity(self, entity_id: int):
        """
        Remove all sparse components associated with a deleted or recycled entity.
        This should be called whenever an entity is destroyed.
        """
        for name, meta in self.meta.items():
            if meta["sparse"]:
                self.entity_masks[name].discard(entity_id)
                self.components[name][entity_id] = 0  # optional: clear memory
