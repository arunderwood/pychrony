"""Setup script for building CFFI extensions.

CFFI bindings are only compiled when:
1. Running in cibuildwheel (CIBUILDWHEEL=1 environment variable)
2. Or when PYCHRONY_BUILD_CFFI=1 is set explicitly

This allows local development without requiring libchrony installation.
"""

import os

from setuptools import setup

# Only compile CFFI bindings in cibuildwheel or when explicitly requested
if (
    os.environ.get("CIBUILDWHEEL") == "1"
    or os.environ.get("PYCHRONY_BUILD_CFFI") == "1"
):
    setup(
        cffi_modules=["src/pychrony/_core/_build_bindings.py:ffi"],
    )
else:
    setup()
