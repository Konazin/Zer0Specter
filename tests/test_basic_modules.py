"""Behavioral tests for geolocation and password generation."""

from unittest.mock import MagicMock

import pytest

from zer0specter.modules import ip_geo, passwd_gen


@pytest.fixture(autouse=True)
def quiet_loggers(monkeypatch):
    monkeypatch.setattr(ip_geo, "get_logger", lambda: MagicMock(), raising=False)


def test_geolocation_prints_result_and_uses_a_finite_timeout(monkeypatch, capsys):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "success": True,
        "ip": "8.8.8.8",
        "country": "United States",
        "region": "California",
        "city": "Mountain View",
        "type": "IPv4",
        "latitude": 37.386,
        "longitude": -122.084,
        "connection": {"isp": "Example ISP"},
    }
    request = MagicMock(return_value=response)
    monkeypatch.setattr(ip_geo.requests, "get", request)

    status = ip_geo.ip_locator(["-ip", "8.8.8.8"])

    output = capsys.readouterr().out
    assert status == 0
    assert "IP: 8.8.8.8" in output
    assert output.count("Connection Type:") == 1
    assert "isp: Example ISP" in output
    request.assert_called_once_with("https://ipwho.is/8.8.8.8", timeout=10)


def test_invalid_geolocation_ip_is_rejected_before_network_call(monkeypatch):
    request = MagicMock()
    monkeypatch.setattr(ip_geo.requests, "get", request)

    with pytest.raises(SystemExit) as error:
        ip_geo.ip_locator(["-ip", "not-an-ip"])

    assert error.value.code == 2
    request.assert_not_called()


def test_geolocation_api_failure_returns_runtime_error(monkeypatch):
    response = MagicMock(status_code=503)
    monkeypatch.setattr(ip_geo.requests, "get", lambda *args, **kwargs: response)
    logger = MagicMock()
    monkeypatch.setattr(ip_geo, "get_logger", lambda: logger)

    assert ip_geo.ip_locator(["-ip", "8.8.8.8"]) == 1
    logger.error.assert_called_once()


def test_geolocation_network_failure_returns_runtime_error(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(ip_geo, "get_logger", lambda: logger)
    monkeypatch.setattr(
        ip_geo.requests,
        "get",
        MagicMock(side_effect=ip_geo.requests.Timeout),
    )

    assert ip_geo.ip_locator([]) == 1
    logger.error.assert_called_once()


def test_password_generator_uses_secure_choice_and_preserves_prefix(
    monkeypatch, capsys
):
    choices = iter("a1B!")
    monkeypatch.setattr(passwd_gen.secrets, "choice", lambda _chars: next(choices))

    status = passwd_gen.password_generator(
        [
            "--prefix",
            "site-",
            "--numberchar",
            "4",
            "--numbers",
            "y",
            "--uppercase",
            "y",
            "--punctuation",
            "y",
        ]
    )

    assert status == 0
    assert capsys.readouterr().out == "site-a1B!\n"


@pytest.mark.parametrize(
    "args",
    [
        ["--numberchar", "0"],
        ["--numberchar", "4", "--numbers", "maybe"],
    ],
)
def test_password_generator_rejects_invalid_values(args):
    with pytest.raises(SystemExit) as error:
        passwd_gen.password_generator(args)

    assert error.value.code == 2
