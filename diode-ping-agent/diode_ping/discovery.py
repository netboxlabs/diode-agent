#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Discover the correct NAPALM Driver."""

from ipaddress import IPv4Network, ip_interface
import logging
import socket

import psutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def discover_interface(name: str) -> str:
    """
    Discover the most used network interface on the device.

    Args:
    ----
        name (str): The policy name.

    Returns:
    -------
        str: The name of the network interface that has the highest combined
             count of sent and received bytes. Returns an empty string if no
             interface is found.
    """
    io_counters = psutil.net_io_counters(pernic=True)
    most_used_interface = max(
        io_counters.items(), key=lambda x: x[1].bytes_sent + x[1].bytes_recv
    )[0]
    logger.info(
        f"Policy {name}: '{most_used_interface}' interface is the most used in {list(io_counters.keys())}"
    )
    return most_used_interface


def discover_ip_range(name: str, interface: str) -> IPv4Network:
    """
    Discover the IP network range for a given network interface.

    Args:
    ----
        name (str): The name associated with the operation or policy for logging purposes.
        interface (str): The name of the network interface to examine.

    Returns:
    -------
        IPv4Network: The IP network range for the given interface, based on its IP address and netmask.
                     Returns None if no IPv4 address is found.
    """
    addrs = psutil.net_if_addrs()[interface]
    for addr in addrs:
        if addr.family == socket.AF_INET:
            interface = ip_interface(f"{addr.address}/{addr.netmask}")
            return interface.network
    logger.error(f"Policy {name}: No IPv4 address found for interface {interface}")
    return None


def get_ip_address(name: str, interface: str) -> IPv4Network:
    addrs = psutil.net_if_addrs()
    if interface in addrs:
        for addr in addrs[interface]:
            if addr.family == socket.AF_INET:
                return addr.address
    logger.error(f"Policy {name}: No IPv4 address found for interface {interface}")
    return None
