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
    with patch("diode_napalm.cli.cli.argparse.ArgumentParser.parse_args") as mock:
        yield mock


@pytest.fixture
def mock_load_dotenv():
    """
    Fixture to mock the load_dotenv function from dotenv.

    Mocks the load_dotenv method to simulate loading environment variables.
    """
    with patch("diode_napalm.cli.cli.load_dotenv") as mock:
        yield mock


@pytest.fixture
def mock_parse_config_file():
    """
    Fixture to mock the parse_config_file function.

    Mocks the parse_config_file method to simulate loading a configuration file.
    """
    with patch("diode_napalm.cli.cli.parse_config_file") as mock:
        yield mock


@pytest.fixture
def mock_start_agent():
    """
    Fixture to mock the start_agent function.

    Mocks the start_agent method to control its behavior during tests.
    """
    with patch("diode_napalm.cli.cli.start_agent") as mock:
        yield mock


def test_main_keyboard_interrupt(mock_parse_args, mock_parse_config_file):
    """
    Test handling of KeyboardInterrupt in main.

    Args:
    ----
        mock_parse_args: Mocked parse_args function.
        mock_parse_config_file: Mocked parse_config_file function.

    """
    mock_parse_args.return_value = MagicMock(config="config.yaml", env=None, workers=2)
    mock_parse_config_file.side_effect = KeyboardInterrupt

    with patch.object(sys, "exit", side_effect=Exception("Test Exit")):
        try:
            main()
        except Exception as e:
            assert str(e) == "Test Exit"


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


def test_main_no_config_file(mock_parse_args):
    """
    Test running the CLI without a configuration file.

    Args:
    ----
        mock_parse_args: Mocked parse_args function.

    """
    mock_parse_args.return_value = MagicMock(config=None, env=None, workers=2)

    with patch.object(sys, "exit", side_effect=Exception("Test Exit")) as mock_exit:
        try:
            main()
        except Exception as e:
            print(f"Caught exception: {str(e)}")  # Debug statement
            assert str(e) == "Test Exit"

    mock_exit.assert_called_once()


def test_main_missing_policy(mock_parse_args, mock_parse_config_file):
    """
    Test handling of missing policy in start_agent.

    Args:
    ----
        mock_parse_args: Mocked parse_args function.
        mock_parse_config_file: Mocked parse_config_file function.

    """
    mock_parse_args.return_value = MagicMock(config="config.yaml", env=None, workers=2)
    mock_cfg = MagicMock()
    mock_cfg.policies = {"policy1": None}  # Simulating a missing policy
    mock_parse_config_file.return_value = mock_cfg

    with patch.object(sys, "exit", side_effect=Exception("Test Exit")):
        try:
            main()
        except Exception as e:
            assert str(e) == "Test Exit"


def test_main_load_dotenv_exception(mock_parse_args):
    """
    Test CLI failure when an exception occurs while loading environment variables.

    Args:
    ----
        mock_parse_args: Mocked parse_args function.

    """
    mock_parse_args.return_value = MagicMock(
        config="config.yaml", env=".env", workers=2
    )

    with patch("dotenv.load_dotenv", side_effect=Exception("Load dotenv error")):
        with patch.object(sys, "exit", side_effect=Exception("Test Exit")) as mock_exit:
            try:
                main()
            except Exception as e:
                assert str(e) == "Test Exit"

    mock_exit.assert_called_once_with(
        "ERROR: : Unable to load environment variables from file .env"
    )
