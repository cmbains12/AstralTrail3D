
## [2025.1003-dev] - 2025-06-23

### Other
- feat(ecs): implement flexible ComponentManager and core SystemManager with full test coverage - Added SoA-based component storage, sparse/dense modes, dynamic registration, and system query support - Introduced SystemManager with named system registration, tags, phases, and conditional execution - Added complete test suites for both managers


## [2025.1002-dev] - 2025-06-23
### Added
- [ECS] Set up testing suite and ECS entity management system: 
  - added pytest config, 
  - EntityManager implementation, and 
  - unit tests for creation and ID reuse
### Other
- [META] - cleaning changelog from messy versioning release debugging

## [2025.1001-dev-hotfix] - 2025-06-21
#### Hotfix patch (2025-06-21)
### Other
- [META] - debugging version changes

## [2025.1001-dev] - 2025-06-20
### Added
- Project structure refactored to modular layout under `src/`
- Bootstrapping system with multiple entry modes (`sandbox`, `legacy`)
- `pyproject.toml` with packaging metadata and dev tool config
- Legacy monolith isolated under `legacy/`
- Initial documentation and long-form design articles under `/docs/`
