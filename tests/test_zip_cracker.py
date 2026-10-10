"""Behavioral tests for the ZIP cracker command handler."""

import zipfile
from unittest.mock import MagicMock

import pyzipper
import pytest

from zer0specter.modules import zip_cracker


class InlinePool:
    """Run pool work synchronously so tests never spawn worker processes."""

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def imap_unordered(self, function, iterable, chunksize):
        for item in iterable:
            yield function(item)

    def terminate(self):
        pass


@pytest.fixture(autouse=True)
def inline_pool(monkeypatch):
    monkeypatch.setattr(zip_cracker, "Pool", lambda _workers: InlinePool())
    monkeypatch.setattr(zip_cracker, "cpu_count", lambda: 1)
    monkeypatch.setattr(zip_cracker, "get_logger", lambda: MagicMock())


def make_encrypted_zip(path, password, member_name="payload.txt"):
    with pyzipper.AESZipFile(
        path,
        "w",
        compression=pyzipper.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES,
    ) as archive:
        archive.setpassword(password.encode())
        archive.writestr(member_name, b"zip payload")
    return path


def make_plain_zip(path):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("payload.txt", b"plain payload")
    return path


def test_found_password_is_printed_and_extracted_once_to_requested_directory(
    tmp_path, monkeypatch, capsys
):
    archive = make_encrypted_zip(tmp_path / "locked.zip", "secret")
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("wrong\nsecret\n")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    logger = MagicMock()
    monkeypatch.setattr(zip_cracker, "get_logger", lambda: logger)

    status = zip_cracker.zipcrack(
        [
            "--path",
            str(archive),
            "--wordlist",
            str(wordlist),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert status == 0
    assert capsys.readouterr().out == "secret\n"
    assert (output_dir / "payload.txt").read_bytes() == b"zip payload"
    assert "secret" not in repr(logger.mock_calls)


def test_failed_search_does_not_extract_files(tmp_path, capsys):
    archive = make_encrypted_zip(tmp_path / "locked.zip", "secret")
    wordlist = tmp_path / "wrong.txt"
    wordlist.write_text("wrong\n")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    status = zip_cracker.zipcrack(
        [
            "--path",
            str(archive),
            "--wordlist",
            str(wordlist),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert status == 0
    assert capsys.readouterr().out == ""
    assert list(output_dir.iterdir()) == []


def test_default_extraction_directory_is_current_working_directory(
    tmp_path, monkeypatch, capsys
):
    archive = make_encrypted_zip(tmp_path / "locked.zip", "secret")
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("secret\n")
    monkeypatch.chdir(tmp_path)

    status = zip_cracker.zipcrack(["--path", str(archive), "--wordlist", str(wordlist)])

    assert status == 0
    assert (tmp_path / "payload.txt").read_bytes() == b"zip payload"
    assert capsys.readouterr().out == "secret\n"


def test_unsafe_member_path_is_rejected_without_writing_outside_destination(
    tmp_path, capsys
):
    archive = make_encrypted_zip(
        tmp_path / "unsafe.zip", "secret", member_name="../escaped.txt"
    )
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("secret\n")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    status = zip_cracker.zipcrack(
        [
            "--path",
            str(archive),
            "--wordlist",
            str(wordlist),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert status == 1
    assert not (tmp_path / "escaped.txt").exists()
    assert list(output_dir.iterdir()) == []
    assert "secret" not in capsys.readouterr().err


def test_missing_input_file_returns_usage_error(tmp_path):
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("secret\n")

    assert (
        zip_cracker.zipcrack(
            ["--path", str(tmp_path / "missing.zip"), "--wordlist", str(wordlist)]
        )
        == 2
    )


def test_unprotected_archive_does_not_match_a_candidate(tmp_path, capsys):
    archive = make_plain_zip(tmp_path / "plain.zip")
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("candidate\n")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    status = zip_cracker.zipcrack(
        [
            "--path",
            str(archive),
            "--wordlist",
            str(wordlist),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert status == 0
    assert capsys.readouterr().out == ""
    assert list(output_dir.iterdir()) == []


def test_existing_output_file_is_not_overwritten(tmp_path, capsys):
    archive = make_encrypted_zip(tmp_path / "locked.zip", "secret")
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("secret\n")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    existing = output_dir / "payload.txt"
    existing.write_bytes(b"keep me")

    status = zip_cracker.zipcrack(
        [
            "--path",
            str(archive),
            "--wordlist",
            str(wordlist),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert status == 1
    assert existing.read_bytes() == b"keep me"
    assert capsys.readouterr().out == ""


def test_nonexistent_output_directory_is_usage_error(tmp_path):
    archive = make_encrypted_zip(tmp_path / "locked.zip", "secret")
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("secret\n")

    assert (
        zip_cracker.zipcrack(
            [
                "--path",
                str(archive),
                "--wordlist",
                str(wordlist),
                "--output-dir",
                str(tmp_path / "missing-output"),
            ]
        )
        == 2
    )


def test_bruteforce_requires_a_charset_and_length(tmp_path):
    archive = make_encrypted_zip(tmp_path / "locked.zip", "a")

    with pytest.raises(SystemExit) as error:
        zip_cracker.zipcrack(["--path", str(archive), "--letters", "y"])

    assert error.value.code == 2
