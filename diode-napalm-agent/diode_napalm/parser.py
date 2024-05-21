#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Parse Diode Agent Config file."""

import yaml
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError


class ParseException(Exception):
    """Custom exception for parsing errors."""
    pass


class Napalm(BaseModel):
    """Model for NAPALM configuration."""
    driver: str
    hostname: str
    username: str
    password: str
    timeout: int = 60
    optional_args: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional arguments")


class DiscoveryConfig(BaseModel):
    """Model for discovery configuration."""
    netbox: Dict[str, str]


class Policy(BaseModel):
    """Model for a policy configuration."""
    config: DiscoveryConfig
    data: List[Napalm]


class DiodeConfig(BaseModel):
    """Model for Diode configuration."""
    target: str
    api_key: str
    tls_verify: bool


class Diode(BaseModel):
    """Model for Diode containing configuration and policies."""
    config: DiodeConfig
    policies: Dict[str, Policy]


class Config(BaseModel):
    """Top-level model for the entire configuration."""
    diode: Diode


def parse_config(config_data: str):
    """
    Parse the YAML configuration data into a Config object.

    Args:
        config_data (str): The YAML configuration data as a string.

    Returns:
        Config: The parsed configuration object.

    Raises:
        ParseException: If there is an error in parsing the YAML or validating the data.
    """
    try:
        config = Config(**yaml.safe_load(config_data))
        return config
    except yaml.YAMLError as e:
        raise ParseException(f"YAML ERROR: {e}")
    except ValidationError as e:
        raise ParseException("Validation ERROR:", e)
