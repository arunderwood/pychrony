"""Integration test configuration.

Every test here is guarded by ``HAS_CFFI_BINDINGS`` so the suite can be
collected on a machine without compiled bindings. That guard makes a run with
no bindings look almost exactly like a passing one, which is the wrong outcome
in an environment built to prove the bindings work.

In that environment - the test image, which sets ``PYCHRONY_INTEGRATION_STRICT``
- missing bindings are a hard error instead. Elsewhere the tests still skip.
"""

import importlib.util
import os

import pytest

STRICT_ENV_VAR = "PYCHRONY_INTEGRATION_STRICT"


def pytest_configure(config: pytest.Config) -> None:
    """Fail rather than skip when the environment promised working bindings."""
    if os.environ.get(STRICT_ENV_VAR) != "1":
        return

    if importlib.util.find_spec("pychrony._core._cffi_bindings") is None:
        raise pytest.UsageError(
            "pychrony._core._cffi_bindings is not importable, so every "
            f"integration test would skip. {STRICT_ENV_VAR} is set, meaning "
            "this environment is supposed to have the compiled bindings. A "
            "common cause is mounting the host's src/ over /app/src, which "
            "hides the .so the image built."
        )
