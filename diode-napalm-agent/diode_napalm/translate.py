#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Translate from NAPALM output format to Diode SDK entities."""

from typing import Iterable
from netboxlabs.diode.sdk.ingester import (
    Entity,
    Platform,
    Device,
    DeviceType,
    Interface,
)


def translate_device(device_info: dict) -> Device:
    """
    Translate device information from NAPALM format to Diode SDK Device entity.

    Args:
        device_info (dict): Dictionary containing device information.

    Returns:
        Device: Translated Device entity.
    """
    device = Device(
        name=device_info["hostname"],
        device_type=DeviceType(
            model=device_info["model"],
            manufacturer=device_info["vendor"]
        ),
        platform=Platform(
            name=device_info["driver"],
            manufacturer=device_info["vendor"]
        ),
        serial=device_info["serial_number"],
        status="active",
        site=device_info["site"]
    )
    return device


def translate_interface(device: Device, if_name: str, interface_info: dict) -> Interface:
    """
    Translate interface information from NAPALM format to Diode SDK Interface entity.

    Args:
        device (Device): The device to which the interface belongs.
        if_name (str): The name of the interface.
        interface_info (dict): Dictionary containing interface information.

    Returns:
        Interface: Translated Interface entity.
    """
    interface = Interface(
        device=device,
        name=if_name,
        type="other",
        enabled=interface_info["is_enabled"],
        mtu=interface_info["mtu"],
        mac_address=interface_info["mac_address"],
        speed=int(interface_info["speed"]),
        description=interface_info["description"]
    )
    return interface


def translate_data(data: dict) -> Iterable[Entity]:
    """
    Translate data from NAPALM format to Diode SDK entities.

    Args:
        data (dict): Dictionary containing data to be translated.

    Returns:
        Iterable[Entity]: Iterable of translated entities.
    """
    entities = []

    device_info = data.get("device")
    if device_info:
        device_info["driver"] = data.get("driver")
        device_info["site"] = data.get("site")
        device = translate_device(device_info)
        entities.append(Entity(device=device))

        interfaces = data.get("interface", {})
        interface_list = device_info.get("interface_list", [])
        for if_name, interface_info in interfaces.items():
            if if_name in interface_list:
                interface = translate_interface(
                    device, if_name, interface_info)
                entities.append(Entity(interface=interface))

    return entities
