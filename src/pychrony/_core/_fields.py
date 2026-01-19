"""Field type registry for chrony report types.

This module defines the field names and types for all chrony report types.
It serves as a single source of truth for:
- Production code (_bindings.py) - field extraction
- Test mocks (tests/mocks/) - field simulation

The field names and types are derived from libchrony's reports.h header.
"""

from enum import Enum

__all__ = [
    "FieldType",
    "TRACKING_FIELDS",
    "SOURCE_FIELDS",
    "SOURCESTATS_FIELDS",
    "RTC_FIELDS",
]


class FieldType(Enum):
    """Type of a chrony report field.

    Used to determine which chrony_get_field_* function to call
    and how to interpret the returned value.
    """

    FLOAT = "float"
    UINTEGER = "uinteger"
    INTEGER = "integer"
    STRING = "string"
    TIMESPEC = "timespec"


# Tracking report fields (from chrony_get_field_* calls in _bindings.py)
# Maps field name (as used in libchrony) to its type
TRACKING_FIELDS: dict[str, FieldType] = {
    "reference ID": FieldType.UINTEGER,
    "stratum": FieldType.UINTEGER,
    "leap status": FieldType.UINTEGER,
    "address": FieldType.STRING,
    "current correction": FieldType.FLOAT,
    "last offset": FieldType.FLOAT,
    "RMS offset": FieldType.FLOAT,
    "frequency offset": FieldType.FLOAT,
    "residual frequency": FieldType.FLOAT,
    "skew": FieldType.FLOAT,
    "root delay": FieldType.FLOAT,
    "root dispersion": FieldType.FLOAT,
    "last update interval": FieldType.FLOAT,
    "reference time": FieldType.TIMESPEC,
}

# Sources report fields
SOURCE_FIELDS: dict[str, FieldType] = {
    "address": FieldType.STRING,
    "reference ID": FieldType.UINTEGER,
    "state": FieldType.UINTEGER,
    "mode": FieldType.UINTEGER,
    "poll": FieldType.INTEGER,
    "stratum": FieldType.UINTEGER,
    "flags": FieldType.UINTEGER,
    "reachability": FieldType.UINTEGER,
    "last sample ago": FieldType.UINTEGER,
    "original last sample offset": FieldType.FLOAT,
    "adjusted last sample offset": FieldType.FLOAT,
    "last sample error": FieldType.FLOAT,
}

# Sourcestats report fields
SOURCESTATS_FIELDS: dict[str, FieldType] = {
    "reference ID": FieldType.UINTEGER,
    "address": FieldType.STRING,
    "samples": FieldType.UINTEGER,
    "runs": FieldType.UINTEGER,
    "span": FieldType.UINTEGER,
    "standard deviation": FieldType.FLOAT,
    "residual frequency": FieldType.FLOAT,
    "skew": FieldType.FLOAT,
    "offset": FieldType.FLOAT,
    "offset error": FieldType.FLOAT,
}

# RTC data report fields
RTC_FIELDS: dict[str, FieldType] = {
    "reference time": FieldType.TIMESPEC,
    "samples": FieldType.UINTEGER,
    "runs": FieldType.UINTEGER,
    "span": FieldType.UINTEGER,
    "offset": FieldType.FLOAT,
    "frequency offset": FieldType.FLOAT,
}
