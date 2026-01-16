"""CFFI build script for libchrony bindings.

This module generates compiled CFFI bindings to libchrony using API mode.
Run directly to compile: python -m pychrony._core._build_bindings

Requires libchrony-devel headers at build time.
"""

from cffi import FFI

ffi = FFI()

# Define the C interface to libchrony's high-level introspection API
ffi.cdef("""
// Opaque session handle
typedef struct chrony_session chrony_session;

// Error codes
typedef int chrony_err;

// Connection management
int chrony_open_socket(const char *address);
chrony_err chrony_init_session(chrony_session **session, int fd);
void chrony_deinit_session(chrony_session *session);

// Request/response lifecycle
chrony_err chrony_request_report_number_records(chrony_session *s, const char *report);
bool chrony_needs_response(chrony_session *s);
chrony_err chrony_process_response(chrony_session *s);
int chrony_get_report_number_records(chrony_session *s);
chrony_err chrony_request_record(chrony_session *s, const char *report, int record);

// Field access - native C types
int chrony_get_field_index(chrony_session *s, const char *name);
double chrony_get_field_float(chrony_session *s, int field);
uint64_t chrony_get_field_uinteger(chrony_session *s, int field);
int64_t chrony_get_field_integer(chrony_session *s, int field);
const char *chrony_get_field_string(chrony_session *s, int field);

// Timespec for reference time
struct timespec {
    long tv_sec;
    long tv_nsec;
};
struct timespec chrony_get_field_timespec(chrony_session *s, int field);
""")

# Set up compiled bindings (API mode)
ffi.set_source(
    "pychrony._core._cffi_bindings",
    "#include <chrony.h>",
    libraries=["chrony"],
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
