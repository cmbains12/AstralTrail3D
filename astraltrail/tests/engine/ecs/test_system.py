import pytest
from unittest.mock import Mock

from astraltrail.src.engine.ecs.system import SystemManager

@pytest.fixture
def basic_systems():
    """
    Returns mocks for various test systems with unique side effects for verification.
    """
    pos_update = Mock(name="PositionUpdateSystem")
    logic_tick = Mock(name="LogicSystem")
    post_fx = Mock(name="PostProcessingSystem")
    return pos_update, logic_tick, post_fx

def test_register_and_run_systems(basic_systems):
    """
    Verify that registered systems are called in order during an update pass.
    """
    pos, logic, post = basic_systems
    sm = SystemManager()

    sm.register(pos, name="pos")
    sm.register(logic, name="logic")
    sm.register(post, name="post")

    sm.update(None, None, 0.1)

    pos.assert_called_once_with(None, None, 0.1)
    logic.assert_called_once_with(None, None, 0.1)
    post.assert_called_once_with(None, None, 0.1)

def test_system_order_is_preserved():
    """
    Ensure systems run in the order they were registered.
    """
    call_order = []
    
    def sys1(*args): call_order.append("sys1")
    def sys2(*args): call_order.append("sys2")
    def sys3(*args): call_order.append("sys3")

    sm = SystemManager()
    sm.register(sys1)
    sm.register(sys2)
    sm.register(sys3)

    sm.update(None, None, 0.016)

    assert call_order == ["sys1", "sys2", "sys3"]

def test_enable_disable_system():
    """
    Disabled systems should not be called during updates.
    """
    logic = Mock()
    sm = SystemManager()
    sm.register(logic, name="Logic")

    sm.set_enabled("Logic", False)
    sm.update(None, None, 0.1)

    logic.assert_not_called()

    sm.set_enabled("Logic", True)
    sm.update(None, None, 0.1)
    logic.assert_called_once()

def test_named_registration_and_lookup():
    """
    Test that systems can be identified by name.
    """
    ai_tick = Mock()
    sm = SystemManager()
    sm.register(ai_tick, name="AITick")
    sm.set_enabled("AITick", False)
    sm.update(None, None, 0.05)
    ai_tick.assert_not_called()

def test_tagged_system_filtering():
    """
    Verify tags can be used to filter system execution.
    """
    physics = Mock()
    render = Mock()
    debug = Mock()

    sm = SystemManager()
    sm.register(physics, name="physics", tags=["physics"])
    sm.register(render, name="render", tags=["render"])
    sm.register(debug, name="debug", tags=["debug"])

    sm.update(None, None, 0.1, include_tags=["physics", "render"])

    physics.assert_called_once()
    render.assert_called_once()
    debug.assert_not_called()

def test_phased_execution():
    """
    Confirm systems only run during their registered phase.
    """
    pre = Mock()
    main = Mock()
    post = Mock()

    sm = SystemManager()
    sm.register(pre, name="pre", phase="pre")
    sm.register(main, name="main", phase="update")
    sm.register(post, name="post", phase="post")

    # Only run 'update' phase
    sm.update(None, None, 0.016, phase="update")

    main.assert_called_once()
    pre.assert_not_called()
    post.assert_not_called()

def test_update_skips_disabled_systems():
    """
    Even if a system matches the current phase/tags, it should be skipped if disabled.
    """
    sys = Mock()
    sm = SystemManager()
    sm.register(sys, name="Sys", phase="update", tags=["core"])
    sm.set_enabled("Sys", False)

    sm.update(None, None, 0.016, include_tags=["core"])
    sys.assert_not_called()
