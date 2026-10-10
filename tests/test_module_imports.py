"""Tests for lightweight module imports."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_port_scanner_import_does_not_load_optional_module_dependencies():
    code = (
        "import sys; import zer0specter.modules.port_scanner; "
        "assert 'scapy' not in sys.modules; "
        "assert 'pyzipper' not in sys.modules"
    )

    subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_package_reexports_remain_handlers_after_submodule_import():
    code = (
        "import importlib; import zer0specter.modules as modules; "
        "assert set(modules.__all__) == {'password_generator', 'ip_locator', "
        "'portscanner', 'zipcrack', 'sniffer', 'wifi_attack'}; "
        "importlib.import_module('zer0specter.modules.sniffer'); "
        "assert callable(modules.sniffer)"
    )

    subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    ("module_name", "function_name", "blocked_dependency"),
    [
        ("zer0specter.modules.sniffer", "sniffer", "scapy"),
        ("zer0specter.modules.wifi_attack", "wifi_attack", "scapy"),
        ("zer0specter.modules.zip_cracker", "zipcrack", "pyzipper"),
    ],
)
def test_module_help_does_not_import_operation_dependency(
    module_name, function_name, blocked_dependency
):
    code = f"""
import builtins, importlib, sys
original_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name.split('.')[0] == {blocked_dependency!r}:
        raise ImportError('dependency deliberately blocked')
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
module = importlib.import_module({module_name!r})
try:
    getattr(module, {function_name!r})(['--help'])
except SystemExit as error:
    assert error.code == 0
else:
    raise AssertionError('help did not exit successfully')
assert not any(name.split('.')[0] == {blocked_dependency!r} for name in sys.modules)
"""
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
