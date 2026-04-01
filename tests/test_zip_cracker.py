"""Tests for ZIP cracker module."""

import pytest
import zipfile
import tempfile
import os
from zer0specter.modules.zip_cracker import crack_zip


class TestZipCracker:
    """Test cases for ZIP cracker functionality."""

    def create_test_zip(self, tmp_path, password=None):
        """Create a test ZIP file with optional password."""
        zip_path = tmp_path / "test.zip"
        test_content = b"Hello, World! This is test content."

        if password:
            # Create password-protected ZIP
            import pyzipper
            with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED,
                                   encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(password.encode())
                zf.writestr("test.txt", test_content)
        else:
            # Create regular ZIP
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("test.txt", test_content)

        return str(zip_path)

    def test_crack_zip_success(self, tmp_path, sample_wordlist):
        """Test successful ZIP cracking."""
        password = "password"
        zip_path = self.create_test_zip(tmp_path, password)

        success, found_password = crack_zip(zip_path, sample_wordlist)

        assert success is True
        assert found_password == password

    def test_crack_zip_failure(self, tmp_path):
        """Test ZIP cracking failure with wrong wordlist."""
        password = "password"
        zip_path = self.create_test_zip(tmp_path, password)

        # Create wordlist without the correct password
        wrong_wordlist = tmp_path / "wrong.txt"
        wrong_wordlist.write_text("wrong1\nwrong2\nwrong3\n")

        success, found_password = crack_zip(zip_path, str(wrong_wordlist))

        assert success is False
        assert found_password is None

    def test_crack_unprotected_zip(self, tmp_path, sample_wordlist):
        """Test cracking unprotected ZIP (should fail gracefully)."""
        zip_path = self.create_test_zip(tmp_path, password=None)

        success, found_password = crack_zip(zip_path, sample_wordlist)

        # Should return False since it's not password protected
        assert success is False
        assert found_password is None

    def test_invalid_zip_file(self, sample_wordlist):
        """Test handling of invalid ZIP files."""
        success, found_password = crack_zip("/nonexistent/file.zip", sample_wordlist)

        assert success is False
        assert found_password is None

    def test_invalid_wordlist(self, tmp_path):
        """Test handling of invalid wordlist files."""
        password = "password"
        zip_path = self.create_test_zip(tmp_path, password)

        success, found_password = crack_zip(zip_path, "/nonexistent/wordlist.txt")

        assert success is False
        assert found_password is None

    def test_empty_wordlist(self, tmp_path):
        """Test handling of empty wordlist."""
        password = "password"
        zip_path = self.create_test_zip(tmp_path, password)

        empty_wordlist = tmp_path / "empty.txt"
        empty_wordlist.write_text("")

        success, found_password = crack_zip(zip_path, str(empty_wordlist))

        assert success is False
        assert found_password is None
