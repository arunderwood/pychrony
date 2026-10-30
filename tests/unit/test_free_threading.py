"""Free-threaded (PEP 703) interpreter support.

An extension module that does not declare free-threading support makes CPython
re-enable the GIL when it is imported. CFFI 2.0+ generates modules that declare
it, so importing the compiled bindings must leave the GIL disabled.
"""

import os
import sys
import sysconfig

import pytest

pytestmark = pytest.mark.skipif(
    not sysconfig.get_config_var("Py_GIL_DISABLED"),
    reason="requires a free-threaded CPython build",
)


def test_compiled_bindings_keep_gil_disabled():
    """Importing the compiled CFFI module must not re-enable the GIL."""
    if os.environ.get("PYTHON_GIL") == "1" or sys.flags.gil == 1:
        pytest.skip("GIL forced on via PYTHON_GIL / -X gil")

    try:
        import pychrony._core._cffi_bindings  # noqa: F401
    except ImportError:
        # Wheels built by cibuildwheel always contain the bindings; anywhere
        # else (plain `uv sync`) they are optional.
        if os.environ.get("CIBUILDWHEEL") == "1":
            raise
        pytest.skip("compiled bindings not built")

    assert not sys._is_gil_enabled()
