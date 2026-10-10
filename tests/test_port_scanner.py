"""Behavioral tests for the port scanner command handler."""

import socket
from unittest.mock import MagicMock

import pytest

from zer0specter.modules import port_scanner


@pytest.fixture(autouse=True)
def quiet_logger(monkeypatch):
    monkeypatch.setattr(port_scanner, "get_logger", lambda: MagicMock())


def make_socket(monkeypatch, *, banner=b"", banner_response=b""):
    sock = MagicMock()
    sock.__enter__.return_value = sock
    sock.recv.side_effect = [banner, banner_response]
    monkeypatch.setattr(port_scanner.socket, "socket", lambda *args: sock)
    return sock


def test_open_port_without_banner_is_reported_without_active_probe(monkeypatch, capsys):
    sock = make_socket(monkeypatch)

    status = port_scanner.portscanner(
        ["--target", "127.0.0.1", "--start", "80", "--end", "80"]
    )

    assert status == 0
    assert "80/tcp open" in capsys.readouterr().out
    sock.sendall.assert_not_called()


def test_banner_probe_is_opt_in_and_does_not_change_open_state(monkeypatch, capsys):
    sock = make_socket(monkeypatch, banner=b"", banner_response=b"Server: example\r\n")

    status = port_scanner.portscanner(
        [
            "--target",
            "127.0.0.1",
            "--start",
            "80",
            "--end",
            "80",
            "--banner",
        ]
    )

    assert status == 0
    output = capsys.readouterr().out
    assert "80/tcp open" in output
    assert "Server: example" in output
    sock.sendall.assert_called_once()


def test_connection_refused_is_not_reported_as_open(monkeypatch, capsys):
    sock = make_socket(monkeypatch)
    sock.connect.side_effect = ConnectionRefusedError

    status = port_scanner.portscanner(
        ["--target", "127.0.0.1", "--start", "80", "--end", "80"]
    )

    assert status == 0
    assert "80/tcp open" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "args",
    [
        ["--target", "127.0.0.1", "--start", "0", "--end", "80"],
        ["--target", "127.0.0.1", "--start", "80", "--end", "79"],
        ["--target", "127.0.0.1", "--start", "80", "--end", "70000"],
        ["--target", "127.0.0.1", "--timeout", "nan"],
        ["--target", "::1"],
    ],
)
def test_invalid_scan_inputs_return_usage_error(monkeypatch, args):
    sock = make_socket(monkeypatch)

    with pytest.raises(SystemExit) as error:
        port_scanner.portscanner(args)

    assert error.value.code == 2
    sock.connect.assert_not_called()


def test_dns_failure_returns_runtime_error(monkeypatch):
    monkeypatch.setattr(
        port_scanner.socket, "gethostbyname", MagicMock(side_effect=socket.gaierror)
    )

    assert port_scanner.portscanner(["--target", "missing.invalid"]) == 1
