# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Releases that changed only CI, tooling or development dependencies are listed
for completeness; their wheels are functionally identical to the release before.

## [Unreleased]

### Added

- `CHANGELOG.md` and `SECURITY.md`.
- CI writes a coverage summary to the job summary and fails below a minimum
  coverage threshold.

## [2.0.3] - 2026-10-20

### Fixed

- `get_sources()` and `get_source_stats()` no longer fail with
  `ChronyDataError` (error code 11) when chronyd adds or removes a source
  mid-read, as it does while resolving pool and server names. The read restarts
  from a fresh record count, up to three times.
  ([#185](https://github.com/arunderwood/pychrony/pull/185))

## [2.0.2] - 2026-09-23

No library changes.

### Changed

- Releases publish to PyPI from the release workflow itself.
  ([#183](https://github.com/arunderwood/pychrony/pull/183))

## [2.0.1] - 2026-09-23

No library changes.

### Changed

- CI and release workflows hardened: actions pinned by SHA, least-privilege
  permissions, timeouts and concurrency groups.
  ([#179](https://github.com/arunderwood/pychrony/pull/179),
  [#180](https://github.com/arunderwood/pychrony/pull/180))

## [2.0.0] - 2026-08-30

### Added

- `Transport` enum, and `ChronyConnection.address` and
  `ChronyConnection.transport` properties reporting which transport an open
  connection settled on.
  ([#168](https://github.com/arunderwood/pychrony/pull/168))

### Changed

- **Breaking:** with no address, `ChronyConnection` decides auto-detection by
  attempting a connection to each candidate in turn (the default Unix socket
  paths, then the localhost command port) instead of checking whether a socket
  path exists. A present but unusable socket now falls back to the command port
  rather than raising. An explicit address still gets no fallback.
  ([#168](https://github.com/arunderwood/pychrony/pull/168))
- Permission-error guidance points read-only callers at the command port;
  joining the `chrony` group does not grant Unix socket access.
  ([#168](https://github.com/arunderwood/pychrony/pull/168))

### Fixed

- `chrony_err` values are resolved from libchrony's `chrony.h` at build time
  instead of being mirrored in Python.
  ([#168](https://github.com/arunderwood/pychrony/pull/168))

## [1.1.2] - 2026-08-30

No library changes.

### Fixed

- Release verification against Test PyPI no longer reads a stale pip index
  cache. ([#167](https://github.com/arunderwood/pychrony/pull/167))

## [1.1.1] - 2026-08-30

### Changed

- Locked `cffi` bumped to 2.1.1.
  ([#166](https://github.com/arunderwood/pychrony/pull/166))

## [1.1.0] - 2026-08-08

### Added

- Python 3.15 support and wheels.
  ([#149](https://github.com/arunderwood/pychrony/pull/149))

### Changed

- Development Status classifier set to Production/Stable.
  ([#151](https://github.com/arunderwood/pychrony/pull/151))

## [1.0.0] - 2026-07-12

First stable release. No library changes from 0.2.4.

## [0.2.4] - 2026-05-03

No library changes.

### Fixed

- Documentation deploy restored by bumping `pymdown-extensions`.
  ([#92](https://github.com/arunderwood/pychrony/pull/92))

## [0.2.3] - 2026-03-06

No library changes.

### Changed

- Wheels are built with uv as the cibuildwheel build frontend.
  ([#71](https://github.com/arunderwood/pychrony/pull/71))

## [0.2.2] - 2026-02-13

No library changes.

### Fixed

- Duplicate permissions blocks removed from the test workflow.
  ([#45](https://github.com/arunderwood/pychrony/pull/45))

## [0.2.1] - 2026-01-20

No library changes.

### Changed

- Workflows declare explicit token permissions.
  ([#40](https://github.com/arunderwood/pychrony/pull/40),
  [#41](https://github.com/arunderwood/pychrony/pull/41),
  [#42](https://github.com/arunderwood/pychrony/pull/42),
  [#43](https://github.com/arunderwood/pychrony/pull/43))
- README usage example corrected.
  ([#44](https://github.com/arunderwood/pychrony/pull/44))

## [0.2.0] - 2026-01-20

No library changes.

### Fixed

- Publish workflow artifact download.
  ([#39](https://github.com/arunderwood/pychrony/pull/39))

## [0.1.0] - 2026-01-19

### Changed

- Docstrings reworked for the MkDocs API reference.
  ([#36](https://github.com/arunderwood/pychrony/pull/36),
  [#38](https://github.com/arunderwood/pychrony/pull/38))

## [0.0.15] - 2026-01-19

### Fixed

- `get_sources()` handles reference clock sources.
  ([#35](https://github.com/arunderwood/pychrony/pull/35))

## [0.0.14] - 2026-01-19

### Added

- Protocol-level test mock infrastructure in `pychrony.testing`.
  ([#32](https://github.com/arunderwood/pychrony/pull/32))
- API documentation at <https://pychrony.org/>, a testing guide (`TESTING.md`)
  and thread-safety documentation.
  ([#31](https://github.com/arunderwood/pychrony/pull/31),
  [#33](https://github.com/arunderwood/pychrony/pull/33),
  [#34](https://github.com/arunderwood/pychrony/pull/34))

## [0.0.12] - 2026-01-17

### Added

- `ChronyConnection` context manager, reusing one connection across queries
  and closing its socket on exit.
  ([#29](https://github.com/arunderwood/pychrony/pull/29))
- Test factory functions and pytest fixtures in `pychrony.testing`, registered
  as a pytest plugin. ([#28](https://github.com/arunderwood/pychrony/pull/28))

### Changed

- `get_rtc_data()` returns `None` when RTC tracking is not configured, instead
  of raising `ChronyDataError`.
  ([#27](https://github.com/arunderwood/pychrony/pull/27))

### Removed

- **Breaking:** module-level `get_tracking()`, `get_sources()`,
  `get_source_stats()` and `get_rtc_data()`; call them on a
  `ChronyConnection`. ([#29](https://github.com/arunderwood/pychrony/pull/29))

## [0.0.11] - 2026-01-17

### Added

- `pychrony.__version__`.
  ([#22](https://github.com/arunderwood/pychrony/pull/22))
- LGPL license compliance for the bundled libchrony.
  ([#21](https://github.com/arunderwood/pychrony/pull/21))

## [0.0.10] - 2026-01-17

First tagged release.

### Added

- CFFI bindings to libchrony: `get_tracking()`, `get_sources()`,
  `get_source_stats()` and `get_rtc_data()`, returning frozen dataclasses.
  ([#3](https://github.com/arunderwood/pychrony/pull/3),
  [#7](https://github.com/arunderwood/pychrony/pull/7))
- `LeapStatus`, `SourceState` and `SourceMode` enums for categorical fields.
  ([#10](https://github.com/arunderwood/pychrony/pull/10))
- `ChronyError` exception hierarchy.
- manylinux and musllinux wheels for x86_64 and aarch64 with libchrony bundled,
  published to PyPI through Trusted Publishers.
  ([#11](https://github.com/arunderwood/pychrony/pull/11))

[Unreleased]: https://github.com/arunderwood/pychrony/compare/v2.0.3...HEAD
[2.0.3]: https://github.com/arunderwood/pychrony/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/arunderwood/pychrony/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/arunderwood/pychrony/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/arunderwood/pychrony/compare/v1.1.2...v2.0.0
[1.1.2]: https://github.com/arunderwood/pychrony/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/arunderwood/pychrony/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/arunderwood/pychrony/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/arunderwood/pychrony/compare/v0.2.4...v1.0.0
[0.2.4]: https://github.com/arunderwood/pychrony/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/arunderwood/pychrony/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/arunderwood/pychrony/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/arunderwood/pychrony/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/arunderwood/pychrony/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/arunderwood/pychrony/compare/v0.0.15...v0.1.0
[0.0.15]: https://github.com/arunderwood/pychrony/compare/v0.0.14...v0.0.15
[0.0.14]: https://github.com/arunderwood/pychrony/compare/v0.0.12...v0.0.14
[0.0.12]: https://github.com/arunderwood/pychrony/compare/v0.0.11...v0.0.12
[0.0.11]: https://github.com/arunderwood/pychrony/compare/v0.0.10...v0.0.11
[0.0.10]: https://github.com/arunderwood/pychrony/releases/tag/v0.0.10
