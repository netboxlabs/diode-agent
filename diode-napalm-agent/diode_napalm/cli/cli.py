
#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode NAPALM Agent CLI"""

import argparse
import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

from napalm import get_network_driver
from diode_napalm.client import Client
from diode_napalm.parser import parse_config, ParseException
from diode_napalm.version import version_semver
import netboxlabs.diode.sdk.version as SdkVersion


def parse_config_file(cfile: Path):
    try:
        with open(cfile, "r") as f:
            cfg = parse_config(f.read())
    except ParseException as e:
        sys.exit(e.args[1])
    except Exception as e:
        sys.exit(f"ERROR: Unable to open config file {cfile}: {e.args[1]}")
    return cfg.diode


async def start_policy(cfg, client):
    for info in cfg.data:
        print(f"Get driver '{info.driver}'")
        np_driver = get_network_driver(info.driver)
        print(f"Getting information from '{info.hostname}'")
        with np_driver(info.hostname, info.username, info.password, info.timeout, info.optional_args) as device:
            data = {}
            data["driver"] = info.driver
            data["site"] = cfg.config.netbox.get("site", None)
            data["device"] = device.get_facts()
            data["interface"] = device.get_interfaces()
            client.ingest(data)


async def start_agent(cfg):
    # start diode client
    client = Client()
    client.init_client(target=cfg.config.target,
                       api_key=cfg.config.api_key, tls_verify=cfg.config.tls_verify)
    for policy_name in cfg.policies:
        try:
            await start_policy(cfg.policies[policy_name], client)
        except Exception as e:
            raise Exception(f"Unable to start policy {policy_name}: {e}")


def agent_main():
    parser = argparse.ArgumentParser(description="Diode Agent for SuzieQ")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"Diode Agent version: {version_semver()}, SuzieQ version: {version('napalm')}, Diode SDK version: {SdkVersion.version_semver()}",
        help='Display Diode Agent, SuzieQ and Diode SDK versions'
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="config.yaml",
        help='Agent yaml configuration file',
        type=str, required=True
    )
    args = parser.parse_args()
    config = parse_config_file(Path(args.config))
    try:
        asyncio.run(start_agent(config))
    except (KeyboardInterrupt, RuntimeError):
        pass
    except Exception as e:
        sys.exit(f"ERROR: Unable to start agent: {e}")


if __name__ == '__main__':
    agent_main()
