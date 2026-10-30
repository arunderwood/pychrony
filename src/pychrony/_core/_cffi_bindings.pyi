"""Type stub for the CFFI extension built by _build_bindings.py.

The extension is compiled at install time and is absent from a source checkout,
so this stub gives type checkers its interface. It has no effect at runtime:
the import system never loads .pyi files, so importing the module still raises
ImportError when the compiled extension is missing.

Keep `_Lib` in step with the cdef in _build_bindings.py; a unit test compares
the two. The classes below are stub-only and do not exist at runtime: import
them under TYPE_CHECKING only.
"""

from typing import Literal, overload, type_check_only

@type_check_only
class _CData:
    """Any CFFI cdata object."""

@type_check_only
class _ChronySession(_CData):
    """chrony_session * (opaque handle)."""

@type_check_only
class _ChronySessionPtr(_CData):
    """chrony_session ** (out-parameter for chrony_init_session)."""

    def __getitem__(self, index: int, /) -> _ChronySession: ...

@type_check_only
class _CharPtr(_CData):
    """const char * returned by libchrony."""

@type_check_only
class _Timespec(_CData):
    """struct timespec, returned by value."""

    tv_sec: int
    tv_nsec: int

@type_check_only
class _FFI:
    NULL: _CData
    @overload
    def new(self, cdecl: Literal["chrony_session **"], /) -> _ChronySessionPtr: ...
    @overload
    def new(self, cdecl: str, init: object = ..., /) -> _CData: ...
    def string(self, cdata: _CharPtr, maxlen: int = ..., /) -> bytes: ...

@type_check_only
class _Lib:
    # chrony_err enumerators named in the cdef. CFFI passes enum values as int.
    CHRONY_OK: int
    CHRONY_SEND_FAILED: int
    CHRONY_RECV_FAILED: int
    CHRONY_UNEXPECTED_STATUS: int

    # Connection management
    def chrony_open_socket(self, address: bytes, /) -> int: ...
    def chrony_close_socket(self, fd: int, /) -> None: ...
    def chrony_init_session(self, session: _ChronySessionPtr, fd: int, /) -> int: ...
    def chrony_deinit_session(self, session: _ChronySession, /) -> None: ...

    # Request/response lifecycle
    def chrony_request_report_number_records(
        self, s: _ChronySession, report: bytes, /
    ) -> int: ...
    def chrony_needs_response(self, s: _ChronySession, /) -> bool: ...
    def chrony_process_response(self, s: _ChronySession, /) -> int: ...
    def chrony_get_report_number_records(self, s: _ChronySession, /) -> int: ...
    def chrony_request_record(
        self, s: _ChronySession, report: bytes, record: int, /
    ) -> int: ...

    # Field access
    def chrony_get_field_index(self, s: _ChronySession, name: bytes, /) -> int: ...
    def chrony_get_field_float(self, s: _ChronySession, field: int, /) -> float: ...
    def chrony_get_field_uinteger(self, s: _ChronySession, field: int, /) -> int: ...
    def chrony_get_field_integer(self, s: _ChronySession, field: int, /) -> int: ...
    def chrony_get_field_string(self, s: _ChronySession, field: int, /) -> _CharPtr: ...
    def chrony_get_field_timespec(
        self, s: _ChronySession, field: int, /
    ) -> _Timespec: ...

ffi: _FFI
lib: _Lib
