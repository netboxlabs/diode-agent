#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode Ping Agent CLI."""

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import IPv4Network

import netboxlabs.diode.sdk.version as SdkVersion
from dotenv import load_dotenv
from mac_vendor_lookup import MacLookup
from ping3 import ping

from diode_ping.arp import arp_scan
from diode_ping.client import Client
from diode_ping.discovery import discover_interface, discover_ip_range, get_ip_address
from diode_ping.parser import Diode, Policy, parse_config_file
from diode_ping.ports import scan_ports
from diode_ping.version import version_semver

mac = MacLookup()
mac.update_vendors()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ping_ip(ip: IPv4Network) -> IPv4Network:
    """
    Ping a given IP address.

    Args:
    ----
        ip: The IP address to ping.

    Returns:
    -------
        The IP address if the ping is successful, otherwise None.

    """
    response = ping(ip, timeout=1)
    if response is not None:
        return ip
    return None


def scan_network(ip: IPv4Network) -> list[IPv4Network]:
    """
    Scan a network range for active IP addresses.

    Args:
    ----
        ip: The IP network range to scan.

    Returns:
    -------
        A list of active IP addresses within the given network range.

    """
    active_ips = []
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = [
            executor.submit(ping_ip, str(ip_address)) for ip_address in ip.hosts()
        ]
        for future in as_completed(futures):
            result = future.result()
            if result:
                active_ips.append(result)
    return set(active_ips)


def arp_scan_async(
    interface: str, src_ip: IPv4Network, ips: list[IPv4Network]
) -> dict[IPv4Network, str]:
    """
    Perform an ARP scan to resolve the MAC address of a given IP address.

    Args:
    ----
        interface: The network interface to use.
        src_ip: The source IP address.
        ips: The destination IP addresses.

    Returns:
    -------
        dict: The MAC address of the destination IP address.

    """
    data = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(arp_scan, interface, src_ip, ip_address)
            for ip_address in ips
        ]
        for future in as_completed(futures):
            result = future.result()
            if result:
                data[result[0]] = result[1]
    return data


def run_ping(name: str, policy: Policy):
    """
    Run the device discovery and ping process for a specified policy.

    Args:
    ----
        name: The name of the policy.
        policy: The policy object containing configuration data.

    Raises:
    ------
        Exception: If the interface or IP range cannot be discovered.

    """
    if policy.interface is None:
        logger.info(f"Policy {name}: Interface not informed, discovering the most used")
        policy.interface = discover_interface(name)
        if not policy.interface:
            raise Exception(f"Policy {name}: Not able to discover interface")

    if policy.network is None:
        logger.info(
            f"Policy {name}: IP range not informed, discovering it based on the provided interface"
        )
        policy.network = discover_ip_range(name, policy.interface)
        if not policy.network:
            raise Exception(f"Policy {name}: Not able to discover IPv4 range")

    logger.info(
        f"Policy {name}: Getting Active IP Addresses on interface '{policy.interface}' in range '{policy.network}'"
    )
    active_ips = scan_network(policy.network)

    src_ip = get_ip_address(name, policy.interface)

    mac_addresses = {}
    if policy.config.macaddress_lookup:
        mac_addresses = arp_scan_async(policy.interface, src_ip, active_ips)

    ips = []
    for ip in active_ips:
        ipam = {
            "ip": str(ip),
        }
        if policy.config.macaddress_lookup and mac_addresses.get(ip):
            try:
                ipam["vendor"] = mac.lookup(mac_addresses.get(ip))
            except Exception:
                pass
        if policy.config.scan_ports:
            ipam["ports"] = scan_ports(ip)
        ips.append(ipam)

    data = {
        "site": policy.config.netbox.get("site", None),
        "prefix": policy.network,
        "active_ips": ips,
    }

    Client().ingest(name, data)


def start_agent(cfg: Diode):
    """
    Start the Diode client and execute policies.

    Args:
    ----
        cfg: The configuration object containing policies.

    """
    client = Client()
    client.init_client(target=cfg.config.target, api_key=cfg.config.api_key)
    for policy_name in cfg.policies:
        run_ping(policy_name, cfg.policies.get(policy_name))


def main():
    """
    Main entry point for the Diode Ping Agent CLI.

    Parses command-line arguments and starts the agent.
    """
    parser = argparse.ArgumentParser(description="Diode Agent for Ping")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"Diode Agent version: {version_semver()}, "
        f"Diode SDK version: {SdkVersion.version_semver()}",
        help="Display Diode Agent and Diode SDK versions",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="config.yaml",
        help="Path to the agent YAML configuration file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-e",
        "--env",
        metavar=".env",
        help="Path to a file containing environment variables",
        type=str,
    )
    args = parser.parse_args()

    if hasattr(args, "env") and args.env is not None:
        if not load_dotenv(args.env, override=True):
            sys.exit(
                f"ERROR: Unable to load environment variables from file {args.env}"
            )

    try:
        config = parse_config_file(args.config)
        start_agent(config)
    except (KeyboardInterrupt, RuntimeError):
        pass
    except Exception as e:
        sys.exit(f"ERROR: Unable to start agent: {e}")


if __name__ == "__main__":
    main()
