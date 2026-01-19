"""Configuration dataclasses for mock chrony state.

This module provides dataclasses for declarative configuration of
mock chrony scenarios for testing.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pychrony.models import LeapStatus, SourceState, SourceMode


__all__ = [
    "ChronyStateConfig",
    "SourceConfig",
    "RTCConfig",
]


@dataclass
class RTCConfig:
    """Configuration for RTC (Real-Time Clock) data.

    Attributes:
        available: Whether RTC data is available
        ref_time: RTC reference time (seconds since epoch)
        samples: Calibration samples count
        runs: Run count
        span: Time span in seconds
        offset: RTC offset in seconds
        freq_offset: Frequency offset in ppm
    """

    available: bool = True
    ref_time: float = 1705320000.123456789
    samples: int = 10
    runs: int = 4
    span: int = 86400
    offset: float = 0.123456
    freq_offset: float = -1.234

    def __post_init__(self) -> None:
        """Validate RTCConfig fields."""
        if self.samples < 0:
            raise ValueError("samples must be non-negative")
        if self.runs < 0:
            raise ValueError("runs must be non-negative")
        if self.span < 0:
            raise ValueError("span must be non-negative")
        if self.ref_time < 0:
            raise ValueError("ref_time must be non-negative")

    def is_calibrated(self) -> bool:
        """Check if RTC has calibration data.

        Returns:
            True if samples > 0
        """
        return self.samples > 0


@dataclass
class SourceConfig:
    """Configuration for a single time source.

    Combines both sources report fields and sourcestats report fields
    for convenience in test configuration.

    Attributes:
        address: Source address (IP or refclock name)
        poll: Polling interval (log2 seconds)
        stratum: NTP stratum level (0-15)
        state: Selection state
        mode: Source mode (CLIENT, PEER, REFCLOCK)
        flags: Source flags
        reachability: Reachability register (0-255)
        last_sample_ago: Seconds since last sample
        orig_latest_meas: Original offset measurement
        latest_meas: Adjusted offset measurement
        latest_meas_err: Measurement error bound
        reference_id: Optional override for reference ID
        samples: Sample count (for sourcestats)
        runs: Run count (for sourcestats)
        span: Time span (for sourcestats)
        std_dev: Standard deviation (for sourcestats)
        resid_freq: Residual frequency (for sourcestats)
        stats_skew: Skew (for sourcestats)
        stats_offset: Offset (for sourcestats)
        offset_err: Offset error (for sourcestats)
    """

    address: str = "192.168.1.100"
    poll: int = 6
    stratum: int = 2
    state: SourceState = SourceState.SELECTED
    mode: SourceMode = SourceMode.CLIENT
    flags: int = 0
    reachability: int = 255
    last_sample_ago: int = 32
    orig_latest_meas: float = 0.000123456
    latest_meas: float = 0.000123456
    latest_meas_err: float = 0.000010000

    # Optional reference_id override (auto-computed from address if None)
    reference_id: int | None = None

    # SourceStats fields
    samples: int = 8
    runs: int = 3
    span: int = 512
    std_dev: float = 0.000100000
    resid_freq: float = 0.001
    stats_skew: float = 0.005
    stats_offset: float = 0.000123456
    offset_err: float = 0.000010000

    def __post_init__(self) -> None:
        """Validate SourceConfig fields."""
        if not 0 <= self.stratum <= 15:
            raise ValueError("stratum must be 0-15")
        if not 0 <= self.reachability <= 255:
            raise ValueError("reachability must be 0-255")
        if self.last_sample_ago < 0:
            raise ValueError("last_sample_ago must be non-negative")
        if self.latest_meas_err < 0:
            raise ValueError("latest_meas_err must be non-negative")
        if self.samples < 0:
            raise ValueError("samples must be non-negative")
        if self.runs < 0:
            raise ValueError("runs must be non-negative")
        if self.span < 0:
            raise ValueError("span must be non-negative")
        if self.std_dev < 0:
            raise ValueError("std_dev must be non-negative")
        if self.stats_skew < 0:
            raise ValueError("stats_skew must be non-negative")
        if self.offset_err < 0:
            raise ValueError("offset_err must be non-negative")

    def compute_reference_id(self) -> int:
        """Compute reference_id from address if not set.

        Returns:
            Computed reference ID (IP as uint32 or ASCII refclock ID)
        """
        if self.reference_id is not None:
            return self.reference_id

        address = self.address

        # Check if it looks like a refclock name (short ASCII string)
        if len(address) <= 4 and address.isalpha():
            # Convert to ASCII reference ID (e.g., "GPS" -> 0x47505300)
            padded = address.ljust(4, "\x00")
            return int.from_bytes(padded.encode("ascii"), "big")

        # Try to parse as IPv4 address
        try:
            parts = address.split(".")
            if len(parts) == 4:
                octets = [int(p) for p in parts]
                if all(0 <= o <= 255 for o in octets):
                    return (
                        (octets[0] << 24)
                        | (octets[1] << 16)
                        | (octets[2] << 8)
                        | octets[3]
                    )
        except (ValueError, AttributeError):
            pass

        # Fallback: hash the address
        return hash(address) & 0xFFFFFFFF

    def is_reachable(self) -> bool:
        """Check if source is reachable.

        Returns:
            True if reachability > 0
        """
        return self.reachability > 0

    def is_selected(self) -> bool:
        """Check if source is selected.

        Returns:
            True if state is SELECTED
        """
        return self.state == SourceState.SELECTED


@dataclass
class ChronyStateConfig:
    """Root configuration for mock chrony state.

    Contains tracking fields, source list, RTC configuration,
    and error injection settings.

    Attributes:
        stratum: NTP stratum level (0-15)
        reference_id: Reference identifier (uint32)
        reference_ip: Reference source IP/name
        leap_status: Leap second status
        ref_time: Reference timestamp (seconds since epoch)
        offset: Current offset in seconds
        last_offset: Previous offset in seconds
        rms_offset: RMS offset in seconds
        frequency: Frequency offset in ppm
        residual_freq: Residual frequency in ppm
        skew: Frequency skew in ppm
        root_delay: Root delay in seconds
        root_dispersion: Root dispersion in seconds
        update_interval: Update interval in seconds
        sources: List of source configurations
        rtc: RTC configuration (None if not available)
        error_injection: Map of operation names to error codes
    """

    stratum: int = 2
    reference_id: int = 0x7F000001
    reference_ip: str = "127.0.0.1"
    leap_status: LeapStatus = LeapStatus.NORMAL
    ref_time: float = 1705320000.123456789
    offset: float = 0.000123456
    last_offset: float = 0.000111222
    rms_offset: float = 0.000100000
    frequency: float = 1.234
    residual_freq: float = 0.001
    skew: float = 0.005
    root_delay: float = 0.001234
    root_dispersion: float = 0.002345
    update_interval: float = 64.0

    # Sub-configurations
    sources: list[SourceConfig] = field(default_factory=list)
    rtc: RTCConfig | None = None

    # Error injection
    error_injection: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate ChronyStateConfig fields."""
        if not 0 <= self.stratum <= 16:
            raise ValueError("stratum must be 0-16 (16 means unsynchronized)")
        if self.rms_offset < 0:
            raise ValueError("rms_offset must be non-negative")
        if self.skew < 0:
            raise ValueError("skew must be non-negative")
        if self.root_delay < 0:
            raise ValueError("root_delay must be non-negative")
        if self.root_dispersion < 0:
            raise ValueError("root_dispersion must be non-negative")
        if self.update_interval < 0:
            raise ValueError("update_interval must be non-negative")
        if self.ref_time < 0:
            raise ValueError("ref_time must be non-negative")

        # Validate error injection keys
        valid_keys = {
            "chrony_open_socket",
            "chrony_init_session",
            "chrony_request_report_number_records",
            "chrony_process_response",
            "chrony_request_record",
        }
        for key in self.error_injection:
            if key not in valid_keys:
                raise ValueError(
                    f"Invalid error_injection key: {key}. "
                    f"Valid keys are: {', '.join(sorted(valid_keys))}"
                )

    def reference_id_name(self) -> str:
        """Compute human-readable reference ID name.

        Returns:
            IP address string or ASCII name
        """
        # Check if it looks like ASCII (all bytes printable or null)
        bytes_val = self.reference_id.to_bytes(4, "big")
        if all(b == 0 or 32 <= b < 127 for b in bytes_val):
            return bytes_val.rstrip(b"\x00").decode("ascii", errors="replace")
        # Otherwise format as IP address
        return ".".join(str(b) for b in bytes_val)

    def is_synchronized(self) -> bool:
        """Check if config represents synchronized state.

        Returns:
            True if reference_id != 0 and stratum < 16
        """
        return self.reference_id != 0 and self.stratum < 16

    def is_leap_pending(self) -> bool:
        """Check if leap second is pending.

        Returns:
            True if leap_status is INSERT or DELETE
        """
        return self.leap_status in (LeapStatus.INSERT, LeapStatus.DELETE)
