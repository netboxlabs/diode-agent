#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Parse Diode Agent Config file."""

from ipaddress import IPv4Network
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError


class ParseException(Exception):
    """Custom exception for parsing errors."""

    pass


class DiscoveryConfig(BaseModel):
    """Model for discovery configuration."""

    netbox: dict[str, str]


class Policy(BaseModel):
    """Model for a policy configuration."""

    config: DiscoveryConfig
    interface: str | None = Field(default=None, description="interface name, optional")
    network: IPv4Network | None = Field(
        default=None, description="network range, optional"
    )


class DiodeConfig(BaseModel):
    """Model for Diode configuration."""

    target: str
    api_key: str


class Diode(BaseModel):
    """Model for Diode containing configuration and policies."""

    config: DiodeConfig
    policies: dict[str, Policy]


class Config(BaseModel):
    """Top-level model for the entire configuration."""

    diode: Diode


def resolve_env_vars(config):
    """
    Recursively resolve environment variables in the configuration.

    Args:
    ----
        config (dict): The configuration dictionary.

    Returns:
    -------
        dict: The configuration dictionary with environment variables resolved.

    """
    if isinstance(config, dict):
        return {k: resolve_env_vars(v) for k, v in config.items()}
    if isinstance(config, list):
        return [resolve_env_vars(i) for i in config]
    if isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        env_var = config[2:-1]
        return os.getenv(env_var, config)
    return config


def parse_config(config_data: str):
    """
    Parse the YAML configuration data into a Config object.

    Args:
    ----
        config_data (str): The YAML configuration data as a string.

    Returns:
    -------
        Config: The parsed configuration object.

    Raises:
    ------
        ParseException: If there is an error in parsing the YAML or validating the data.

    """
    try:
        # Parse the YAML configuration data
        config_dict = yaml.safe_load(config_data)
        # Resolve environment variables
        resolved_config = resolve_env_vars(config_dict)
        # Parse the data into the Config model
        config = Config(**resolved_config)
        return config
    except yaml.YAMLError as e:
        raise ParseException(f"YAML ERROR: {e}")
    except ValidationError as e:
        raise ParseException("Validation ERROR:", e)


def parse_config_file(file_path: Path) -> Diode:
    """
    Parse the Diode configuration file and return the Diode configuration object.

    This function reads the content of the specified YAML configuration file,
    parses it into a `Config` object, and returns the `Diode` part of the configuration.

    Args:
    ----
        file_path (Path): The path to the YAML configuration file.

    Returns:
    -------
        Diode: The `Diode` configuration object extracted from the parsed configuration.

    Raises:
    ------
        ParseException: If there is an error parsing the YAML content or validating the data.
        Exception: If there is an error opening the file or any other unexpected error.

    """
    try:
        with open(file_path) as f:
            cfg = parse_config(f.read())
    except ParseException:
        raise
    except Exception as e:
        raise Exception(f"Unable to open config file {file_path}: {e.args[1]}")
    return cfg.diode
