# Versioning Strategy

Ascendant: The Eternal Spire follows [Semantic Versioning 2.0.0](https://semver.org/).

## Version Format

`MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes, save file format changes, major gameplay overhauls
- **MINOR**: New features, backwards-compatible changes, new game content
- **PATCH**: Bug fixes, performance improvements, minor adjustments

## Version Locations

The version number is maintained in several locations:
1. `VERSION` file (single source of truth)
2. `src/__init__.py` (__version__ attribute)
3. `setup.py` (reads from VERSION file)
4. Git tags (v0.1.0, v0.2.0, etc.)

## Release Process

1. Update `VERSION` file
2. Update `src/__init__.py` with new version and history note
3. Update `CHANGELOG.md` with release notes
4. Commit changes: `git commit -m "Release version X.Y.Z"`
5. Tag the release: `git tag -a vX.Y.Z -m "Version X.Y.Z"`
6. Push with tags: `git push origin main --tags`

## Pre-release Versions

During development phases:
- Alpha: `0.1.0-alpha.1`, `0.1.0-alpha.2`
- Beta: `0.1.0-beta.1`, `0.1.0-beta.2`
- Release Candidate: `0.1.0-rc.1`, `0.1.0-rc.2`

## Version Milestones

- `0.x.x` - Pre-release development (current)
- `1.0.0` - First stable release with core gameplay
- `2.0.0` - Major expansion or multiplayer addition
- `3.0.0` - Complete engine overhaul or major platform change

## Contract Version Mapping

Each version implements specific UTF contracts:
- `0.1.0` - GAME-CORE-001 (Project Initialization)
- `0.2.0` - GAME-CORE-002 through GAME-CORE-005 (Core Data Structures)
- `0.3.0` - GAME-MAP-001 through GAME-MAP-007 (Map Generation)
- etc.

This ensures traceability between game versions and CAFE methodology compliance.
