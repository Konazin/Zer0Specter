"""Tests for packet capture and Wi-Fi output without live network access."""

import sys
import types
import importlib
from unittest.mock import MagicMock

import pytest

sniffer = importlib.import_module("zer0specter.modules.sniffer")
wifi_attack = importlib.import_module("zer0specter.modules.wifi_attack")


class Layer:
    def __init__(self, *args, **kwargs):
        pass

    def __truediv__(self, other):
        return self


class Packet:
    def haslayer(self, _layer):
        return False

    def __len__(self):
        return 64


@pytest.fixture
def fake_scapy(monkeypatch):
    package = types.ModuleType("scapy")
    package.__path__ = []
    all_module = types.ModuleType("scapy.all")
    for name in ("ARP", "Dot11", "Ether", "ICMP", "IP", "TCP", "UDP"):
        setattr(all_module, name, Layer)
    all_module.RadioTap = Layer
    all_module.Dot11Deauth = Layer
    all_module.ifaces = ["lo", "eth0"]
    all_module.sniff = MagicMock()
    all_module.sendp = MagicMock()
    monkeypatch.setitem(sys.modules, "scapy", package)
    monkeypatch.setitem(sys.modules, "scapy.all", all_module)
    return all_module


def test_sniffer_prints_packets_and_returns_success(monkeypatch, fake_scapy, capsys):
    logger = MagicMock()
    monkeypatch.setattr(sniffer, "get_logger", lambda: logger)
    fake_scapy.sniff.side_effect = lambda **kwargs: kwargs["prn"](Packet())

    status = sniffer.sniffer(["--interface", "eth0"])

    output = capsys.readouterr().out
    assert status == 0
    assert "PROTOCOL" in output
    assert "64 bytes" in output
    fake_scapy.sniff.assert_called_once_with(
        iface="eth0", prn=fake_scapy.sniff.call_args.kwargs["prn"], store=False
    )


def test_sniffer_lists_interfaces_as_result(monkeypatch, fake_scapy, capsys):
    monkeypatch.setattr(sniffer, "get_logger", lambda: MagicMock())

    assert sniffer.sniffer(["--showinterfaces"]) == 0
    output = capsys.readouterr().out
    assert "0: lo" in output
    assert "1: eth0" in output


def test_sniffer_permission_failure_returns_error(monkeypatch, fake_scapy):
    logger = MagicMock()
    monkeypatch.setattr(sniffer, "get_logger", lambda: logger)
    fake_scapy.sniff.side_effect = PermissionError

    assert sniffer.sniffer(["-i", "eth0"]) == 1
    logger.error.assert_called_once()


def test_sniffer_interrupt_returns_shell_interrupt_status(monkeypatch, fake_scapy):
    logger = MagicMock()
    monkeypatch.setattr(sniffer, "get_logger", lambda: logger)
    fake_scapy.sniff.side_effect = KeyboardInterrupt

    assert sniffer.sniffer(["-i", "eth0"]) == 130
    logger.warning.assert_called_once()


def test_wifi_transmission_uses_quiet_scapy_output(monkeypatch, fake_scapy, capsys):
    logger = MagicMock()
    monkeypatch.setattr(wifi_attack, "get_logger", lambda: logger)

    status = wifi_attack.wifi_attack(
        [
            "--interface",
            "wlan0",
            "--ap",
            "aa:bb:cc:dd:ee:ff",
            "--client",
            "11:22:33:44:55:66",
            "--count",
            "3",
        ]
    )

    assert status == 0
    assert capsys.readouterr().out == ""
    assert fake_scapy.sendp.call_args.kwargs == {
        "iface": "wlan0",
        "inter": 0.1,
        "verbose": False,
        "count": 3,
    }


def test_wifi_rejects_invalid_mac_before_loading_scapy(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(wifi_attack, "get_logger", lambda: logger)

    with pytest.raises(SystemExit) as error:
        wifi_attack.wifi_attack(["-i", "wlan0", "-a", "bad", "-c", "11:22:33:44:55:66"])

    assert error.value.code == 2


def test_wifi_zero_count_uses_loop_and_interrupt_returns_130(monkeypatch, fake_scapy):
    monkeypatch.setattr(wifi_attack, "get_logger", lambda: MagicMock())
    fake_scapy.sendp.side_effect = KeyboardInterrupt

    status = wifi_attack.wifi_attack(
        ["-i", "wlan0", "-a", "aabbccddeeff", "-c", "112233445566", "-n", "0"]
    )

    assert status == 130
    assert fake_scapy.sendp.call_args.kwargs["loop"] == 1
