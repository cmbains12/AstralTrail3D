class System:
    """
    Represents a single ECS system with optional metadata.
    
    Attributes:
        fn (callable): The system function to execute (takes cm, em, dt).
        name (str): Unique name for identification and debugging.
        enabled (bool): Whether the system is currently active.
        tags (set): Optional labels for filtering execution (e.g. 'physics', 'render').
        phase (str): Which update phase the system belongs to ('pre', 'update', 'post').
    """
    def __init__(self, fn, name=None, enabled=True, tags=None, phase="update"):
        self.fn = fn
        self.name = name or fn.__name__
        self.enabled = enabled
        self.tags = set(tags or [])
        self.phase = phase

class SystemManager:
    """
    Core ECS system scheduler. Registers and executes systems based on phase, tag,
    and enable/disable status.

    Usage:
        sm = SystemManager()
        sm.register(my_physics_system, tags=["physics"], phase="update")
        sm.update(cm, em, dt)  # runs all 'update'-phase systems
    """
    def __init__(self):
        self.systems = []

    def register(self, fn, name=None, tags=None, phase="update"):
        """
        Register a system function.

        Args:
            fn (callable): The system function, taking (cm, em, dt).
            name (str): Optional name override (default is function name).
            tags (list[str]): Optional list of tags (e.g. ['physics', 'network']).
            phase (str): Execution phase ('pre', 'update', or 'post').
        """
        system = System(fn, name=name, tags=tags, phase=phase)
        self.systems.append(system)

    def set_enabled(self, name: str, enabled: bool):
        """
        Enable or disable a system by name.

        Args:
            name (str): The name of the system to toggle.
            enabled (bool): True to enable, False to disable.
        """
        for sys in self.systems:
            if sys.name == name:
                sys.enabled = enabled

    def update(self, cm, em, dt, phase="update", include_tags=None):
        """
        Execute all systems matching the current phase and (optionally) tags.

        Args:
            cm (ComponentManager): Component manager to pass to each system.
            em (EntityManager): Entity manager to pass to each system.
            dt (float): Delta time for the update.
            phase (str): Phase to execute ('pre', 'update', or 'post').
            include_tags (list[str]): If set, only systems with these tags will run.
        """
        include_tags = set(include_tags or [])
        for sys in self.systems:
            if not sys.enabled:
                continue
            if sys.phase != phase:
                continue
            if include_tags and not (sys.tags & include_tags):
                continue
            sys.fn(cm, em, dt)
