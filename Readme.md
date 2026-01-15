# pychrony

pychrony is a Linux-first Python SDK that provides typed access to whatever monitoring data libchrony natively exposes.

It exists to replace fragile chronyc subprocess parsing with a stable, testable Python API.

## What pychrony is

- A thin, typed Python wrapper around libchrony
- Focused on read-only monitoring data
- Designed for observability, dashboards, and analysis
- Linux-first and CI-tested

## What pychrony is not

- A replacement for chronyc
- A chronyd configuration or control tool
- A client-reporting API (chronyc clients is out of scope)
- A reimplementation of chronyd protocols

If libchrony does not support a feature, pychrony does not implement it.
