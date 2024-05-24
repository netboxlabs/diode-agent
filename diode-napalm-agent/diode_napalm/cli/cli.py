#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode NAPALM Agent CLI."""

import argparse
import asyncio
import logging
import sys
from importlib.metadata import version
from pathlib import Path

from napalm import get_network_driver
from diode_napalm.client import Client
from diode_napalm.parser import parse_config_file
from diode_napalm.version import version_semver
import netboxlabs.diode.sdk.version as SdkVersion

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_policy(cfg, client):
    """
    Start the policy for the given configuration and client.

    Args:
        cfg: Configuration data for the policy.
        client: Client instance for data ingestion.
    """
    for info in cfg.data:
        logger.info(f"Get driver '{info.driver}'")
        np_driver = get_network_driver(info.driver)
        logger.info(f"Getting information from '{info.hostname}'")
        with np_driver(info.hostname, info.username, info.password, info.timeout, info.optional_args) as device:
            data = {
                "driver": info.driver,
                "site": cfg.config.netbox.get("site", None),
                "device": device.get_facts(),
                "interface": device.get_interfaces(),
                "interface_ip": device.get_interfaces_ip(),
                "vlan": device.get_vlans()
            }
            client.ingest(data)


async def start_agent(cfg):
    """
    Start the diode client and execute policies.

    Args:
        cfg: Configuration data containing policies.
    """
    client = Client()
    client.init_client(target=cfg.config.target,
                       api_key=cfg.config.api_key, tls_verify=cfg.config.tls_verify)
    for policy_name in cfg.policies:
        try:
            await start_policy(cfg.policies.get(policy_name), client)
        except Exception as e:
            raise Exception(f"Unable to start policy {policy_name}: {e}")


def main():
    """
    Main entry point for the Diode NAPALM Agent CLI.
    Parses command-line arguments and starts the agent.
    """
    parser = argparse.ArgumentParser(description="Diode Agent for NAPALM")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"Diode Agent version: {version_semver()}, NAPALM version: {version('napalm')}, Diode SDK version: {SdkVersion.version_semver()}",
        help="Display Diode Agent, NAPALM and Diode SDK versions"
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="config.yaml",
        help="Agent yaml configuration file",
        type=str, required=True
    )
    args = parser.parse_args()

    try:
        config = parse_config_file(Path(args.config))
        asyncio.run(start_agent(config))
    except (KeyboardInterrupt, RuntimeError):
        pass
    except Exception as e:
        sys.exit(f"ERROR: Unable to start agent: {e}")


if __name__ == '__main__':
    main()
