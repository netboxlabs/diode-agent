#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode NAPALM Agent CLI."""

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.metadata import version

import netboxlabs.diode.sdk.version as SdkVersion
from dotenv import load_dotenv
from napalm import get_network_driver

from diode_napalm.client import Client
from diode_napalm.discovery import discover_device_driver
from diode_napalm.parser import parse_config_file, Diode, DiodeConfig, Policy, Napalm
from diode_napalm.version import version_semver

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_driver(info: Napalm, config: DiodeConfig):
    """
    Run the device driver code for a single info item.

    Args:
    ----
        info: Information data for the device.
        config: Configuration data containing site information.

    """
    client = Client()
    if info.driver is None:
        logger.info("Driver not informed, discovering it")
        info.driver = discover_device_driver(info)
        if not info.driver:
            raise Exception("Not able to discover device driver")

    logger.info(f"Get driver '{info.driver}'")
    np_driver = get_network_driver(info.driver)
    logger.info(f"Getting information from '{info.hostname}'")
    with np_driver(
        info.hostname, info.username, info.password, info.timeout, info.optional_args
    ) as device:
        data = {
            "driver": info.driver,
            "site": config.netbox.get("site", None),
            "device": device.get_facts(),
            "interface": device.get_interfaces(),
            "interface_ip": device.get_interfaces_ip(),
            "vlan": device.get_vlans(),
        }
        client.ingest(data)


def start_policy(cfg: Policy, max_workers: int):
    """
    Start the policy for the given configuration.

    Args:
    ----
        cfg: Configuration data for the policy.
        max_workers: Maximum number of threads in the pool.

    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_driver, info, cfg.config) for info in cfg.data]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in processing: {e}")


def start_agent(cfg: Diode, workers: int):
    """
    Start the diode client and execute policies.

    Args:
    ----
        cfg: Configuration data containing policies.
        workers: Number of workers to be used in the thread pool.

    """
    client = Client()
    client.init_client(target=cfg.config.target, api_key=cfg.config.api_key)
    for policy_name in cfg.policies:
        try:
            start_policy(cfg.policies.get(policy_name), workers)
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
        version=f"Diode Agent version: {version_semver()}, NAPALM version: {version('napalm')}, "
        f"Diode SDK version: {SdkVersion.version_semver()}",
        help="Display Diode Agent, NAPALM and Diode SDK versions",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="config.yaml",
        help="Agent yaml configuration file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-e",
        "--env",
        metavar=".env",
        help="File containing environment variables",
        type=str,
    )
    parser.add_argument(
        "-w",
        "--workers",
        metavar="N",
        help="Number of workers to be used",
        type=int,
        default=2,
    )
    args = parser.parse_args()

    if hasattr(args, "env") and args.env is not None:
        if not load_dotenv(args.env, override=True):
            sys.exit(
                f"ERROR: : Unable to load environment variables from file {args.env}"
            )

    try:
        config = parse_config_file(args.config)
        start_agent(config, args.workers)
    except (KeyboardInterrupt, RuntimeError):
        pass
    except Exception as e:
        sys.exit(f"ERROR: Unable to start agent: {e}")


if __name__ == "__main__":
    main()
