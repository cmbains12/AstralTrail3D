import numpy as np
import pytest
from astraltrail.src.engine.ecs.component import ComponentManager
from astraltrail.src.engine.ecs.entity import EntityManager

MAX_ENTITIES = 1000

@pytest.fixture
def setup_ecs():
    """
    Pytest fixture to initialize a fresh ECS with static component definitions.
    Registers a dense 'Position' component and a sparse 'Velocity' component.
    """
    em = EntityManager(max_entities=MAX_ENTITIES)
    cm = ComponentManager(max_entities=MAX_ENTITIES)
    
    # Register known component types
    cm.register_component("Position", shape=(2,), dtype=np.float32, sparse=False)
    cm.register_component("Velocity", shape=(2,), dtype=np.float32, sparse=True)

    return em, cm

def test_register_and_add_static_component(setup_ecs):
    """
    Test that a dense static component ('Position') can be added and retrieved.
    """
    em, cm = setup_ecs
    eid = em.create_entity()
    
    cm.add_component(eid, "Position", [1.0, 2.0])
    data = cm.get_component_data("Position")
    
    assert np.allclose(data[eid], [1.0, 2.0])
    assert cm.has_component(eid, "Position")

def test_add_sparse_component(setup_ecs):
    """
    Test adding and verifying a sparse component ('Velocity') for a single entity.
    Confirm that other entities do not get the component by default.
    """
    em, cm = setup_ecs
    eid = em.create_entity()
    
    cm.add_component(eid, "Velocity", [0.1, -0.2])
    assert cm.has_component(eid, "Velocity")

    data = cm.get_component_data("Velocity")
    assert np.allclose(data[eid], [0.1, -0.2])
    
    # Confirm no leakage to other entities
    other_eid = em.create_entity()
    assert not cm.has_component(other_eid, "Velocity")

def test_dynamic_component_registration(setup_ecs):
    """
    Test registering a new component at runtime and verifying its layout.
    """
    _, cm = setup_ecs
    cm.register_component("Energy", shape=(1,), dtype=np.float32, sparse=True)

    assert "Energy" in cm.components
    assert cm.components["Energy"].shape == (MAX_ENTITIES, 1)

def test_dense_sparse_behavior(setup_ecs):
    """
    Confirm that dense components are initialized automatically,
    and sparse components are not.
    """
    em, cm = setup_ecs
    eid = em.create_entity()

    # Dense components should be initialized to zeros
    assert cm.has_component(eid, "Position")
    assert np.allclose(cm.get_component_data("Position")[eid], [0.0, 0.0])

    # Sparse components must be explicitly added
    assert not cm.has_component(eid, "Velocity")

def test_query_entities_with_components(setup_ecs):
    """
    Test querying for entities that contain multiple specific components.
    This simulates system-level filtering.
    """
    em, cm = setup_ecs
    ids = [em.create_entity() for _ in range(10)]
    
    for eid in ids[:5]:
        cm.add_component(eid, "Position", [eid, eid])
    for eid in ids[3:8]:
        cm.add_component(eid, "Velocity", [0.0, 0.0])
    
    # Expect entities 3 and 4 to have both Position and Velocity
    result = cm.query_entities_with(["Position", "Velocity"])
    assert result == set(ids[3:8])

def test_overwrite_component_data(setup_ecs):
    """
    Test that re-adding a component for an entity updates its stored value.
    """
    em, cm = setup_ecs
    eid = em.create_entity()
    
    cm.add_component(eid, "Position", [1, 1])
    cm.add_component(eid, "Position", [2, 2])
    
    assert np.allclose(cm.get_component_data("Position")[eid], [2, 2])

def test_invalid_component_addition(setup_ecs):
    """
    Adding a component that hasn't been registered should raise a KeyError.
    """
    em, cm = setup_ecs
    eid = em.create_entity()
    
    with pytest.raises(KeyError):
        cm.add_component(eid, "DoesNotExist", [0])

def test_mass_component_addition(setup_ecs):
    """
    Stress test: add sparse component 'Velocity' to all entities and validate correctness.
    This ensures the system scales and doesn't leak across entity slots.
    """
    em, cm = setup_ecs
    for i in range(MAX_ENTITIES):
        eid = em.create_entity()
        cm.add_component(eid, "Velocity", [float(i), float(-i)])
    
    velocity_data = cm.get_component_data("Velocity")
    assert np.allclose(velocity_data[:MAX_ENTITIES, 0], np.arange(MAX_ENTITIES))

def test_memory_layout_is_soa(setup_ecs):
    """
    Ensure that component arrays are stored in SoA layout (C-contiguous),
    which is essential for cache efficiency and vectorization.
    """
    _, cm = setup_ecs
    pos = cm.get_component_data("Position")
    
    assert pos.flags['C_CONTIGUOUS']
    assert pos.shape == (MAX_ENTITIES, 2)
    assert pos.dtype == np.float32

def test_can_remove_component(setup_ecs):
    """
    Verify that removing a component works and the entity no longer reports it.
    """
    em, cm = setup_ecs
    eid = em.create_entity()
    
    cm.add_component(eid, "Velocity", [1, 2])
    cm.remove_component(eid, "Velocity")
    
    assert not cm.has_component(eid, "Velocity")

def test_can_remove_entity_and_cleanup(setup_ecs):
    """
    Ensure that destroying an entity and cleaning up removes all associated components.
    """
    em, cm = setup_ecs
    eid = em.create_entity()
    
    cm.add_component(eid, "Position", [5, 5])
    cm.add_component(eid, "Velocity", [1, -1])

    em.destroy_entity(eid)
    cm.cleanup_entity(eid)

    # Only sparse components can be cleaned up
    assert not cm.has_component(eid, "Velocity")

    # Dense component still exists
    assert cm.has_component(eid, "Position")
