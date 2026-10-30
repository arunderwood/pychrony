"""Setup script for building CFFI extensions.

The CFFI bindings to libchrony are compiled by default, so an sdist install
produces a working package. That requires libchrony (chrony.h and the shared
library) and a C compiler at build time.

Set PYCHRONY_SKIP_CFFI=1 to skip compilation, e.g. for development on a system
without libchrony. The resulting install imports, but any connection attempt
raises ChronyLibraryError. ``[tool.uv]`` in pyproject.toml sets this for
``uv sync`` and ``uv pip``.

PYCHRONY_BUILD_CFFI=1, formerly the opt-in, overrides PYCHRONY_SKIP_CFFI, e.g.
``PYCHRONY_BUILD_CFFI=1 uv sync`` builds the bindings despite the uv config.
Otherwise it is a no-op. cibuildwheel (CIBUILDWHEEL=1) always compiles, since a
wheel without bindings would be broken.
"""

import os
import tempfile

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.errors import CompileError, LinkError, PlatformError

CFFI_EXTENSION = "pychrony._core._cffi_bindings"

LIBCHRONY_HELP = """\
pychrony needs libchrony to compile its CFFI bindings.
Install libchrony and a C compiler, then retry:

  Fedora 42+:  dnf install libchrony-devel gcc
  RHEL 9:      dnf install epel-release
               dnf install libchrony-devel gcc
  Others:      build https://gitlab.com/chrony/libchrony
               make && make install prefix=/usr && ldconfig

For a non-standard prefix, set CFLAGS=-I<prefix>/include
and LDFLAGS=-L<prefix>/lib.

To install without the bindings (development only:
pychrony cannot query chronyd), set PYCHRONY_SKIP_CFFI=1."""


class build_ext_with_libchrony_check(build_ext):
    """build_ext that checks for libchrony before compiling the bindings.

    Without this, a missing libchrony surfaces as a raw compiler or linker
    error from the CFFI-generated source.
    """

    def build_extension(self, ext):
        if ext.name == CFFI_EXTENSION:
            self._check_libchrony(ext)
        super().build_extension(ext)

    def _check_libchrony(self, ext):
        include_dirs = list(ext.include_dirs) + list(self.include_dirs or [])
        library_dirs = list(ext.library_dirs) + list(self.library_dirs or [])
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "check_libchrony.c")
            with open(src, "w") as f:
                f.write(
                    "#include <chrony.h>\n"
                    "int main(void) { return chrony_open_socket == 0; }\n"
                )
            try:
                objects = self.compiler.compile(
                    [src], output_dir=tmp, include_dirs=include_dirs
                )
            except CompileError:
                raise PlatformError(
                    f"chrony.h not found.\n\n{LIBCHRONY_HELP}"
                ) from None
            try:
                self.compiler.link_executable(
                    objects,
                    "check_libchrony",
                    output_dir=tmp,
                    libraries=["chrony"],
                    library_dirs=library_dirs,
                )
            except LinkError:
                raise PlatformError(
                    f"libchrony shared library not found.\n\n{LIBCHRONY_HELP}"
                ) from None


force = (
    os.environ.get("CIBUILDWHEEL") == "1"
    or os.environ.get("PYCHRONY_BUILD_CFFI") == "1"
)
skip = os.environ.get("PYCHRONY_SKIP_CFFI") == "1" and not force

if skip:
    setup()
else:
    setup(
        cffi_modules=["src/pychrony/_core/_build_bindings.py:ffi"],
        cmdclass={"build_ext": build_ext_with_libchrony_check},
    )
