
## [2025.1003-dev] - 2025-06-20 <!-- {bumpver} -->

### Added
- • feat(core): add centralized entry points routed through bootstrap script
### Changed
- debugging
- refactor[project] moving project files around
- release: prepare version bump with multiple changes
- chore(lfs): track binary assets using Git LFS
- feat(cli): support legacy monolith via CLI flag
- feat(release): implement automatic versioning and changelog generation
- chore(pyproject): update version metadata for release
### Fixed
- fixed: more debugging
- fix: correcting bumbver changlog pattern

## [2025.1002-dev] - 2025-06-20 
### Added
- Project structure refactored to modular layout under `src/`
- Bootstrapping system with multiple entry modes (`sandbox`, `legacy`)
- `pyproject.toml` with packaging metadata and dev tool config
- Legacy monolith isolated under `legacy/`
- Initial documentation and long-form design articles under `/docs/`
