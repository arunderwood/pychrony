"""Contract tests for API stability of enum types."""

from dataclasses import fields
from enum import Enum


from pychrony import Source, TrackingStatus, LeapStatus, SourceState, SourceMode


class TestEnumExports:
    """Tests for enum exports from pychrony package."""

    def test_leap_status_in_all(self):
        """Test that LeapStatus is in __all__."""
        from pychrony import __all__

        assert "LeapStatus" in __all__

    def test_source_state_in_all(self):
        """Test that SourceState is in __all__."""
        from pychrony import __all__

        assert "SourceState" in __all__

    def test_source_mode_in_all(self):
        """Test that SourceMode is in __all__."""
        from pychrony import __all__

        assert "SourceMode" in __all__


class TestSourceStateFieldType:
    """Contract tests for Source.state field type (T007)."""

    def test_source_state_field_is_source_state_enum(self):
        """Test that Source.state field type is SourceState enum."""
        type_hints = {f.name: f.type for f in fields(Source)}
        assert type_hints["state"] is SourceState

    def test_source_state_is_enum(self):
        """Test that SourceState is an Enum subclass."""
        assert issubclass(SourceState, Enum)


class TestSourceModeFieldType:
    """Contract tests for Source.mode field type (T026)."""

    def test_source_mode_field_is_source_mode_enum(self):
        """Test that Source.mode field type is SourceMode enum."""
        type_hints = {f.name: f.type for f in fields(Source)}
        assert type_hints["mode"] is SourceMode

    def test_source_mode_is_enum(self):
        """Test that SourceMode is an Enum subclass."""
        assert issubclass(SourceMode, Enum)


class TestLeapStatusFieldType:
    """Contract tests for TrackingStatus.leap_status field type (T017)."""

    def test_tracking_leap_status_field_is_leap_status_enum(self):
        """Test that TrackingStatus.leap_status field type is LeapStatus enum."""
        type_hints = {f.name: f.type for f in fields(TrackingStatus)}
        assert type_hints["leap_status"] is LeapStatus

    def test_leap_status_is_enum(self):
        """Test that LeapStatus is an Enum subclass."""
        assert issubclass(LeapStatus, Enum)


class TestSourceNoLongerHasNameProperties:
    """Contract tests verifying removed properties."""

    def test_source_no_mode_name_property(self):
        """Test that Source no longer has mode_name property."""
        # After enum migration, mode_name is removed - use mode.name instead
        assert not hasattr(Source, "mode_name")

    def test_source_no_state_name_property(self):
        """Test that Source no longer has state_name property."""
        # After enum migration, state_name is removed - use state.name instead
        assert not hasattr(Source, "state_name")
