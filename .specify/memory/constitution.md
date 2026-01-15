<!--
Sync Impact Report:
Version change: 1.0.0 → 1.0.1 (PATCH - added UV package manager)
Modified principles: None
Added sections: None
Removed sections: None
Templates requiring updates: ✅ updated - tasks-template.md
Follow-up TODOs: None
-->

# pychrony Constitution

## Core Principles

### libchrony is the source of truth
libchrony defines the native API surface; pychrony only exposes what libchrony supports; no artificial abstractions or interpretations

### Pythonic, typed API
All interfaces follow Python conventions; full type hints required; native Python data structures and idioms

### Monitoring only
Read-only access exclusively; no control or configuration capabilities; observe but never modify system state

### Linux-first
Primary target platform is Linux; other platforms supported if libchrony available; testing and CI focused on Linux

### Tests required
All features must have automated tests; test coverage mandatory for new code; tests must pass in Linux CI

## Implementation Requirements

Bind via CFFI; Dynamically link system libchrony; No vendoring or reimplementation; UV is the package manager.

## Quality Standards

Tests required; Linux CI required; Versioning follows libchrony changes

## Governance

Constitution supersedes all other practices; Amendments require documentation, approval, migration plan; All PRs/reviews must verify compliance; Complexity must be justified

**Version**: 1.0.1 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-01-14
