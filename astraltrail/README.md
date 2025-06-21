# Astral Engine

**Astral Engine** is a custom-built, high-performance voxel simulation engine and the foundation of the solo-developed game **Astral Trail**. The goal is to unify rendering, physics, logic, and AI under a coherent simulation framework that enables scalable, emergent systems without resorting to traditional game engine abstractions.

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

MIT License. See `LICENSE` for details.

---

## About the Developer

Astral Engine is being developed solo by [Cameron Bains](mailto:cameronenginebytes@gmail.com), a mechanical engineer turned programmer building a simulation-first engine from the ground up. The project is equal parts engine research, worldbuilding platform, and design experiment.
