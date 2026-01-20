"""Data models for pychrony.

This module defines dataclasses for chrony report types, enums for categorical
fields, and helper functions for converting libchrony data to Python types.
"""

from dataclasses import dataclass
from enum import Enum

__all__ = [
    # Enums
    "LeapStatus",
    "SourceState",
    "SourceMode",
    # Dataclasses
    "TrackingStatus",
    "Source",
    "SourceStats",
    "RTCData",
    # Helpers
    "_ref_id_to_name",
]


class LeapStatus(Enum):
    """Leap second status for NTP synchronization.

    Indicates whether time is normal or if a leap second adjustment
    is scheduled at the next midnight UTC.

    Attributes:
        NORMAL: No leap second pending.
        INSERT: Leap second will be inserted at midnight (23:59:60).
        DELETE: Leap second will be deleted at midnight (skip 23:59:59).
        UNSYNC: Clock is unsynchronized.

    Examples:
        >>> from pychrony import ChronyConnection, LeapStatus
        >>> with ChronyConnection() as conn:
        ...     status = conn.get_tracking()
        ...     if status.leap_status == LeapStatus.INSERT:
        ...         print("Leap second insertion scheduled")
        ...     elif status.leap_status == LeapStatus.UNSYNC:
        ...         print("Clock not synchronized")
    """

    NORMAL = 0
    INSERT = 1
    DELETE = 2
    UNSYNC = 3


class SourceState(Enum):
    """Selection state of a chrony time source.

    Indicates whether chrony has selected, rejected, or is
    considering this source for time synchronization.

    Attributes:
        SELECTED: Currently selected for synchronization.
        NONSELECTABLE: Cannot be selected (bad measurements).
        FALSETICKER: Detected as providing incorrect time.
        JITTERY: Measurements have excessive jitter.
        UNSELECTED: Valid but not currently selected.
        SELECTABLE: Candidate for selection.

    Examples:
        >>> from pychrony import ChronyConnection, SourceState
        >>> with ChronyConnection() as conn:
        ...     for src in conn.get_sources():
        ...         if src.state == SourceState.FALSETICKER:
        ...             print(f"Warning: {src.address} detected as falseticker")
        ...         elif src.state == SourceState.SELECTED:
        ...             print(f"Active source: {src.address}")
    """

    SELECTED = 0
    NONSELECTABLE = 1
    FALSETICKER = 2
    JITTERY = 3
    UNSELECTED = 4
    SELECTABLE = 5


class SourceMode(Enum):
    """Operational mode of a chrony time source.

    Distinguishes between NTP client connections, peer
    relationships, and local reference clocks.

    Attributes:
        CLIENT: NTP client polling a server.
        PEER: NTP peer relationship (bidirectional).
        REFCLOCK: Local reference clock (GPS, PPS, etc.).

    Examples:
        >>> from pychrony import ChronyConnection, SourceMode
        >>> with ChronyConnection() as conn:
        ...     for src in conn.get_sources():
        ...         if src.mode == SourceMode.REFCLOCK:
        ...             print(f"Reference clock: {src.address}")
        ...         elif src.mode == SourceMode.CLIENT:
        ...             print(f"NTP server: {src.address}")
    """

    CLIENT = 0
    PEER = 1
    REFCLOCK = 2


@dataclass(frozen=True)
class TrackingStatus:
    """Chrony tracking status information.

    Represents the current time synchronization state from chronyd,
    including offset, frequency, and accuracy metrics.

    Attributes:
        reference_id: NTP reference identifier (uint32 as hex IP or name).
        reference_id_name: Human-readable reference source name.
        reference_ip: IP address of reference source (IPv4, IPv6, or ID#).
        stratum: NTP stratum level (0=reference clock, 1-15=downstream).
        leap_status: Leap second status (see `LeapStatus`).
        ref_time: Timestamp of last measurement (seconds since epoch).
        offset: Current offset from reference (seconds, can be negative).
        last_offset: Offset at last measurement (seconds).
        rms_offset: Root mean square of recent offsets (seconds).
        frequency: Clock frequency error (parts per million).
        residual_freq: Residual frequency for current source (ppm).
        skew: Estimated error bound on frequency (ppm).
        root_delay: Total roundtrip delay to stratum-1 source (seconds).
        root_dispersion: Total dispersion to reference (seconds).
        update_interval: Seconds since last successful update.

    See Also:
        `LeapStatus`: Enum for leap second status values.
        `ChronyConnection.get_tracking`: Method to retrieve this data.
    """

    reference_id: int
    reference_id_name: str
    reference_ip: str
    stratum: int
    leap_status: LeapStatus
    ref_time: float
    offset: float
    last_offset: float
    rms_offset: float
    frequency: float
    residual_freq: float
    skew: float
    root_delay: float
    root_dispersion: float
    update_interval: float

    def is_synchronized(self) -> bool:
        """Check if chronyd is synchronized to a source.

        Returns:
            True if synchronized (reference_id != 0 and stratum < 16),
            False otherwise.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     status = conn.get_tracking()
            ...     if status.is_synchronized():
            ...         print(f"Synced to {status.reference_ip}")
        """
        return self.reference_id != 0 and self.stratum < 16

    def is_leap_pending(self) -> bool:
        """Check if a leap second adjustment is pending.

        Returns:
            True if leap_status is INSERT or DELETE,
            False otherwise.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     status = conn.get_tracking()
            ...     if status.is_leap_pending():
            ...         print(f"Leap second pending: {status.leap_status.name}")
        """
        return self.leap_status in (LeapStatus.INSERT, LeapStatus.DELETE)


@dataclass(frozen=True)
class Source:
    """Chrony source information.

    Represents an NTP server, peer, or reference clock being used
    as a time source by chronyd.

    Attributes:
        address: IP address or reference ID of the source (IPv4, IPv6, or refclock ID).
        poll: Polling interval as log2 seconds (e.g., 6 means 64 seconds).
        stratum: NTP stratum level of the source (0-15).
        state: Selection state (see `SourceState`).
        mode: Source mode (see `SourceMode`).
        flags: Source flags (bitfield).
        reachability: Reachability register (8-bit, 377 octal = all recent polls succeeded).
        last_sample_ago: Seconds since last valid sample was received.
        orig_latest_meas: Original last sample offset (seconds).
        latest_meas: Adjusted last sample offset (seconds).
        latest_meas_err: Last sample error bound (seconds).

    See Also:
        `SourceState`: Enum for source selection states.
        `SourceMode`: Enum for source operational modes.
        `ChronyConnection.get_sources`: Method to retrieve source list.
    """

    address: str
    poll: int
    stratum: int
    state: SourceState
    mode: SourceMode
    flags: int
    reachability: int
    last_sample_ago: int
    orig_latest_meas: float
    latest_meas: float
    latest_meas_err: float

    def is_reachable(self) -> bool:
        """Check if the source has been reachable recently.

        Returns:
            True if reachability register is non-zero (at least one successful poll).

        Examples:
            >>> with ChronyConnection() as conn:
            ...     for src in conn.get_sources():
            ...         if not src.is_reachable():
            ...             print(f"Source {src.address} is unreachable")
        """
        return self.reachability > 0

    def is_selected(self) -> bool:
        """Check if this source is currently selected for synchronization.

        Returns:
            True if state is SELECTED.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     for src in conn.get_sources():
            ...         if src.is_selected():
            ...             print(f"Currently using {src.address}")
        """
        return self.state == SourceState.SELECTED


@dataclass(frozen=True)
class SourceStats:
    """Chrony source statistics.

    Represents statistical data about measurements from an NTP source,
    used for drift and offset estimation.

    Attributes:
        reference_id: 32-bit NTP reference identifier.
        address: IP address of the source (empty for reference clocks).
        samples: Number of sample points currently retained.
        runs: Number of runs of residuals with same sign.
        span: Time interval between oldest and newest samples (seconds).
        std_dev: Estimated sample standard deviation (seconds).
        resid_freq: Residual frequency (parts per million).
        skew: Frequency skew (error bound) in ppm.
        offset: Estimated offset of the source (seconds).
        offset_err: Offset error bound (seconds).

    See Also:
        `ChronyConnection.get_source_stats`: Method to retrieve statistics.
    """

    reference_id: int
    address: str
    samples: int
    runs: int
    span: int
    std_dev: float
    resid_freq: float
    skew: float
    offset: float
    offset_err: float

    def has_sufficient_samples(self, minimum: int = 4) -> bool:
        """Check if enough samples exist for reliable statistics.

        Args:
            minimum: Minimum number of samples required (default 4).

        Returns:
            True if samples >= minimum.

        Examples:
            >>> with ChronyConnection() as conn:
            ...     for stats in conn.get_source_stats():
            ...         if stats.has_sufficient_samples(8):
            ...             print(f"{stats.address}: offset={stats.offset:.6f}s")
        """
        return self.samples >= minimum


@dataclass(frozen=True)
class RTCData:
    """Chrony RTC (Real-Time Clock) data.

    Represents information about the hardware RTC and its relationship
    to system time, as tracked by chronyd.

    Note: RTC tracking must be enabled in chronyd configuration.
    If not enabled, `get_rtc_data()` returns ``None``.

    Attributes:
        ref_time: RTC reading at last error measurement (seconds since epoch).
        samples: Number of previous measurements used for calibration.
        runs: Number of runs of residuals (indicates linear model fit quality).
        span: Time period covered by measurements (seconds).
        offset: Estimated RTC offset (fast by) in seconds.
        freq_offset: RTC frequency offset (drift rate) in parts per million.

    See Also:
        `ChronyConnection.get_rtc_data`: Method to retrieve RTC data.
    """

    ref_time: float
    samples: int
    runs: int
    span: int
    offset: float
    freq_offset: float

    def is_calibrated(self) -> bool:
        """Check if RTC has enough calibration data.

        Returns:
            True if samples > 0 (some calibration exists).

        Examples:
            >>> with ChronyConnection() as conn:
            ...     rtc = conn.get_rtc_data()
            ...     if rtc and rtc.is_calibrated():
            ...         print(f"RTC drift: {rtc.freq_offset:.2f} ppm")
        """
        return self.samples > 0


def _ref_id_to_name(ref_id: int) -> str:
    """Convert reference ID to human-readable name.

    The reference_id is a 32-bit value interpreted as:
    - For IP addresses: Network byte order IP (e.g., 0x7f000001 = 127.0.0.1)
    - For reference clocks: ASCII characters (e.g., 0x47505300 = "GPS\\0")

    Args:
        ref_id: The 32-bit reference ID value

    Returns:
        Human-readable name (IP address string or ASCII name)
    """
    # Check if it looks like ASCII (all bytes printable or null)
    bytes_val = ref_id.to_bytes(4, "big")
    if all(b == 0 or 32 <= b < 127 for b in bytes_val):
        return bytes_val.rstrip(b"\x00").decode("ascii", errors="replace")
    # Otherwise format as IP address
    return ".".join(str(b) for b in bytes_val)
