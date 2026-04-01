"""Tests for port scanner module."""

import pytest
from unittest.mock import patch, MagicMock
from zer0specter.modules.port_scanner import scan_ports, PortScanner


class TestPortScanner:
    """Test cases for PortScanner class."""

    def test_scan_ports_basic(self):
        """Test basic port scanning functionality."""
        # Mock socket operations
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect_ex.return_value = 0  # Port open

            open_ports = scan_ports("127.0.0.1", start_port=80, end_port=80, timeout=1)

            assert 80 in open_ports
            mock_sock_instance.connect_ex.assert_called_with(("127.0.0.1", 80))

    def test_scan_ports_closed(self):
        """Test scanning closed ports."""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect_ex.return_value = 1  # Port closed

            open_ports = scan_ports("127.0.0.1", start_port=80, end_port=80, timeout=1)

            assert 80 not in open_ports

    def test_scan_ports_range(self):
        """Test scanning a range of ports."""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            # Alternate between open and closed ports
            mock_sock_instance.connect_ex.side_effect = [0, 1, 0, 1, 0]

            open_ports = scan_ports("127.0.0.1", start_port=80, end_port=84, timeout=1)

            expected_open = [80, 82, 84]
            assert open_ports == expected_open

    def test_scan_ports_timeout(self):
        """Test port scanning with timeout."""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect_ex.return_value = 0

            open_ports = scan_ports("127.0.0.1", start_port=80, end_port=80, timeout=5)

            # Verify timeout was set
            mock_sock_instance.settimeout.assert_called_with(5)

    @pytest.mark.parametrize("invalid_ip", [
        "256.1.1.1",
        "192.168.1.256",
        "invalid.ip.address",
        "",
    ])
    def test_invalid_ip_addresses(self, invalid_ip):
        """Test handling of invalid IP addresses."""
        with pytest.raises(ValueError):
            scan_ports(invalid_ip, start_port=80, end_port=80)

    def test_port_range_validation(self):
        """Test port range validation."""
        # Valid ranges
        scan_ports("127.0.0.1", start_port=1, end_port=100)  # Should not raise

        # Invalid ranges
        with pytest.raises(ValueError):
            scan_ports("127.0.0.1", start_port=0, end_port=100)  # Start port too low

        with pytest.raises(ValueError):
            scan_ports("127.0.0.1", start_port=100, end_port=80)  # Start > end

        with pytest.raises(ValueError):
            scan_ports("127.0.0.1", start_port=80, end_port=70000)  # End port too high
