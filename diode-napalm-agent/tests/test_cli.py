#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""NetBox Labs - CLI Unit Tests."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from diode_napalm.cli.cli import main


@pytest.fixture
def mock_parse_args():
    """
    Fixture to mock argparse.ArgumentParser.parse_args.

    Mocks the parse_args method to control CLI arguments.
    """
    with patch("diode_napalm.cli.argparse.ArgumentParser.parse_args") as mock:
        yield mock


@pytest.fixture
def mock_load_dotenv():
    """
    Fixture to mock the load_dotenv function from dotenv.

    Mocks the load_dotenv method to simulate loading environment variables.
    """
    with patch("diode_napalm.cli.load_dotenv") as mock:
        yield mock


@pytest.fixture
def mock_parse_config_file():
    """
    Fixture to mock the parse_config_file function.

    Mocks the parse_config_file method to simulate loading a configuration file.
    """
    with patch("diode_napalm.cli.parse_config_file") as mock:
        yield mock


@pytest.fixture
def mock_start_agent():
    """
    Fixture to mock the start_agent function.

    Mocks the start_agent method to control its behavior during tests.
    """
    with patch("diode_napalm.cli.start_agent") as mock:
        yield mock


def test_main_with_config_and_env(
    mock_parse_args, mock_load_dotenv, mock_parse_config_file, mock_start_agent
):
    """Test running the CLI with a configuration file and environment file."""
    mock_parse_args.return_value = MagicMock(
        config="config.yaml", env=".env", workers=2
    )
    mock_load_dotenv.return_value = True
    mock_parse_config_file.return_value = MagicMock()

    with patch.object(sys, "exit", side_effect=Exception("Test Exit")):
        try:
            main()
        except Exception as e:
            assert str(e) == "Test Exit"

    mock_load_dotenv.assert_called_once_with(".env", override=True)
    mock_parse_config_file.assert_called_once_with("config.yaml")
    mock_start_agent.assert_called_once()


def test_main_with_config_no_env(
    mock_parse_args, mock_load_dotenv, mock_parse_config_file, mock_start_agent
):
    """Test running the CLI with a configuration file and no environment file."""
    mock_parse_args.return_value = MagicMock(config="config.yaml", env=None, workers=2)
    mock_parse_config_file.return_value = MagicMock()

    with patch.object(sys, "exit", side_effect=Exception("Test Exit")):
        try:
            main()
        except Exception as e:
            assert str(e) == "Test Exit"

    mock_load_dotenv.assert_not_called()
    mock_parse_config_file.assert_called_once_with("config.yaml")
    mock_start_agent.assert_called_once()


def test_main_load_dotenv_failure(mock_parse_args, mock_load_dotenv):
    """Test CLI failure when loading environment variables fails."""
    mock_parse_args.return_value = MagicMock(
        config="config.yaml", env=".env", workers=2
    )
    mock_load_dotenv.return_value = False

    with patch.object(sys, "exit", side_effect=Exception("Test Exit")) as mock_exit:
        try:
            main()
        except Exception as e:
            assert str(e) == "Test Exit"

    mock_load_dotenv.assert_called_once_with(".env", override=True)
    mock_exit.assert_called_once_with(
        "ERROR: : Unable to load environment variables from file .env"
    )


def test_main_start_agent_failure(
    mock_parse_args, mock_parse_config_file, mock_start_agent
):
    """Test CLI failure when starting the agent."""
    mock_parse_args.return_value = MagicMock(config="config.yaml", env=None, workers=2)
    mock_parse_config_file.return_value = MagicMock()
    mock_start_agent.side_effect = Exception("Test Start Agent Failure")

    with patch.object(sys, "exit", side_effect=Exception("Test Exit")) as mock_exit:
        try:
            main()
        except Exception as e:
            assert str(e) == "Test Exit"

    mock_parse_config_file.assert_called_once_with("config.yaml")
    mock_start_agent.assert_called_once()
    mock_exit.assert_called_once_with(
        "ERROR: Unable to start agent: Test Start Agent Failure"
    )
