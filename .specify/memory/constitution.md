<!--
Sync Impact Report:
Version change: 1.1.0 → 1.2.0 (MINOR - CFFI API mode requirement)
Modified principles: "Bind via CFFI API mode" (changed from generic CFFI to explicit API mode)
Added sections: None
Removed sections: None
Templates requiring updates: ✅ no changes needed - templates reference principles generically
Follow-up TODOs: Update specs to reflect API mode (set_source instead of dlopen)
-->

# pychrony Constitution

## Core Principles

### libchrony is the source of truth
libchrony defines the native API surface; pychrony only exposes what libchrony supports; no artificial abstractions or interpretations. Use libchrony's high-level introspection API (chrony_get_field_float, chrony_get_field_timespec, chrony_get_field_uinteger, etc.) rather than direct struct access; these functions return native C types (double, struct timespec), providing ABI stability without manual wire-format conversions.

### Pythonic, typed API
All interfaces follow Python conventions; full type hints required; native Python data structures and idioms

### Monitoring only
Read-only access exclusively; no control or configuration capabilities; observe but never modify system state

### Linux-first
Primary target platform is Linux; other platforms supported if libchrony available; testing and CI focused on Linux

### Tests required
All features must have automated tests; test coverage mandatory for new code; tests must pass in Linux CI

## Implementation Requirements

Bind via CFFI API mode (ffi.set_source); Requires libchrony-devel headers at build/install time; Dynamically link system libchrony at runtime; No vendoring or reimplementation; UV is the package manager.

## Quality Standards

Tests required; Linux CI required; Versioning follows libchrony changes

## Governance

Constitution supersedes all other practices; Amendments require documentation, approval, migration plan; All PRs/reviews must verify compliance; Complexity must be justified

**Version**: 1.2.0 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-01-16
