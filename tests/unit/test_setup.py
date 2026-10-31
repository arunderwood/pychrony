"""Tests for setup.py: when the CFFI bindings build, and missing-libchrony errors.

setup.py only runs setup() as __main__, so importing it here is side-effect
free. setuptools is a dev dependency but is absent from cibuildwheel's wheel
test environment (which runs tests/unit too) or may be older there, so these
skip unless the build-system minimum is installed.
"""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("setuptools", minversion="77.0.1")

from cffi import FFI
from setuptools import Distribution, Extension
from setuptools.errors import CompileError, LinkError, PlatformError

ROOT = Path(__file__).parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


setup_py = _load("pychrony_setup", ROOT / "setup.py")


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        ({}, True),
        ({"PYCHRONY_SKIP_CFFI": "1"}, False),
        ({"PYCHRONY_SKIP_CFFI": "0"}, True),
        ({"PYCHRONY_BUILD_CFFI": "1"}, True),
        ({"PYCHRONY_SKIP_CFFI": "1", "PYCHRONY_BUILD_CFFI": "1"}, True),
        ({"PYCHRONY_SKIP_CFFI": "1", "CIBUILDWHEEL": "1"}, True),
    ],
)
def test_should_build_cffi(environ, expected):
    assert setup_py.should_build_cffi(environ) is expected


def test_cffi_modules_target_exists():
    """The "path:attribute" setup.py hands cffi names a real FFI builder."""
    module = _load(
        "pychrony_build_bindings", ROOT / "src/pychrony/_core/_build_bindings.py"
    )
    assert isinstance(module.ffibuilder, FFI)
    assert module.MODULE_NAME == setup_py.CFFI_EXTENSION


class _FakeCompiler:
    def __init__(self, fail_compile=False, fail_link=False):
        self.fail_compile = fail_compile
        self.fail_link = fail_link
        self.compile_kwargs = None
        self.link_kwargs = None

    def compile(self, sources, **kwargs):
        self.compile_kwargs = kwargs
        if self.fail_compile:
            raise CompileError("fatal error: chrony.h: No such file or directory")
        return ["check_libchrony.o"]

    def link_executable(self, objects, name, **kwargs):
        self.link_kwargs = kwargs
        if self.fail_link:
            raise LinkError("cannot find -lchrony")


def _check(compiler):
    cmd = setup_py.build_ext_with_libchrony_check(Distribution())
    cmd.compiler = compiler
    cmd.include_dirs = ["/opt/cmdline/include"]
    cmd.library_dirs = ["/opt/cmdline/lib"]
    ext = Extension(
        setup_py.CFFI_EXTENSION,
        sources=[],
        include_dirs=["/opt/pkgconfig/include"],
        library_dirs=["/opt/pkgconfig/lib"],
    )
    cmd._check_libchrony(ext)


def test_check_passes_extension_and_command_search_paths():
    compiler = _FakeCompiler()
    _check(compiler)
    assert compiler.compile_kwargs["include_dirs"] == [
        "/opt/pkgconfig/include",
        "/opt/cmdline/include",
    ]
    assert compiler.link_kwargs["libraries"] == ["chrony"]
    assert compiler.link_kwargs["library_dirs"] == [
        "/opt/pkgconfig/lib",
        "/opt/cmdline/lib",
    ]


def test_missing_header_is_a_clear_error():
    with pytest.raises(PlatformError, match=r"chrony\.h not found") as excinfo:
        _check(_FakeCompiler(fail_compile=True))
    assert "PYCHRONY_SKIP_CFFI=1" in str(excinfo.value)


def test_missing_library_is_a_clear_error():
    with pytest.raises(PlatformError, match="libchrony shared library not found"):
        _check(_FakeCompiler(fail_link=True))
