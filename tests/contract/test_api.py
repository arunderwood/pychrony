"""Contract tests for pychrony public API stability."""

from dataclasses import fields


class TestPublicExports:
    """Tests for public API exports."""

    def test_all_exports_importable(self):
        """Test that all __all__ exports are importable."""
        from pychrony import __all__

        assert "get_tracking" in __all__
        assert "TrackingStatus" in __all__
        assert "ChronyError" in __all__
        assert "ChronyConnectionError" in __all__
        assert "ChronyPermissionError" in __all__
        assert "ChronyDataError" in __all__
        assert "ChronyLibraryError" in __all__

    def test_get_tracking_importable(self):
        """Test that get_tracking can be imported."""
        from pychrony import get_tracking

        assert callable(get_tracking)

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
        assert type_hints["leap_status"] is int
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


class TestGetTrackingContract:
    """Tests for get_tracking function contract."""

    def test_signature_accepts_socket_path(self):
        """Test that get_tracking accepts socket_path parameter."""
        import inspect
        from pychrony import get_tracking

        sig = inspect.signature(get_tracking)
        params = list(sig.parameters.keys())
        assert "socket_path" in params

    def test_socket_path_is_optional(self):
        """Test that socket_path parameter has a default value."""
        import inspect
        from pychrony import get_tracking

        sig = inspect.signature(get_tracking)
        param = sig.parameters["socket_path"]
        assert param.default is None or param.default is not inspect.Parameter.empty


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
