"""Data models for pychrony.

This module defines dataclasses for chrony report types and helper functions
for converting libchrony data to Python types.
"""

from dataclasses import dataclass

__all__ = [
    "TrackingStatus",
    "Source",
    "SourceStats",
    "RTCData",
    "_ref_id_to_name",
]


@dataclass(frozen=True)
class TrackingStatus:
    """Chrony tracking status information.

    Represents the current time synchronization state from chronyd,
    including offset, frequency, and accuracy metrics.

    Attributes:
        reference_id: NTP reference identifier (uint32 as hex IP or name)
        reference_id_name: Human-readable reference source name
        reference_ip: IP address of reference source (IPv4, IPv6, or ID#)
        stratum: NTP stratum level (0=reference clock, 1-15=downstream)
        leap_status: Leap second status (0=normal, 1=insert, 2=delete, 3=unsync)
        ref_time: Timestamp of last measurement (seconds since epoch)
        offset: Current offset from reference in seconds (can be negative)
        last_offset: Offset at last measurement in seconds
        rms_offset: Root mean square of recent offsets in seconds
        frequency: Clock frequency error in parts per million
        residual_freq: Residual frequency for current source in ppm
        skew: Estimated error bound on frequency in ppm
        root_delay: Total roundtrip delay to stratum-1 source in seconds
        root_dispersion: Total dispersion to reference in seconds
        update_interval: Seconds since last successful update
    """

    reference_id: int
    reference_id_name: str
    reference_ip: str
    stratum: int
    leap_status: int
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
        """
        return self.reference_id != 0 and self.stratum < 16

    def is_leap_pending(self) -> bool:
        """Check if a leap second adjustment is pending.

        Returns:
            True if leap_status is 1 (insert) or 2 (delete),
            False otherwise.
        """
        return self.leap_status in (1, 2)


@dataclass(frozen=True)
class Source:
    """Chrony source information.

    Represents an NTP server, peer, or reference clock being used
    as a time source by chronyd.

    Attributes:
        address: IP address or reference ID of the source (IPv4, IPv6, or refclock ID)
        poll: Polling interval as log2 seconds (e.g., 6 means 64 seconds)
        stratum: NTP stratum level of the source (0-15)
        state: Selection state (0=selected, 1=nonselectable, 2=falseticker,
               3=jittery, 4=unselected, 5=selectable)
        mode: Source mode (0=client, 1=peer, 2=reference clock)
        flags: Source flags (bitfield)
        reachability: Reachability register (8-bit, 377 octal = all recent polls succeeded)
        last_sample_ago: Seconds since last valid sample was received
        orig_latest_meas: Original last sample offset in seconds
        latest_meas: Adjusted last sample offset in seconds
        latest_meas_err: Last sample error bound in seconds
    """

    address: str
    poll: int
    stratum: int
    state: int
    mode: int
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
        """
        return self.reachability > 0

    def is_selected(self) -> bool:
        """Check if this source is currently selected for synchronization.

        Returns:
            True if state is 0 (selected).
        """
        return self.state == 0

    @property
    def mode_name(self) -> str:
        """Human-readable mode name."""
        modes = {0: "client", 1: "peer", 2: "reference clock"}
        return modes.get(self.mode, f"unknown({self.mode})")

    @property
    def state_name(self) -> str:
        """Human-readable state name."""
        states = {
            0: "selected",
            1: "nonselectable",
            2: "falseticker",
            3: "jittery",
            4: "unselected",
            5: "selectable",
        }
        return states.get(self.state, f"unknown({self.state})")


@dataclass(frozen=True)
class SourceStats:
    """Chrony source statistics.

    Represents statistical data about measurements from an NTP source,
    used for drift and offset estimation.

    Attributes:
        reference_id: 32-bit NTP reference identifier
        address: IP address of the source (empty for reference clocks)
        samples: Number of sample points currently retained
        runs: Number of runs of residuals with same sign
        span: Time interval between oldest and newest samples in seconds
        std_dev: Estimated sample standard deviation in seconds
        resid_freq: Residual frequency in parts per million
        skew: Frequency skew (error bound) in ppm
        offset: Estimated offset of the source in seconds
        offset_err: Offset error bound in seconds
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
            minimum: Minimum number of samples required (default 4)

        Returns:
            True if samples >= minimum.
        """
        return self.samples >= minimum


@dataclass(frozen=True)
class RTCData:
    """Chrony RTC (Real-Time Clock) data.

    Represents information about the hardware RTC and its relationship
    to system time, as tracked by chronyd.

    Note: RTC tracking must be enabled in chronyd configuration.
    If not enabled, get_rtc_data() raises ChronyDataError.

    Attributes:
        ref_time: RTC reading at last error measurement (seconds since epoch)
        samples: Number of previous measurements used for calibration
        runs: Number of runs of residuals (indicates linear model fit quality)
        span: Time period covered by measurements in seconds
        offset: Estimated RTC offset (fast by) in seconds
        freq_offset: RTC frequency offset (drift rate) in parts per million
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
