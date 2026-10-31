"""Compiling by default means a source install either works or fails at build
time, never yielding a package that cannot reach chronyd.

PYCHRONY_SKIP_CFFI=1 is for development without libchrony; ``[tool.uv]`` in
pyproject.toml sets it for uv installs of the project. Such an install imports,
but connecting raises ChronyLibraryError. cibuildwheel always compiles because a
wheel without bindings is broken.
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

For a non-standard prefix, add <prefix>/lib/pkgconfig to
PKG_CONFIG_PATH (or set CFLAGS=-I<prefix>/include and
LDFLAGS=-L<prefix>/lib).

To install without the bindings (development only:
pychrony cannot query chronyd), set PYCHRONY_SKIP_CFFI=1."""


class build_ext_with_libchrony_check(build_ext):
    """Without this, a missing libchrony surfaces as a raw compiler or linker
    error from the CFFI-generated source."""

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


def should_build_cffi(environ=os.environ):
    if environ.get("CIBUILDWHEEL") == "1" or environ.get("PYCHRONY_BUILD_CFFI") == "1":
        return True
    return environ.get("PYCHRONY_SKIP_CFFI") != "1"


# setuptools' PEP 517 backend runs this file as __main__; the guard lets tests
# import it without running setup().
if __name__ == "__main__":
    if should_build_cffi():
        setup(
            cffi_modules=["src/pychrony/_core/_build_bindings.py:ffibuilder"],
            cmdclass={"build_ext": build_ext_with_libchrony_check},
        )
    else:
        setup()
