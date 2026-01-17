"""Unit tests for pychrony enum classes."""

import pytest

from pychrony import LeapStatus, SourceState, SourceMode


class TestSourceStateEnum:
    """Tests for SourceState enum (T006, T008)."""

    def test_has_all_members(self):
        """Test SourceState has all expected members."""
        assert hasattr(SourceState, "SELECTED")
        assert hasattr(SourceState, "NONSELECTABLE")
        assert hasattr(SourceState, "FALSETICKER")
        assert hasattr(SourceState, "JITTERY")
        assert hasattr(SourceState, "UNSELECTED")
        assert hasattr(SourceState, "SELECTABLE")

    def test_member_values(self):
        """Test SourceState members have correct integer values."""
        assert SourceState.SELECTED.value == 0
        assert SourceState.NONSELECTABLE.value == 1
        assert SourceState.FALSETICKER.value == 2
        assert SourceState.JITTERY.value == 3
        assert SourceState.UNSELECTED.value == 4
        assert SourceState.SELECTABLE.value == 5

    def test_name_attribute(self):
        """Test SourceState .name attribute returns uppercase string."""
        assert SourceState.SELECTED.name == "SELECTED"
        assert SourceState.NONSELECTABLE.name == "NONSELECTABLE"
        assert SourceState.FALSETICKER.name == "FALSETICKER"
        assert SourceState.JITTERY.name == "JITTERY"
        assert SourceState.UNSELECTED.name == "UNSELECTED"
        assert SourceState.SELECTABLE.name == "SELECTABLE"

    def test_value_attribute(self):
        """Test SourceState .value attribute returns integer."""
        for member in SourceState:
            assert isinstance(member.value, int)

    def test_construction_from_value(self):
        """Test SourceState can be constructed from integer value."""
        assert SourceState(0) == SourceState.SELECTED
        assert SourceState(1) == SourceState.NONSELECTABLE
        assert SourceState(2) == SourceState.FALSETICKER
        assert SourceState(3) == SourceState.JITTERY
        assert SourceState(4) == SourceState.UNSELECTED
        assert SourceState(5) == SourceState.SELECTABLE

    def test_invalid_value_raises_valueerror(self):
        """Test SourceState raises ValueError for invalid integer."""
        with pytest.raises(ValueError):
            SourceState(6)
        with pytest.raises(ValueError):
            SourceState(-1)
        with pytest.raises(ValueError):
            SourceState(99)

    def test_member_count(self):
        """Test SourceState has exactly 6 members."""
        assert len(SourceState) == 6

    def test_equality_with_same_member(self):
        """Test SourceState members are equal to themselves."""
        assert SourceState.SELECTED == SourceState.SELECTED
        assert SourceState(0) == SourceState.SELECTED

    def test_inequality_with_different_member(self):
        """Test SourceState members are not equal to different members."""
        assert SourceState.SELECTED != SourceState.UNSELECTED

    def test_not_equal_to_integer(self):
        """Test SourceState is not equal to raw integer (not IntEnum)."""
        # This is the key difference from IntEnum - enum != int
        assert SourceState.SELECTED != 0
        assert SourceState.NONSELECTABLE != 1


class TestLeapStatusEnum:
    """Tests for LeapStatus enum (T016, T018)."""

    def test_has_all_members(self):
        """Test LeapStatus has all expected members."""
        assert hasattr(LeapStatus, "NORMAL")
        assert hasattr(LeapStatus, "INSERT")
        assert hasattr(LeapStatus, "DELETE")
        assert hasattr(LeapStatus, "UNSYNC")

    def test_member_values(self):
        """Test LeapStatus members have correct integer values."""
        assert LeapStatus.NORMAL.value == 0
        assert LeapStatus.INSERT.value == 1
        assert LeapStatus.DELETE.value == 2
        assert LeapStatus.UNSYNC.value == 3

    def test_name_attribute(self):
        """Test LeapStatus .name attribute returns uppercase string."""
        assert LeapStatus.NORMAL.name == "NORMAL"
        assert LeapStatus.INSERT.name == "INSERT"
        assert LeapStatus.DELETE.name == "DELETE"
        assert LeapStatus.UNSYNC.name == "UNSYNC"

    def test_value_attribute(self):
        """Test LeapStatus .value attribute returns integer."""
        for member in LeapStatus:
            assert isinstance(member.value, int)

    def test_construction_from_value(self):
        """Test LeapStatus can be constructed from integer value."""
        assert LeapStatus(0) == LeapStatus.NORMAL
        assert LeapStatus(1) == LeapStatus.INSERT
        assert LeapStatus(2) == LeapStatus.DELETE
        assert LeapStatus(3) == LeapStatus.UNSYNC

    def test_invalid_value_raises_valueerror(self):
        """Test LeapStatus raises ValueError for invalid integer."""
        with pytest.raises(ValueError):
            LeapStatus(4)
        with pytest.raises(ValueError):
            LeapStatus(-1)
        with pytest.raises(ValueError):
            LeapStatus(99)

    def test_member_count(self):
        """Test LeapStatus has exactly 4 members."""
        assert len(LeapStatus) == 4

    def test_not_equal_to_integer(self):
        """Test LeapStatus is not equal to raw integer (not IntEnum)."""
        assert LeapStatus.NORMAL != 0
        assert LeapStatus.INSERT != 1


class TestSourceModeEnum:
    """Tests for SourceMode enum (T025, T027)."""

    def test_has_all_members(self):
        """Test SourceMode has all expected members."""
        assert hasattr(SourceMode, "CLIENT")
        assert hasattr(SourceMode, "PEER")
        assert hasattr(SourceMode, "REFCLOCK")

    def test_member_values(self):
        """Test SourceMode members have correct integer values."""
        assert SourceMode.CLIENT.value == 0
        assert SourceMode.PEER.value == 1
        assert SourceMode.REFCLOCK.value == 2

    def test_name_attribute(self):
        """Test SourceMode .name attribute returns uppercase string."""
        assert SourceMode.CLIENT.name == "CLIENT"
        assert SourceMode.PEER.name == "PEER"
        assert SourceMode.REFCLOCK.name == "REFCLOCK"

    def test_value_attribute(self):
        """Test SourceMode .value attribute returns integer."""
        for member in SourceMode:
            assert isinstance(member.value, int)

    def test_construction_from_value(self):
        """Test SourceMode can be constructed from integer value."""
        assert SourceMode(0) == SourceMode.CLIENT
        assert SourceMode(1) == SourceMode.PEER
        assert SourceMode(2) == SourceMode.REFCLOCK

    def test_invalid_value_raises_valueerror(self):
        """Test SourceMode raises ValueError for invalid integer."""
        with pytest.raises(ValueError):
            SourceMode(3)
        with pytest.raises(ValueError):
            SourceMode(-1)
        with pytest.raises(ValueError):
            SourceMode(99)

    def test_member_count(self):
        """Test SourceMode has exactly 3 members."""
        assert len(SourceMode) == 3

    def test_not_equal_to_integer(self):
        """Test SourceMode is not equal to raw integer (not IntEnum)."""
        assert SourceMode.CLIENT != 0
        assert SourceMode.PEER != 1
