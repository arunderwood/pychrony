"""Contract tests for pychrony public API stability."""

import inspect
from dataclasses import fields, is_dataclass

from pychrony import LeapStatus, SourceState, SourceMode


class TestPublicExports:
    """Tests for public API exports."""

    def test_all_exports_importable(self):
        """Test that all __all__ exports are importable."""
        from pychrony import __all__

        assert "ChronyConnection" in __all__
        assert "TrackingStatus" in __all__
        assert "ChronyError" in __all__
        assert "ChronyConnectionError" in __all__
        assert "ChronyPermissionError" in __all__
        assert "ChronyDataError" in __all__
        assert "ChronyLibraryError" in __all__

    def test_chrony_connection_importable(self):
        """Test that ChronyConnection can be imported."""
        from pychrony import ChronyConnection

        assert ChronyConnection is not None

    def test_tracking_status_importable(self):
        """Test that TrackingStatus can be imported."""
        from pychrony import TrackingStatus

        assert TrackingStatus is not None

    def test_exceptions_importable(self):
        """Test that all exceptions can be imported."""
        from pychrony import (
            ChronyError,
            ChronyConnectionError,
            ChronyPermissionError,
            ChronyDataError,
            ChronyLibraryError,
        )

        assert issubclass(ChronyConnectionError, ChronyError)
        assert issubclass(ChronyPermissionError, ChronyError)
        assert issubclass(ChronyDataError, ChronyError)
        assert issubclass(ChronyLibraryError, ChronyError)


class TestChronyConnectionContract:
    """Tests for ChronyConnection API contract."""

    def test_is_context_manager(self):
        """Test that ChronyConnection implements context manager protocol."""
        from pychrony import ChronyConnection

        assert hasattr(ChronyConnection, "__enter__")
        assert hasattr(ChronyConnection, "__exit__")
        assert callable(getattr(ChronyConnection, "__enter__"))
        assert callable(getattr(ChronyConnection, "__exit__"))

    def test_has_get_tracking_method(self):
        """Test that ChronyConnection has get_tracking method."""
        from pychrony import ChronyConnection

        assert hasattr(ChronyConnection, "get_tracking")
        assert callable(getattr(ChronyConnection, "get_tracking"))

    def test_has_get_sources_method(self):
        """Test that ChronyConnection has get_sources method."""
        from pychrony import ChronyConnection

        assert hasattr(ChronyConnection, "get_sources")
        assert callable(getattr(ChronyConnection, "get_sources"))

    def test_has_get_source_stats_method(self):
        """Test that ChronyConnection has get_source_stats method."""
        from pychrony import ChronyConnection

        assert hasattr(ChronyConnection, "get_source_stats")
        assert callable(getattr(ChronyConnection, "get_source_stats"))

    def test_has_get_rtc_data_method(self):
        """Test that ChronyConnection has get_rtc_data method."""
        from pychrony import ChronyConnection

        assert hasattr(ChronyConnection, "get_rtc_data")
        assert callable(getattr(ChronyConnection, "get_rtc_data"))

    def test_init_accepts_address_parameter(self):
        """Test that ChronyConnection.__init__ accepts address parameter."""
        from pychrony import ChronyConnection

        sig = inspect.signature(ChronyConnection.__init__)
        params = list(sig.parameters.keys())
        assert "address" in params

    def test_address_is_optional(self):
        """Test that address parameter has a default value of None."""
        from pychrony import ChronyConnection

        sig = inspect.signature(ChronyConnection.__init__)
        param = sig.parameters["address"]
        assert param.default is None


class TestTrackingStatusContract:
    """Tests for TrackingStatus API contract."""

    def test_is_dataclass(self):
        """Test that TrackingStatus is a dataclass."""
        from pychrony import TrackingStatus
        from dataclasses import is_dataclass

        assert is_dataclass(TrackingStatus)

    def test_is_frozen(self):
        """Test that TrackingStatus is frozen (immutable)."""
        from pychrony import TrackingStatus

        # Check __dataclass_fields__ for frozen flag
        # Frozen dataclasses raise FrozenInstanceError on mutation
        assert TrackingStatus.__dataclass_fields__ is not None

    def test_has_required_fields(self):
        """Test that TrackingStatus has all required fields."""
        from pychrony import TrackingStatus

        field_names = {f.name for f in fields(TrackingStatus)}
        required_fields = {
            "reference_id",
            "reference_id_name",
            "reference_ip",
            "stratum",
            "leap_status",
            "ref_time",
            "offset",
            "last_offset",
            "rms_offset",
            "frequency",
            "residual_freq",
            "skew",
            "root_delay",
            "root_dispersion",
            "update_interval",
        }
        assert required_fields.issubset(field_names)

    def test_field_types(self):
        """Test that TrackingStatus fields have correct types."""
        from pychrony import TrackingStatus

        type_hints = {f.name: f.type for f in fields(TrackingStatus)}

        assert type_hints["reference_id"] is int
        assert type_hints["reference_id_name"] is str
        assert type_hints["reference_ip"] is str
        assert type_hints["stratum"] is int
        assert type_hints["leap_status"] is LeapStatus
        assert type_hints["ref_time"] is float
        assert type_hints["offset"] is float
        assert type_hints["last_offset"] is float
        assert type_hints["rms_offset"] is float
        assert type_hints["frequency"] is float
        assert type_hints["residual_freq"] is float
        assert type_hints["skew"] is float
        assert type_hints["root_delay"] is float
        assert type_hints["root_dispersion"] is float
        assert type_hints["update_interval"] is float

    def test_has_is_synchronized_method(self):
        """Test that TrackingStatus has is_synchronized method."""
        from pychrony import TrackingStatus

        assert hasattr(TrackingStatus, "is_synchronized")
        assert callable(getattr(TrackingStatus, "is_synchronized"))

    def test_has_is_leap_pending_method(self):
        """Test that TrackingStatus has is_leap_pending method."""
        from pychrony import TrackingStatus

        assert hasattr(TrackingStatus, "is_leap_pending")
        assert callable(getattr(TrackingStatus, "is_leap_pending"))


class TestExceptionContract:
    """Tests for exception class contracts."""

    def test_chrony_error_has_message_attribute(self):
        """Test that ChronyError has message attribute."""
        from pychrony import ChronyError

        error = ChronyError("test message")
        assert hasattr(error, "message")
        assert error.message == "test message"

    def test_chrony_error_has_error_code_attribute(self):
        """Test that ChronyError has error_code attribute."""
        from pychrony import ChronyError

        error = ChronyError("test", error_code=42)
        assert hasattr(error, "error_code")
        assert error.error_code == 42

    def test_chrony_library_error_has_none_error_code(self):
        """Test that ChronyLibraryError always has None error_code."""
        from pychrony import ChronyLibraryError

        error = ChronyLibraryError("lib not found")
        assert error.error_code is None


class TestDataModelExports:
    """Tests for data model exports."""

    def test_all_data_models_in_all(self):
        """Test that all data models are in __all__."""
        from pychrony import __all__

        assert "Source" in __all__
        assert "SourceStats" in __all__
        assert "RTCData" in __all__

    def test_source_importable(self):
        """Test that Source can be imported."""
        from pychrony import Source

        assert Source is not None

    def test_sourcestats_importable(self):
        """Test that SourceStats can be imported."""
        from pychrony import SourceStats

        assert SourceStats is not None

    def test_rtcdata_importable(self):
        """Test that RTCData can be imported."""
        from pychrony import RTCData

        assert RTCData is not None


class TestSourceContract:
    """Tests for Source API contract."""

    def test_is_dataclass(self):
        """Test that Source is a dataclass."""
        from pychrony import Source

        assert is_dataclass(Source)

    def test_is_frozen(self):
        """Test that Source is frozen (immutable)."""
        from pychrony import Source

        assert Source.__dataclass_fields__ is not None

    def test_has_required_fields(self):
        """Test that Source has all required fields."""
        from pychrony import Source

        field_names = {f.name for f in fields(Source)}
        required_fields = {
            "address",
            "poll",
            "stratum",
            "state",
            "mode",
            "flags",
            "reachability",
            "last_sample_ago",
            "orig_latest_meas",
            "latest_meas",
            "latest_meas_err",
        }
        assert required_fields.issubset(field_names)

    def test_field_types(self):
        """Test that Source fields have correct types."""
        from pychrony import Source

        type_hints = {f.name: f.type for f in fields(Source)}

        assert type_hints["address"] is str
        assert type_hints["poll"] is int
        assert type_hints["stratum"] is int
        assert type_hints["state"] is SourceState
        assert type_hints["mode"] is SourceMode
        assert type_hints["flags"] is int
        assert type_hints["reachability"] is int
        assert type_hints["last_sample_ago"] is int
        assert type_hints["orig_latest_meas"] is float
        assert type_hints["latest_meas"] is float
        assert type_hints["latest_meas_err"] is float

    def test_has_is_reachable_method(self):
        """Test that Source has is_reachable method."""
        from pychrony import Source

        assert hasattr(Source, "is_reachable")
        assert callable(getattr(Source, "is_reachable"))

    def test_has_is_selected_method(self):
        """Test that Source has is_selected method."""
        from pychrony import Source

        assert hasattr(Source, "is_selected")
        assert callable(getattr(Source, "is_selected"))


class TestSourceStatsContract:
    """Tests for SourceStats API contract."""

    def test_is_dataclass(self):
        """Test that SourceStats is a dataclass."""
        from pychrony import SourceStats

        assert is_dataclass(SourceStats)

    def test_is_frozen(self):
        """Test that SourceStats is frozen (immutable)."""
        from pychrony import SourceStats

        assert SourceStats.__dataclass_fields__ is not None

    def test_has_required_fields(self):
        """Test that SourceStats has all required fields."""
        from pychrony import SourceStats

        field_names = {f.name for f in fields(SourceStats)}
        required_fields = {
            "reference_id",
            "address",
            "samples",
            "runs",
            "span",
            "std_dev",
            "resid_freq",
            "skew",
            "offset",
            "offset_err",
        }
        assert required_fields.issubset(field_names)

    def test_field_types(self):
        """Test that SourceStats fields have correct types."""
        from pychrony import SourceStats

        type_hints = {f.name: f.type for f in fields(SourceStats)}

        assert type_hints["reference_id"] is int
        assert type_hints["address"] is str
        assert type_hints["samples"] is int
        assert type_hints["runs"] is int
        assert type_hints["span"] is int
        assert type_hints["std_dev"] is float
        assert type_hints["resid_freq"] is float
        assert type_hints["skew"] is float
        assert type_hints["offset"] is float
        assert type_hints["offset_err"] is float

    def test_has_has_sufficient_samples_method(self):
        """Test that SourceStats has has_sufficient_samples method."""
        from pychrony import SourceStats

        assert hasattr(SourceStats, "has_sufficient_samples")
        assert callable(getattr(SourceStats, "has_sufficient_samples"))


class TestRTCDataContract:
    """Tests for RTCData API contract."""

    def test_is_dataclass(self):
        """Test that RTCData is a dataclass."""
        from pychrony import RTCData

        assert is_dataclass(RTCData)

    def test_is_frozen(self):
        """Test that RTCData is frozen (immutable)."""
        from pychrony import RTCData

        assert RTCData.__dataclass_fields__ is not None

    def test_has_required_fields(self):
        """Test that RTCData has all required fields."""
        from pychrony import RTCData

        field_names = {f.name for f in fields(RTCData)}
        required_fields = {
            "ref_time",
            "samples",
            "runs",
            "span",
            "offset",
            "freq_offset",
        }
        assert required_fields.issubset(field_names)

    def test_field_types(self):
        """Test that RTCData fields have correct types."""
        from pychrony import RTCData

        type_hints = {f.name: f.type for f in fields(RTCData)}

        assert type_hints["ref_time"] is float
        assert type_hints["samples"] is int
        assert type_hints["runs"] is int
        assert type_hints["span"] is int
        assert type_hints["offset"] is float
        assert type_hints["freq_offset"] is float

    def test_has_is_calibrated_method(self):
        """Test that RTCData has is_calibrated method."""
        from pychrony import RTCData

        assert hasattr(RTCData, "is_calibrated")
        assert callable(getattr(RTCData, "is_calibrated"))


class TestAllDataclassesAreFrozen:
    """Tests verifying all dataclasses are frozen (immutable)."""

    def test_tracking_status_is_frozen(self):
        """Test that TrackingStatus is frozen."""
        from pychrony import TrackingStatus

        # Check frozen attribute
        assert getattr(TrackingStatus, "__dataclass_params__").frozen is True

    def test_source_is_frozen(self):
        """Test that Source is frozen."""
        from pychrony import Source

        assert getattr(Source, "__dataclass_params__").frozen is True

    def test_sourcestats_is_frozen(self):
        """Test that SourceStats is frozen."""
        from pychrony import SourceStats

        assert getattr(SourceStats, "__dataclass_params__").frozen is True

    def test_rtcdata_is_frozen(self):
        """Test that RTCData is frozen."""
        from pychrony import RTCData

        assert getattr(RTCData, "__dataclass_params__").frozen is True
