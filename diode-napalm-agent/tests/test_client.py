#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""NetBox Labs - Client Unit Tests."""

from unittest.mock import MagicMock, patch

import pytest

from diode_napalm.client import Client
from diode_napalm.translate import translate_data


@pytest.fixture
def sample_data():
    """Sample data for testing ingestion."""
    return {
        "device": {
            "hostname": "router1",
            "model": "ISR4451",
            "vendor": "Cisco",
            "serial_number": "123456789",
            "site": "New York",
            "driver": "ios",
        },
        "interface": {
            "GigabitEthernet0/0": {
                "is_enabled": True,
                "mtu": 1500,
                "mac_address": "00:1C:58:29:4A:71",
                "speed": 1000,
                "description": "Uplink Interface",
            }
        },
        "interface_ip": {
            "GigabitEthernet0/0": {"ipv4": {"192.0.2.1": {"prefix_length": 24}}}
        },
        "driver": "ios",
        "site": "New York",
    }


@patch("diode_napalm.client.version_semver", return_value="0.0.0")
@patch("diode_napalm.client.DiodeClient")
def test_init_client(mock_diode_client_class, mock_version):
    """Test the initialization of the Diode client."""
    client = Client()
    client.init_client(target="https://example.com", api_key="dummy_api_key")

    mock_diode_client_class.assert_called_once_with(
        target="https://example.com",
        app_name="diode-napalm-agent",
        app_version=mock_version(),
        api_key="dummy_api_key",
    )


@patch("diode_napalm.client.DiodeClient")
def test_ingest_success(mock_diode_client_class, sample_data):
    """Test successful data ingestion."""
    client = Client()
    client.init_client(target="https://example.com", api_key="dummy_api_key")

    mock_diode_instance = mock_diode_client_class.return_value
    mock_diode_instance.ingest.return_value.errors = []

    with patch(
        "diode_napalm.client.translate_data", return_value=translate_data(sample_data)
    ) as mock_translate_data:
        client.ingest(sample_data)
        mock_translate_data.assert_called_once_with(sample_data)
        mock_diode_instance.ingest.assert_called_once()


@patch("diode_napalm.client.DiodeClient")
def test_ingest_failure(mock_diode_client_class, sample_data):
    """Test data ingestion with errors."""
    client = Client()
    client.init_client(target="https://example.com", api_key="dummy_api_key")

    mock_diode_instance = mock_diode_client_class.return_value
    mock_diode_instance.ingest.return_value.errors = ["Error1", "Error2"]

    with patch(
        "diode_napalm.client.translate_data", return_value=translate_data(sample_data)
    ) as mock_translate_data:
        client.ingest(sample_data)
        mock_translate_data.assert_called_once_with(sample_data)
        mock_diode_instance.ingest.assert_called_once()

    assert len(mock_diode_instance.ingest.return_value.errors) > 0


def test_ingest_without_initialization():
    """Test ingestion without client initialization raises ValueError."""
    Client._instance = None  # Reset the Client singleton instance
    client = Client()
    with pytest.raises(ValueError, match="Diode client not initialized"):
        client.ingest({})
