"""Behavior tests for the interactive terminal interface."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from textual.widgets import Input, ListView, Static

from zer0specter.tui import (
    CATEGORIES,
    CLI_RUNNER,
    TOOL_CATALOG,
    ZeroSpecterTUI,
    build_command,
    build_cli_argv,
    run_cli_process,
)


def test_m3_tools_are_shared_category_entries_and_disabled_until_m3():
    assert "sqlmap" in CATEGORIES["Web"]
    assert "sqlmap" in CATEGORIES["Ofensiva"]
    assert TOOL_CATALOG["sqlmap"]["enabled"] is False
    assert TOOL_CATALOG["zap"]["enabled"] is False


def test_port_scanner_form_builds_existing_cli_arguments():
    command = build_command(
        "port-scanner",
        {
            "target": "192.0.2.10",
            "start": "80",
            "end": "443",
            "delay": "0.25",
            "banner": True,
        },
    )

    assert command == [
        "port-scanner",
        "-t",
        "192.0.2.10",
        "-s",
        "80",
        "-e",
        "443",
        "-d",
        "0.25",
        "--banner",
    ]


def test_sniffer_form_supports_listing_interfaces_without_a_target():
    assert build_command(
        "packet-sniffer", {"interface": "", "show_interfaces": True}
    ) == ["packet-sniffer", "--showinterfaces"]

    with pytest.raises(ValueError, match="interface"):
        build_command("packet-sniffer", {"interface": "", "show_interfaces": False})


def test_ip_geolocation_form_builds_existing_cli_arguments():
    assert build_command("ip-geolocation", {"ip": "192.0.2.10"}) == [
        "ip-geolocation",
        "-ip",
        "192.0.2.10",
    ]


def test_wifi_deauth_form_builds_existing_cli_arguments():
    assert build_command(
        "wifi-deauth",
        {
            "interface": "wlan0mon",
            "ap": "00:11:22:33:44:55",
            "client": "66:77:88:99:aa:bb",
            "count": "10",
            "interval": "0.2",
        },
    ) == [
        "wifi-deauth",
        "-i",
        "wlan0mon",
        "-a",
        "00:11:22:33:44:55",
        "-c",
        "66:77:88:99:aa:bb",
        "-n",
        "10",
        "--interval",
        "0.2",
    ]


def test_zip_cracker_form_builds_existing_cli_arguments():
    assert build_command(
        "zip-cracker",
        {
            "path": "target file.zip",
            "wordlist": "words.txt",
            "size": "8",
            "letters": True,
            "numbers": False,
            "special": True,
            "output_dir": "output dir",
        },
    ) == [
        "zip-cracker",
        "-p",
        "target file.zip",
        "-w",
        "words.txt",
        "-s",
        "8",
        "-l",
        "y",
        "-sc",
        "y",
        "--output-dir",
        "output dir",
    ]


def test_password_form_preserves_spaces_as_one_argument():
    command = build_command(
        "password-generator",
        {
            "prefix": "lab pass",
            "length": "20",
            "punctuation": False,
            "numbers": True,
            "uppercase": True,
        },
    )

    assert command == [
        "password-generator",
        "--prefix",
        "lab pass",
        "--numberchar",
        "20",
        "--numbers",
        "y",
        "--uppercase",
        "y",
    ]


def test_planned_tools_cannot_build_an_executable_command():
    try:
        build_command("sqlmap", {})
    except ValueError as error:
        assert "M3" in str(error)
    else:
        raise AssertionError("planned M3 tools must not be executable in M2")


def test_cli_invocation_uses_python_argv_without_a_shell():
    command = ["password-generator", "--prefix", "lab pass", "--numberchar", "20"]

    argv = build_cli_argv(command, python_executable="/usr/bin/python3")

    assert argv == [
        "/usr/bin/python3",
        "-c",
        CLI_RUNNER,
        "password-generator",
        "--prefix",
        "lab pass",
        "--numberchar",
        "20",
    ]


def test_cli_process_captures_stdout_stderr_and_return_code():
    output = []
    command = [
        sys.executable,
        "-c",
        "import sys; print('visible'); print('problem', file=sys.stderr); sys.exit(7)",
    ]

    return_code = asyncio.run(
        run_cli_process(command, lambda stream, line: output.append((stream, line)))
    )

    assert return_code == 7
    assert ("stdout", "visible") in output
    assert ("stderr", "problem") in output


def test_cli_process_reopens_the_real_dispatcher_for_help():
    output = []

    return_code = asyncio.run(
        run_cli_process(
            build_cli_argv(["--help"]),
            lambda stream, line: output.append(line),
        )
    )

    assert return_code == 0
    assert any("Usage: zer0specter" in line for line in output)
    assert any("tui" in line for line in output)


def test_cli_process_can_be_terminated():
    output = []
    processes = []
    command = [
        sys.executable,
        "-c",
        "import time; print('started', flush=True); time.sleep(30)",
    ]

    async def terminate_process():
        task = asyncio.create_task(
            run_cli_process(
                command,
                lambda stream, line: output.append((stream, line)),
                on_process=processes.append,
            )
        )
        while not processes:
            await asyncio.sleep(0.01)
        await asyncio.sleep(0.05)
        processes[0].terminate()
        return await task

    return_code = asyncio.run(terminate_process())

    assert return_code != 0
    assert ("stdout", "started") in output


def test_cli_process_does_not_interpret_arguments_as_shell_code(tmp_path):
    marker = tmp_path / "should-not-exist"
    injected_text = f"; touch {marker}"
    output = []
    command = [
        sys.executable,
        "-c",
        "import sys; print(sys.argv[1])",
        injected_text,
    ]

    return_code = asyncio.run(
        run_cli_process(command, lambda stream, line: output.append(line))
    )

    assert return_code == 0
    assert output == [injected_text]
    assert not Path(marker).exists()


def test_tui_reflows_for_compact_and_wide_terminals():
    async def check_layouts():
        app = ZeroSpecterTUI()
        async with app.run_test(size=(64, 20)) as pilot:
            await pilot.pause()
            workspace = app.query_one("#workspace")
            assert workspace.has_class("compact-layout")
            for width, height, compact in (
                (80, 24, True),
                (120, 40, False),
                (180, 60, False),
            ):
                await pilot.resize_terminal(width, height)
                await pilot.pause()
                assert workspace.has_class("compact-layout") is compact

    asyncio.run(check_layouts())


def test_web_category_shows_m3_tools_as_unavailable():
    async def check_category():
        app = ZeroSpecterTUI()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("down", "enter")
            await pilot.pause()

            assert str(app.query_one("#category-heading").render()) == "Web"
            assert app.query_one("#tool-zap", Static)
            assert app.query_one("#tool-sqlmap", Static)

    asyncio.run(check_category())


def test_tool_search_filters_current_category():
    async def check_search():
        app = ZeroSpecterTUI()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("/")
            await pilot.press("s", "c", "a", "n", "n", "e", "r")
            await pilot.pause()

            assert app.query_one("#tool-port-scanner").display
            assert not app.query_one("#tool-packet-sniffer").display

    asyncio.run(check_search())


def test_tui_form_invokes_cli_and_shows_result():
    async def fake_run(argv, on_output, on_process=None):
        captured_argv.extend(argv)
        on_output("stdout", "scan complete")
        return 0

    captured_argv = []

    async def run_form():
        app = ZeroSpecterTUI()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.click("#tool-port-scanner")
            await pilot.pause()
            app.query_one("#field-target", Input).value = "127.0.0.1"
            await pilot.click("#run-tool")
            await pilot.pause()

            assert "port-scanner" in captured_argv
            assert "127.0.0.1" in captured_argv
            assert str(app.query_one("#run-status", Static).render()) == "Concluído (0)"

    with patch("zer0specter.tui.run_cli_process", side_effect=fake_run):
        asyncio.run(run_form())


def test_tui_displays_nonzero_cli_exit_status():
    async def fake_run(argv, on_output, on_process=None):
        on_output("stderr", "invalid arguments")
        return 2

    async def run_form():
        app = ZeroSpecterTUI()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.click("#tool-port-scanner")
            app.query_one("#field-target", Input).value = "127.0.0.1"
            await pilot.click("#run-tool")
            await pilot.pause()

            assert str(app.query_one("#run-status", Static).render()) == "Falhou (2)"

    with patch("zer0specter.tui.run_cli_process", side_effect=fake_run):
        asyncio.run(run_form())


def test_cancel_button_terminates_active_cli_process():
    class FakeProcess:
        returncode = None

        def terminate(self):
            self.returncode = -15
            cancelled.set()

    cancelled = asyncio.Event()
    process = FakeProcess()

    async def fake_run(argv, on_output, on_process=None):
        on_process(process)
        await cancelled.wait()
        return process.returncode

    async def run_and_cancel():
        app = ZeroSpecterTUI()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.click("#tool-port-scanner")
            app.query_one("#field-target", Input).value = "127.0.0.1"
            run_click = asyncio.create_task(pilot.click("#run-tool"))
            for _ in range(20):
                await pilot.pause(0.02)
                if app._process is process:
                    break
            assert app._process is process
            await pilot.click("#cancel-run")
            await run_click
            await pilot.pause()

            assert process.returncode == -15
            assert str(app.query_one("#run-status", Static).render()) == "Interrompido"

    with patch("zer0specter.tui.run_cli_process", side_effect=fake_run):
        asyncio.run(run_and_cancel())
