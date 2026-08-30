# pychrony

Python bindings for libchrony - read-only monitoring of chronyd NTP daemon.

## Installation

```bash
pip install pychrony
```

## Quick Example

```python
from pychrony import ChronyConnection

with ChronyConnection() as conn:
    status = conn.get_tracking()
    print(f"Offset: {status.offset:.6f} seconds")
    print(f"Stratum: {status.stratum}")
    if status.is_synchronized():
        print(f"Synchronized to {status.reference_id_name}")
```

## Features

- **Read-only monitoring**: Query chronyd status without modification capabilities
- **Full type hints**: Complete type annotations for IDE support
- **Pythonic API**: Native Python data structures and context managers
- **Multiple reports**: Access tracking, sources, source stats, and RTC data

## Multiple Queries (Connection Reuse)

Use a single connection for multiple queries to minimize overhead:

```python
from pychrony import ChronyConnection

with ChronyConnection() as conn:
    tracking = conn.get_tracking()
    sources = conn.get_sources()
    stats = conn.get_source_stats()
    rtc = conn.get_rtc_data()
```

## Error Handling

pychrony provides typed exceptions for different error conditions:

```python
from pychrony import (
    ChronyConnection,
    ChronyError,
    ChronyLibraryError,
    ChronyConnectionError,
    ChronyPermissionError,
)

try:
    with ChronyConnection() as conn:
        status = conn.get_tracking()
except ChronyLibraryError:
    print("libchrony not installed")
except ChronyPermissionError:
    # chronyd's Unix socket is its control channel and is restricted to the
    # root or chrony user. For read-only monitoring, use the command port.
    print("Permission denied - falling back to the command port")
    with ChronyConnection("127.0.0.1") as conn:
        status = conn.get_tracking()
except ChronyConnectionError:
    print("chronyd unreachable")
```

`ChronyConnectionError` means chronyd could not be reached — the connection
would not open, or it opened and nothing answered. The second is normal on the
command port, which is UDP: the socket opens whether or not chronyd is
listening, so a disabled port only surfaces on the first request.
`ChronyDataError` is reserved for a report that arrived but was malformed.

## Choosing a Transport

With no argument, `ChronyConnection` tries each candidate in turn — the default
Unix socket paths, then the localhost command port — and uses the first that
connects. A socket path that exists is not assumed usable: connecting to a Unix
socket requires write permission, so a present socket can still refuse, and
auto-detect moves on when it does. These are the same candidates
[chronyc uses](https://chrony-project.org/doc/4.9/chronyc.html).

!!! note "The IPv6 candidate is close to a formality"

    The command port is UDP, so opening a socket succeeds with nothing
    listening, and the IPv4 candidate wins whenever an IPv4 socket can be
    created. On a host serving the command port on `::1` alone, pass `"[::1]"`
    explicitly.

The two transports do not carry the same privileges:

| | Unix socket | Command port |
| --- | --- | --- |
| Address | `/run/chrony/chronyd.sock` | `127.0.0.1`, `[::1]` (port 323) |
| Access | root or the `chrony` user only | localhost by default (`cmdallow`) |
| Capability | chronyd's control channel | monitoring commands only |

chrony describes full access through the Unix socket as "more or less equivalent
to being able to modify the chronyd's configuration file and restart it";
anything outside the monitoring set is refused over the command port with
`Not authorised`, even from localhost.

**For read-only monitoring, prefer the command port.** Every report pychrony
reads — `tracking`, `sources`, `sourcestats` and `rtcdata` — is in the set
chronyd serves over it, so it costs nothing in capability. chronyd binds it to
localhost by default; `cmdport 0` disables it (but not the Unix socket).

!!! warning "Joining the `chrony` group does not grant socket access"

    chronyd creates the socket owned by the `chrony` user without group write,
    and connecting requires write permission. chrony also requires the socket's
    directory to be accessible only by the root or chrony user, so loosening
    these permissions works against its design — and buys a control channel a
    monitoring client does not need.

See the [chrony.conf man page](https://chrony-project.org/doc/4.9/chrony.conf.html)
for `cmdport`, `bindcmdaddress` and `cmdallow`.

`address` and `transport` report what the connection actually settled on, so a
caller that must not hold a control channel can assert on it:

```python
from pychrony import ChronyConnection, Transport

with ChronyConnection() as conn:
    if conn.transport is not Transport.COMMAND_PORT:
        raise RuntimeError(f"refusing to hold a control channel ({conn.address})")
    status = conn.get_tracking()
```

Both are `None` outside an open connection.

## Remote and Custom Connections

An explicit address is used as given, with no fallback — asking for a specific
transport never lands you silently on another one.

Connect to a custom Unix socket path:

```python
with ChronyConnection("/custom/path/chronyd.sock") as conn:
    status = conn.get_tracking()
```

Connect to a remote chronyd instance via UDP:

```python
with ChronyConnection("192.168.1.100") as conn:
    status = conn.get_tracking()
```

This needs configuration on the remote host, which does not allow it by default:
chronyd binds its command port to loopback only (`bindcmdaddress`) and accepts
monitoring commands only from localhost (`cmdallow`). Widening either exposes
chronyd's monitoring data to the network, so scope `cmdallow` to the hosts that
need it. The command port is unauthenticated, so treat it as readable by anyone
who can reach it.

## Thread Safety

`ChronyConnection` is **NOT thread-safe**. The underlying libchrony session
maintains stateful request/response cycles that cannot be safely shared
between threads.

For multi-threaded applications, use one of these patterns:

**Connection per thread (simplest):**

```python
def worker():
    with ChronyConnection() as conn:
        return conn.get_tracking()
```

**Thread-local storage (for connection reuse):**

```python
import threading

_local = threading.local()


def get_tracking():
    if not hasattr(_local, "conn"):
        _local.conn = ChronyConnection()
    with _local.conn as conn:
        return conn.get_tracking()
```

The returned dataclasses (`TrackingStatus`, `Source`, etc.) are frozen and
immutable, so they can be safely shared across threads after retrieval.

## Quick Links

- [API Reference](api/index.md) - Complete API documentation
- [GitHub Repository](https://github.com/arunderwood/pychrony) - Source code and issues
- [PyPI Package](https://pypi.org/project/pychrony/) - Installation

## Requirements

- Python 3.10+
- libchrony (system library)
- Linux (primary platform)
