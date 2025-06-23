# NumPy ECS: A Data-Oriented Simulation Framework

A fast, flexible Entity-Component-System (ECS) engine in Python built from first principles using NumPy. Designed for real-time simulation, large-scale virtual environments, and future integration with AI, voxel systems, and custom game logic. This ECS is not just a game engine submodule—it’s the foundation of a simulation substrate.

## Project Philosophy

Traditional object-oriented game engines struggle under simulation-heavy loads. This project embraces a **data-oriented design (DoD)** architecture, leveraging:
- **Contiguous memory layouts** (via NumPy arrays)
- **Cache-friendly processing**
- **Parallelism-ready separation of data and behavior**
- **Predictable, inspectable, deterministic state flow**

## Key Features

### Entity Management
- Fast allocation and ID recycling with freelist
- Fixed-capacity storage for performance predictability
- Bitmask-based "alive" checks

### Component System
- Dense and sparse component layouts
- Per-type NumPy arrays for simulation-scale data throughput
- Dynamic registration and tracking of component types

### System Scheduling
- Signature-based system execution (requires component sets)
- Decoupled update logic from data storage
- Frame loop orchestration or external loop integration

### Debugging & Introspection (planned)
- Live entity inspector/debug HUD
- ECS state serialization and replay tools
- Per-system timing/profiling hooks

### Archetype Optimization (advanced/future)
- Grouping entities by component composition
- Minimized branching and indirect access
- Batched iteration and SIMD-prepared inner loops

## Example Use Case

```python
from ecs.entity import EntityManager
from ecs.components import Position, Velocity
from ecs.systems import PhysicsSystem

em = EntityManager()
eid = em.create_entity()

# Attach components (API in dev)
Position[eid] = (0.0, 0.0)
Velocity[eid] = (1.0, 0.0)

physics = PhysicsSystem()
physics.update(dt=0.016)  # Advance by 16 ms
