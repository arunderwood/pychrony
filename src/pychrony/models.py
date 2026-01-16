"""Data models for pychrony.

This module defines the TrackingStatus dataclass and helper functions
for converting libchrony data to Python types.
"""

from dataclasses import dataclass


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
