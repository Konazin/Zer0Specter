"""Tests for console and file logging channels."""

import logging
import sys

from zer0specter.utils.logger import ZeroSpecterLogger


def test_console_logs_use_stderr_and_file_logging_is_preserved(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    manager = ZeroSpecterLogger(name="test-log-channel")
    console = next(
        handler
        for handler in manager.logger.handlers
        if type(handler) is logging.StreamHandler
    )
    file_handler = next(
        handler
        for handler in manager.logger.handlers
        if isinstance(handler, logging.handlers.RotatingFileHandler)
    )

    try:
        manager.info("diagnostic message")
        file_handler.flush()

        output = capsys.readouterr()
        assert output.out == ""
        assert "diagnostic message" in output.err
        assert (
            "diagnostic message" in (tmp_path / "logs" / "zer0specter.log").read_text()
        )
        assert console.stream is sys.stderr
    finally:
        for handler in manager.logger.handlers[:]:
            manager.logger.removeHandler(handler)
            handler.close()
