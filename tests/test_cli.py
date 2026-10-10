"""Tests for direct ZeroSpecter CLI dispatch."""

import contextlib
import io
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from zer0specter import cli


class RecordingLogger:
    def __init__(self):
        self.records = []

    def info(self, message, *args):
        self.records.append(("info", message % args if args else message))

    def warning(self, message, *args):
        self.records.append(("warning", message % args if args else message))

    def error(self, message, *args):
        self.records.append(("error", message % args if args else message))


class TestCli(unittest.TestCase):
    def invoke(self, args, logger=None, loader=None):
        logger = logger or RecordingLogger()
        loader = loader or cli._load_feature
        with (
            patch.object(sys, "argv", ["zer0specter", *args]),
            patch.object(cli, "get_logger", return_value=logger),
            patch.object(cli, "_load_feature", side_effect=loader),
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = cli.main()
        return code, stdout.getvalue(), stderr.getvalue(), logger

    def test_no_arguments_and_top_level_help_print_usage(self):
        for args in ([], ["--help"], ["-h"]):
            with self.subTest(args=args):
                code, output, _, _ = self.invoke(args)
                self.assertEqual(code, 0)
                self.assertIn("packet-sniffer", output)
                self.assertIn("sniffer", output)
                self.assertIn("tui", output)
                self.assertNotIn("gui", output)

    def test_tui_command_launches_interface_and_returns_its_status(self):
        with patch.object(cli, "_launch_tui", return_value=0) as launch_tui:
            code, _, _, _ = self.invoke(["tui"])

        self.assertEqual(code, 0)
        launch_tui.assert_called_once_with()

    def test_tui_help_does_not_launch_interface(self):
        with patch.object(cli, "_launch_tui") as launch_tui:
            code, output, _, _ = self.invoke(["tui", "--help"])

        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "Usage: zer0specter tui")
        launch_tui.assert_not_called()

    def test_commands_and_aliases_preserve_argument_tokens(self):
        command_names = {
            "packet-sniffer": "packet-sniffer",
            "sniffer": "packet-sniffer",
            "port-scanner": "port-scanner",
            "ports": "port-scanner",
            "ip-geolocation": "ip-geolocation",
            "geo": "ip-geolocation",
            "password-generator": "password-generator",
            "pass": "password-generator",
            "zip-cracker": "zip-cracker",
            "zip": "zip-cracker",
            "wifi-deauth": "wifi-deauth",
            "deauth": "wifi-deauth",
        }
        for command, canonical in command_names.items():
            with self.subTest(command=command):
                received = []
                code, _, _, logger = self.invoke(
                    [command, "--prefix", "two words", "--count", "2"],
                    loader=lambda loaded: received.append(loaded)
                    or (lambda args: received.append(args)),
                )

                self.assertEqual(code, 0)
                self.assertEqual(
                    received,
                    [canonical, ["--prefix", "two words", "--count", "2"]],
                )
                self.assertTrue(
                    any(canonical in message for _, message in logger.records)
                )

    def test_unknown_command_returns_usage_error(self):
        code, _, error, logger = self.invoke(["unknown"])

        self.assertEqual(code, 2)
        self.assertIn("Unknown command", error)
        self.assertTrue(any(level == "warning" for level, _ in logger.records))

    def test_gui_is_not_an_active_command(self):
        code, _, error, _ = self.invoke(["gui"])

        self.assertEqual(code, 2)
        self.assertIn("Unknown command", error)
        self.assertNotIn("zer0specter.gui.app", sys.modules)

    def test_module_help_is_forwarded(self):
        received = []
        code, _, _, _ = self.invoke(
            ["sniffer", "--help"],
            loader=lambda command: received.append(command)
            or (lambda args: received.append(args)),
        )

        self.assertEqual(code, 0)
        self.assertEqual(received, ["packet-sniffer", ["--help"]])

    def test_feature_map_loads_expected_module_function(self):
        for command, (module_name, function_name, _) in cli.FEATURES.items():
            with self.subTest(command=command):
                function = object()
                module = SimpleNamespace(**{function_name: function})
                with patch.object(
                    cli.importlib, "import_module", return_value=module
                ) as import_module:
                    self.assertIs(cli._load_feature(command), function)
                import_module.assert_called_once_with(module_name)

    def test_module_system_exit_code_is_preserved(self):
        def exit_with_usage_error(_args):
            raise SystemExit(2)

        code, _, _, _ = self.invoke(
            ["sniffer"], loader=lambda _command: exit_with_usage_error
        )

        self.assertEqual(code, 2)

    def test_module_return_status_is_forwarded(self):
        code, _, _, logger = self.invoke(
            ["ports"], loader=lambda _command: lambda _args: 7
        )

        self.assertEqual(code, 7)
        self.assertTrue(
            any("finished with status 7" in message for _, message in logger.records)
        )

    def test_unexpected_exception_returns_error_and_logs_type(self):
        def fail(_args):
            raise RuntimeError("failure")

        code, _, error, logger = self.invoke(["sniffer"], loader=lambda _command: fail)

        self.assertEqual(code, 1)
        self.assertIn("RuntimeError", error)
        self.assertTrue(
            any(
                level == "error" and "RuntimeError" in message
                for level, message in logger.records
            )
        )
        self.assertFalse(any("failure" in message for _, message in logger.records))

    def test_keyboard_interrupt_returns_shell_interrupt_status(self):
        def interrupt(_args):
            raise KeyboardInterrupt

        code, _, error, logger = self.invoke(
            ["sniffer"], loader=lambda _command: interrupt
        )

        self.assertEqual(code, 130)
        self.assertIn("Interrupted by user", error)
        self.assertTrue(any(level == "warning" for level, _ in logger.records))

    def test_cli_import_does_not_load_gui(self):
        self.assertNotIn("zer0specter.gui.app", sys.modules)


if __name__ == "__main__":
    unittest.main()
