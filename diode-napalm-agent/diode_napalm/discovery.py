#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Discover the correct NAPALM Driver."""

import logging

from napalm import get_network_driver

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

supported_drivers = ["ios", "eos", "junos", "nxos"]


def discover_device_driver(info: dict) -> str:
    """
    Discover the correct NAPALM driver for the given device information.

    Args:
    ----
        info (dict): A dictionary containing device connection information.
            Expected keys are 'hostname', 'username', 'password', 'timeout',
            and 'optional_args'.

    Returns:
    -------
        str: The name of the driver that successfully connects and identifies
             the device. Returns an empty string if no suitable driver is found.

    """
    for driver in supported_drivers:
        try:
            np_driver = get_network_driver(driver)
            with np_driver(info.hostname, info.username, info.password, info.timeout, info.optional_args) as device:
                device_info = device.get_facts()
                if device_info.get("serial_number", "Unknown").lower() == "unknown":
                    continue
                return driver
        except Exception as e:
            logger.error(e)
    return ''