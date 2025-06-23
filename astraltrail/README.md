# Astral Engine

**Astral Engine** is a custom-built, high-performance voxel simulation engine and the foundation of the solo-developed game **Astral Trail**. The goal is to unify rendering, physics, logic, and AI under a coherent simulation framework that enables scalable, emergent systems without resorting to traditional game engine abstractions.

---

## Architectural Design Goals

Astral Engine is architected to serve not just as a rendering or gameplay framework, but as a platform for simulation-native software development. Every system is designed with careful tradeoffs between performance, clarity, and creative control. If a paradigm or a principle can be justified to serve at least one, or possible all guiding values, it is then elevated and explored to maximize its impact and minimize its trade-offs.  The biggest contribution to success might be found in powerful combinations and fresh-minded approaches to well-tested ideas.  Architecture is anchored by the following design goals:
 
### High-Fidelity, Cache-Aware Data Pipelines

Simulation and rendering systems are built around memory-contiguous, batch-processed data pipelines that maximize CPU and GPU cache usage. Data structures and processing flows are explicitly structured to reduce branching, indirection, and unnecessary state duplication—enabling high-throughput, low-latency processing for physics, rendering, and AI alike.

This approach draws inspiration from Data-Oriented Design (DOD) and modern systems engineering to deliver performance without premature specialization or hand-tuned hacks. The result is predictable, inspectable, and maintainable code that remains performant across scale.

### Complexity Where It Matters

The engine embraces complexity in the simulation core—where nuance, precision, and systemic depth matter—but distills away friction in developer-facing systems. APIs, hooks, and scripting interfaces are designed to reduce mental overhead and cognitive branching, making it easier for developers (including future contributors and modders) to reason about behavior, stack systems, and extend capabilities without breakage.

- This structured simplicity supports:
- Fast iteration and debugging
- Modular, composable gameplay systems
- Safe and intuitive control over emergent behavior

### Extensible, Composable System Stack

Modding and long-term extensibility are central to the architecture. Systems can be composed and extended cleanly, even when interdependent. Examples include:

- Layered physics systems (grid-based collision, SDF deformation, material flow)
- Hybrid symbolic & perceptual AI (e.g. Astral observing the world, not querying internals)
- Reversible time systems, saliency maps, and memory overlays

All such systems are designed to be stackable, inspectable, and interoperable—without entangling core simulation logic.

### Threading and Memory Safety via DSL Contract

To enable collaboration, modding, and parallelism without sacrificing safety, Astral Engine will integrate a custom-designed scripting language and execution contract. This DSL is purpose-built for:

- Controlled simulation access and memory sandboxing
- Safe threading and parallel execution
- High-level gameplay logic with low-level guarantees

This forms the foundation for future multiplayer/server support, dynamic physics extensions, and user-driven AI and scripting—without introducing nondeterminism or architectural brittleness.

### Performance Scaling and Ecological Considerations

The engine is being developed with flexible scaling in mind. Systems dynamically adjust fidelity based on distance, activity, or system load. This reduces draw on local resources, enabling:

- Smooth gameplay on a wide range of hardware
- Graceful degradation for large world sizes or multiplayer scope
- Environmentally conscious resource usage for local and hosted simulations

### Vision Beyond Gameplay

Astral Engine is informed by a broad cross-disciplinary foundation: physics, simulation engineering, user experience, game design, AI systems, and software architecture. It is designed to:

- Achieve feature parity with commercial and research-grade engines in select domains
- Enable gameplay mechanics grounded in real system dynamics
- Offer an engine-level substrate for academic exploration, simulation R&D, and future AI-native tooling

This positions Astral Engine not only as a vehicle for solo game development, but as a platform for simulation-first software that bridges play, research, and computational design.

---

## Core Principles

### Unified Substrate

The engine is built around a shared data representation used by all major systems—rendering, physics, logic, and AI. This helps eliminate duplicated state, makes debugging less brittle, and opens the door to tight inter-system feedback loops and emergent behavior.

### Hybrid Grid and SDF Architecture

A hybrid spatial system is used: a voxel grid provides spatial grounding and fast indexing for simulation, while layered Signed Distance Fields (SDFs) allow smooth deformations, dynamic resolution, and high-fidelity effects. The grid offers efficient chunking, local transforms, and gameplay grounding; the SDF layer enables flexible rendering and continuous simulation.

### Two-Space Fidelity Model

Systems can move between grid and SDF representations depending on draw distance, interaction requirements, and computational budget. This allows for dynamic level-of-detail (LOD) in both simulation and graphics—near the player, fidelity is high; far away, representation becomes coarser or symbolic. The engine can scale simulation detail without splitting systems into parallel implementations.

### Data-Oriented Design (DOD)

Core systems follow structured, cache-friendly data access patterns. Logic is applied over raw data tables instead of through nested object hierarchies. This improves performance, especially on modern hardware, and allows for clean system decoupling and better predictability.

### ECS-Inspired System Architecture

Components are kept simple and data-driven, while systems apply transformations and logic in a modular, stateless manner. The engine doesn't enforce a strict ECS framework, but uses its core strengths—separation of logic and data, modular design, and composability—to make simulation features easier to implement, test, and extend.

---

## Why It Matters: Gameplay, Development, and Performance

### Simulation-Driven Gameplay

By grounding all systems in a unified substrate and spatial logic, game elements behave consistently and respond to player input in believable, systemic ways. Deformable terrain, destructible structures, AI agents, and world mechanics all emerge from shared data layers. This opens up design space for emergent mechanics and player creativity without bespoke scripting.

### Designed for Solo and Systems-Oriented Development

This engine doesn't hide complexity behind pre-baked abstractions—it exposes how systems work, how they interact, and how data flows through them. This is ideal for developers who want control and visibility. It's also useful for solo developers who can’t afford black-box behavior or ambiguous bugs. The architecture minimizes unintended coupling, encourages experimentation, and supports traceable, introspectable logic flows.

### Efficient Use of System Resources

Because the engine supports dynamic fidelity scaling across simulation and rendering, system resources are focused where they're needed most. Background areas or inactive systems can downgrade gracefully, while active scenes maintain full fidelity. This allows for larger worlds, richer simulations, and better performance without overly aggressive culling or fakery.

---

## Architecture Diagrams

### High Level System Graphing
                    +------------------------------+
                    |        Game Application      |
                    +--------------+---------------+
                                   |
                    Calls into Engine API Interface via DSL
                                   |
                    +--------------v--------------------------+
                    |      Astral Engine Core                 |
                    |(Modular Runtime and DSL JIT Compilation)|
                    +--------------+--------------------------+
                                   |
                   Delegates Simulation Tasks via tight DSL 
                   typing and schedule protocols and rules.
                   The DSL is an abstraction and execution of
                   these rules and protocols
                                   |
                    +--------------v---------------+
                    |  Thread Scheduler & Safety   |  <== Firewall Layer
                    |       (Execution Control)    |
                    +--------------+---------------+
                                   |
                          +------------------------------+
                          |     Simulation Pipeline      |
                          |  (Threaded, Modular, Safe)   |
                          +-------------+----------------+
                                        |
        +-------------------------------+--------------------------------+
        |                               |                                |
+---------------+           +--------------------+           +--------------------+
|   Rendering   |           |      Physics       |           |        AI / Logic  |
|   Pipeline    |           |      Pipeline      |           |      Pipeline      |
+-------+-------+           +---------+----------+           +---------+----------+
        \\                          //                           //
         \\                        //                           //
          +------------------------v---------------------------+
          |              Shared SDF Field Engine               |  <== Smooth geometry, sampling, distance ops
          +------------------------+---------------------------+
                                   ↕
          +------------------------v---------------------------+
          |               Voxel Grid Engine (Chunks)           |  <== Discrete spatial grounding, simulation cores
          +------------------------+---------------------------+
                                   ↕
          +------------------------v---------------------------+
          |              ECS Substrate / Data Layer            |  <== Unified entity/component storage
          | (Memory-local, cache-aware, job-schedulable data)  |
          +----------------------------------------------------+


---

## Current Focus

Development is currently focused on the most foundational parts of the simulation stack:

- Voxel/SDF hybrid terrain systems and memory-efficient spatial representations
- Collision and physics prototypes that operate directly on volumetric fields
- Simulation-first system scaffolding that prioritizes dynamic world behavior over static asset pipelines

Higher-level gameplay, UI, and rendering pipelines will follow. These early systems are the most technically novel and critical to long-term coherence.

---

## Planned and Experimental Features

Still in development or early research, these features represent the broader goals:

- AI observer ("Astral") with symbolic memory, saliency, and teachable behavior
  - Prioritizes local inference, smart caching, and sustainable design
- Chunk streaming and procedural world generation using layered noise
- Reversible simulation for undo, replay, and debugging
  - Supported by grounded field structures and space-time inversion logic
- Developer-facing debug overlays and dynamic introspection tools
  - Allow live probing and tracing of internal simulation state
  - Intended to support fast iteration and system-level reasoning

---

## Tech Stack & Architecture

### Primary Language:

- Python 3.11+ — chosen for rapid prototyping, introspection tools, and flexible data structures.

### Graphics & Simulation:

- OpenGL via pyglet (2.1.6) — custom shader pipeline, instanced rendering, and GPU-side logic.
- NumPy — vector math, SDF field manipulation, and simulation state.
- ctypes — low-level GPU and OpenGL integration.

### Build & Dev Tools:

- black, isort, pytest — formatting, linting, and test automation.
- bumpver + custom release.py — automated CalVer versioning and changelog generation.

### Planned/Experimental:

- Rust (via pyo3 or full Rust port) for performance-critical systems like physics, mesh generation, or chunk streaming.
- Vulkan backend or SDF raymarcher for high-fidelity rendering.
- Optional C++ interop for stable, high-performance engine core if Rust path is deprioritized.

---

## Module-Level Docs

This root README summarizes the overall vision. Each engine subsystem maintains its own README.md for internal design and API details:

- src/engine/ — engine bootstrap, config, and system loader
- src/render/ — rendering systems and OpenGL bindings
- src/world/ — voxel and chunk management
- src/ai/ — symbolic AI companion design and observer logic
- docs/ — long-form articles, design essays, and technical vision

If viewing this on GitHub, click the folders above to view each README.md.

---

## Release Workflow

The engine uses calendar versioning (`2025.1002-dev`, etc.) and an automated release script that:

- Computes the next version
- Inserts a changelog entry from recent Git commits
- Updates `pyproject.toml`
- Commits the changes and creates an annotated Git tag

Basic usage:

```
python release.py
```

Add `--hotfix` to increment with a `-hotfix` suffix instead of `-dev`.

---

## Project Structure

```
astraltrail/           # Entry point and launcher logic
src/                   # Core engine code
  ├── engine/          # Bootstrap and engine-level systems
  ├── render/          # Rendering and GL pipelines
  ├── world/           # Voxel/SDF spatial data and logic
  └── ai/              # Symbolic observer AI (experimental)
legacy/                # Archived monolithic prototype
assets/                # Static resources (textures, etc.)
docs/                  # Vision documents and essays
CHANGELOG.md           # Auto-generated release history
pyproject.toml         # Build and dependency metadata
release.py             # Automated version and release script
```

---

## License

Business Source License 1.1 (BSL-1.1). See `LICENSE` for details.

---

## About the Developer

Astral Engine is being developed solo by [Cameron Bains](mailto:cameronenginebytes@gmail.com), a mechanical engineer turned programmer building a simulation-first engine from the ground up. The project is equal parts engine research, worldbuilding platform, and design experiment.
