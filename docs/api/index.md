# API Reference

Complete API documentation for pychrony, auto-generated from source code docstrings.

## Connection

The main entry point for interacting with chronyd.

::: pychrony.ChronyConnection
    options:
      show_root_heading: true
      members_order: source

## Data Models

Frozen dataclasses representing chronyd report data.

::: pychrony.TrackingStatus
    options:
      show_root_heading: true

::: pychrony.Source
    options:
      show_root_heading: true

::: pychrony.SourceStats
    options:
      show_root_heading: true

::: pychrony.RTCData
    options:
      show_root_heading: true

## Enums

Categorical values for status fields.

::: pychrony.LeapStatus
    options:
      show_root_heading: true

::: pychrony.SourceState
    options:
      show_root_heading: true

::: pychrony.SourceMode
    options:
      show_root_heading: true

## Exceptions

Exception hierarchy for error handling.

::: pychrony.ChronyError
    options:
      show_root_heading: true

::: pychrony.ChronyConnectionError
    options:
      show_root_heading: true

::: pychrony.ChronyPermissionError
    options:
      show_root_heading: true

::: pychrony.ChronyDataError
    options:
      show_root_heading: true

::: pychrony.ChronyLibraryError
    options:
      show_root_heading: true

## Testing Utilities

Factory functions and pytest fixtures for testing code that uses pychrony.

::: pychrony.testing
    options:
      show_root_heading: true
      members_order: source
