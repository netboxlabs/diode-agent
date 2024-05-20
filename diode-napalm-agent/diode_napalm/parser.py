#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Parse Diode Agent Config file"""

import yaml
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError


class ParseException(Exception):
    pass


class Napalm(BaseModel):
    driver: str
    hostname: str
    username: str
    password: str
    timeout: int = 60
    optional_args: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional arguments")


class DiscoveryConfig(BaseModel):
    netbox: Dict[str, str]


class Policy(BaseModel):
    config: DiscoveryConfig
    data: List[Napalm]


class DiodeConfig(BaseModel):
    target: str
    api_key: str
    tls_verify: bool


class Diode(BaseModel):
    config: DiodeConfig
    policies: Dict[str, Policy]


class Config(BaseModel):
    diode: Diode


def parse_config(config_data: str):
    try:
        config = Config(**yaml.safe_load(config_data))
        return config
    except yaml.YAMLError as e:
        raise ParseException(f"YAML ERROR: {e}")
    except ValidationError as e:
        raise ParseException("Validation ERROR:", e)
