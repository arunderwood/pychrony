"""Keep _cffi_bindings.pyi in step with the cdef in _build_bindings.py.

The stub is what ty checks _bindings.py against, so a function added to or
changed in the cdef without a matching stub edit would go unchecked.
"""

import ast
import re
import tomllib
from pathlib import Path

CORE = Path(__file__).parents[2] / "src" / "pychrony" / "_core"


def _cdef_source() -> str:
    source = (CORE / "_build_bindings.py").read_text()
    match = re.search(r'ffi\.cdef\("""(.*?)"""\)', source, re.DOTALL)
    assert match, "cdef block not found in _build_bindings.py"
    # Drop // comments so prose cannot look like a declaration.
    return re.sub(r"//[^\n]*", "", match.group(1))


def _cdef_functions() -> dict[str, int]:
    """Map each declared libchrony function to its parameter count."""
    functions = {}
    for name, params in re.findall(r"\b(chrony_\w+)\s*\(([^)]*)\)\s*;", _cdef_source()):
        params = params.strip()
        functions[name] = 0 if params in ("", "void") else params.count(",") + 1
    return functions


def _cdef_enumerators() -> set[str]:
    return set(re.findall(r"\b(CHRONY_[A-Z_]+)\s*,", _cdef_source()))


def _stub_lib() -> ast.ClassDef:
    tree = ast.parse((CORE / "_cffi_bindings.pyi").read_text())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "_Lib":
            return node
    raise AssertionError("_Lib not found in _cffi_bindings.pyi")


def test_stub_declares_every_cdef_function_with_matching_arity():
    stub = {
        node.name: len(node.args.posonlyargs) + len(node.args.args) - 1  # self
        for node in _stub_lib().body
        if isinstance(node, ast.FunctionDef)
    }
    assert stub == _cdef_functions()


def test_stub_declares_every_named_enumerator():
    stub = {
        node.target.id
        for node in _stub_lib().body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assert stub == _cdef_enumerators()


def test_stub_is_package_data():
    """The stub must ship, or installed copies of pychrony lose the types."""
    pyproject = tomllib.loads((CORE.parents[2] / "pyproject.toml").read_text())
    package_data = pyproject["tool"]["setuptools"]["package-data"]["pychrony"]
    assert "_core/*.pyi" in package_data
