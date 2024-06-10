#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""NetBox Labs - CLI Unit Tests."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from diode_napalm.cli.cli import main, run_driver, start_policy
from diode_napalm.parser import DiscoveryConfig, Napalm, Policy


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


@pytest.fixture
def mock_client():
    """
    Fixture to mock the Client class.

    Mocks the Client class to control its behavior during tests.
    """
    with patch("diode_napalm.cli.cli.Client") as mock:
        yield mock


@pytest.fixture
def mock_get_network_driver():
    """
    Fixture to mock the get_network_driver function.

    Mocks the get_network_driver function to control its behavior during tests.
    """
    with patch("diode_napalm.cli.cli.get_network_driver") as mock:
        yield mock


@pytest.fixture
def mock_discover_device_driver():
    """
    Fixture to mock the discover_device_driver function.

    Mocks the discover_device_driver function to control its behavior during tests.
    """
    with patch("diode_napalm.cli.cli.discover_device_driver") as mock:
        yield mock


@pytest.fixture
def mock_thread_pool_executor():
    """
    Fixture to mock the ThreadPoolExecutor class.

    Mocks the ThreadPoolExecutor class to control its behavior during tests.
    """
    with patch("diode_napalm.cli.cli.ThreadPoolExecutor") as mock:
        yield mock


@pytest.fixture
def mock_run_driver():
    """
    Fixture to mock the run_driver function.

    Mocks the run_driver function to control its behavior during tests.
    """
    with patch("diode_napalm.cli.cli.run_driver") as mock:
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


def test_run_driver_no_driver(
    mock_client, mock_get_network_driver, mock_discover_device_driver
):
    """
    Test run_driver function when driver is not provided.

    Args:
    ----
        mock_client: Mocked Client class.
        mock_get_network_driver: Mocked get_network_driver function.
        mock_discover_device_driver: Mocked discover_device_driver function.

    """
    info = Napalm(
        driver=None,
        hostname="test_host",
        username="user",
        password="pass",
        timeout=10,
        optional_args={},
    )
    config = DiscoveryConfig(netbox={"site": "test_site"})

    mock_discover_device_driver.return_value = "test_driver"
    mock_np_driver = MagicMock()
    mock_get_network_driver.return_value = mock_np_driver

    run_driver(info, config)

    mock_discover_device_driver.assert_called_once_with(info)
    mock_get_network_driver.assert_called_once_with("test_driver")
    mock_np_driver.assert_called_once_with("test_host", "user", "pass", 10, {})
    mock_client().ingest.assert_called_once()


def test_run_driver_with_driver(
    mock_client, mock_get_network_driver, mock_discover_device_driver
):
    """
    Test run_driver function when driver is already provided.

    Args:
    ----
        mock_client: Mocked Client class.
        mock_get_network_driver: Mocked get_network_driver function.
        mock_discover_device_driver: Mocked discover_device_driver function.

    """
    info = Napalm(
        driver="existing_driver",
        hostname="test_host",
        username="user",
        password="pass",
        timeout=10,
        optional_args={},
    )
    config = DiscoveryConfig(netbox={"site": "test_site"})

    mock_np_driver = MagicMock()
    mock_get_network_driver.return_value = mock_np_driver

    run_driver(info, config)

    mock_discover_device_driver.assert_not_called()
    mock_get_network_driver.assert_called_once_with("existing_driver")
    mock_np_driver.assert_called_once_with("test_host", "user", "pass", 10, {})
    mock_client().ingest.assert_called_once()


def test_start_policy(mock_client, mock_run_driver, mock_thread_pool_executor):
    """
    Test start_policy function with different configurations.

    Args:
    ----
        mock_client: Mocked Client class.
        mock_run_driver: Mocked run_driver function.
        mock_thread_pool_executor: Mocked ThreadPoolExecutor class.

    """
    cfg = Policy(
        config=DiscoveryConfig(netbox={"site": "test_site"}),
        data=[
            Napalm(
                driver="driver",
                hostname="host",
                username="user",
                password="pass",
                timeout=10,
                optional_args={},
            )
        ],
    )
    max_workers = 2

    mock_future = MagicMock()
    mock_future.result.return_value = None
    mock_executor = MagicMock()
    mock_executor.submit.return_value = mock_future
    mock_thread_pool_executor.return_value = mock_executor

    with patch("diode_napalm.cli.cli.as_completed", return_value=[mock_future]):
        start_policy(cfg, max_workers)

        mock_thread_pool_executor.assert_called_once_with(max_workers=2)
