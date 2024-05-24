#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""NetBox Labs - Tests."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from diode_napalm.parser import parse_config, parse_config_file, ParseException, resolve_env_vars, Config


@pytest.fixture
def valid_yaml():
    return """
    diode:
      config:
        target: "target_value"
        api_key: "api_key_value"
        tls_verify: true
      policies:
        policy1:
          config:
            netbox:
              site: "New York"
          data:
            - driver: "ios"
              hostname: "router1"
              username: "admin"
              password: "password"
    """


@pytest.fixture
def invalid_yaml():
    return """
    diode:
      config:
        target: "target_value"
        api_key: "api_key_value"
        tls_verify: true
      policies:
        policy1:
          config:
            netbox:
              site: "New York"
          data:
            - driver: "ios"
              hostname: "router1"
              username: "admin"
              # Missing password field
    """


def test_parse_valid_config(valid_yaml):
    """Ensure we can parse a valid configuration."""
    config = parse_config(valid_yaml)
    assert isinstance(config, Config)
    assert config.diode.config.target == "target_value"
    assert config.diode.policies["policy1"].data[0].hostname == "router1"


def test_parse_invalid_config(invalid_yaml):
    """Ensure an invalid configuration raises a ParseException."""
    with pytest.raises(ParseException):
        parse_config(invalid_yaml)


@patch("builtins.open", new_callable=mock_open, read_data="valid_yaml")
def test_parse_config_file(mock_file, valid_yaml):
    """Ensure we can parse a configuration file."""
    with patch("diode_napalm.parser.parse_config", return_value=parse_config(valid_yaml)):
        config = parse_config_file(Path("fake_path.yaml"))
        assert config.config.target == "target_value"
        mock_file.assert_called_once_with(Path("fake_path.yaml"), "r")


@patch.dict(os.environ, {"API_KEY": "env_api_key"})
def test_resolve_env_vars():
    """Ensure environment variables are resolved correctly."""
    config_with_env_var = {
        "api_key": "${API_KEY}"
    }
    resolved_config = resolve_env_vars(config_with_env_var)
    assert resolved_config["api_key"] == "env_api_key"


def test_resolve_env_vars_no_env():
    """Ensure missing environment variables are handled correctly."""
    config_with_no_env_var = {
        "api_key": "${MISSING_KEY}"
    }
    resolved_config = resolve_env_vars(config_with_no_env_var)
    assert resolved_config["api_key"] == "${MISSING_KEY}"


def test_parse_config_file_exception():
    """Ensure file parsing errors are handled correctly."""
    with pytest.raises(Exception):
        parse_config_file(Path("non_existent_file.yaml"))
