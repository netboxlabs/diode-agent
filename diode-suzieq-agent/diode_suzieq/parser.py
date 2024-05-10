from pydantic import ValidationError
import yaml
from pydantic import BaseModel
from typing import Any, Dict


class ParseException(Exception):
    pass


class InventoryData(BaseModel):
    inventory: Dict[str, Any]


class DiscoveryConfig(BaseModel):
    netbox: Dict[str, str]


class Policy(BaseModel):
    config: DiscoveryConfig
    data: InventoryData


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
