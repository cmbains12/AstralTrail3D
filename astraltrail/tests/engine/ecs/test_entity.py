import pytest
import numpy as np
from astraltrail.src.engine.ecs.entity import EntityManager


def test_entity_creation_and_alive_status():
    """Entities should be created and marked alive."""
    em = EntityManager(max_entities=10)

    eid = em.create_entity()
    assert isinstance(eid, int)
    assert em.is_alive(eid) is True


def test_entity_destruction_and_reuse():
    """Destroyed entities should be marked dead and their IDs reused."""
    em = EntityManager(max_entities=5)

    eid1 = em.create_entity()
    em.destroy_entity(eid1)

    assert not em.is_alive(eid1)

    # ID should be reused (since it goes to the freelist)
    eid2 = em.create_entity()
    assert eid2 == eid1
    assert em.is_alive(eid2)


def test_multiple_entities_up_to_capacity():
    """You should be able to create up to max_entities entities."""
    em = EntityManager(max_entities=3)

    eids = [em.create_entity() for _ in range(3)]
    assert len(set(eids)) == 3

    with pytest.raises(RuntimeError):
        em.create_entity()  # Should raise when full


def test_double_destruction_error():
    """Destroying an entity twice should raise an error."""
    em = EntityManager(max_entities=2)
    eid = em.create_entity()
    em.destroy_entity(eid)

    with pytest.raises(ValueError):
        em.destroy_entity(eid)


def test_reset_clears_all_entities():
    """Resetting the manager should remove all entities and clear counters."""
    em = EntityManager(max_entities=5)

    eids = [em.create_entity() for _ in range(3)]
    for eid in eids:
        assert em.is_alive(eid)

    em.reset()

    for eid in eids:
        assert not em.is_alive(eid)

    # After reset, IDs should start from 0 again
    new_eid = em.create_entity()
    assert new_eid == 0


def test_recycling_multiple_ids_in_lifo_order():
    """Freelist should behave like a stack (LIFO): most recently destroyed gets reused first."""
    em = EntityManager(max_entities=5)

    eid1 = em.create_entity()
    eid2 = em.create_entity()
    eid3 = em.create_entity()

    em.destroy_entity(eid2)
    em.destroy_entity(eid3)

    # eid3 should come back first, because of LIFO, and stack structure
    reused1 = em.create_entity()
    reused2 = em.create_entity()

    assert reused1 == eid3
    assert reused2 == eid2
