#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Translate from NAPALM output format to Diode SDK entities."""

from typing import Iterable

from netboxlabs.diode.sdk.ingester import Device, DeviceType, Entity, Interface, IPAddress, Platform


def translate_device(device_info: dict) -> Device:
    """
    Translate device information from NAPALM format to Diode SDK Device entity.

    Args:
    ----
        device_info (dict): Dictionary containing device information.

    Returns:
    -------
        Device: Translated Device entity.

    """
    device = Device(
        name=device_info.get("hostname"),
        device_type=DeviceType(
            model=device_info.get("model"),
            manufacturer=device_info.get("vendor")
        ),
        platform=Platform(
            name=device_info.get("driver"),
            manufacturer=device_info.get("vendor")
        ),
        serial=device_info.get("serial_number"),
        status="active",
        site=device_info.get("site")
    )
    return device


def translate_interface(device: Device, if_name: str, interface_info: dict) -> Interface:
    """
    Translate interface information from NAPALM format to Diode SDK Interface entity.

    Args:
    ----
        device (Device): The device to which the interface belongs.
        if_name (str): The name of the interface.
        interface_info (dict): Dictionary containing interface information.

    Returns:
    -------
        Interface: Translated Interface entity.

    """
    interface = Interface(
        device=device,
        name=if_name,
        type="other",
        enabled=interface_info.get("is_enabled"),
        mtu=interface_info.get("mtu"),
        mac_address=interface_info.get("mac_address"),
        speed=int(interface_info.get("speed")),
        description=interface_info.get("description")
    )
    return interface


def translate_interface_ips(interface: Interface, interfaces_ip: dict) -> Iterable[Entity]:
    """
    Translate IP address information for an interface.

    Args:
    ----
        interface (Interface): The interface entity.
        if_name (str): The name of the interface.
        interfaces_ip (dict): Dictionary containing interface IP information.

    Returns:
    -------
        Iterable[Entity]: Iterable of translated IP address entities.

    """
    ip_entities = []

    for if_ip_name, ip_info in interfaces_ip.items():
        if interface.name in if_ip_name:
            for ip_version, default_prefix in (("ipv4", 32), ("ipv6", 128)):
                for ip, details in ip_info.get(ip_version, {}).items():
                    ip_entities.append(Entity(
                        ip_address=IPAddress(
                            address=f"{ip}/{details.get('prefix_length', default_prefix)}",
                            interface=interface
                        )))

    return ip_entities


def translate_data(data: dict) -> Iterable[Entity]:
    """
    Translate data from NAPALM format to Diode SDK entities.

    Args:
    ----
        data (dict): Dictionary containing data to be translated.

    Returns:
    -------
        Iterable[Entity]: Iterable of translated entities.

    """
    entities = []

    device_info = data.get("device", {})
    interfaces = data.get("interface", {})
    interfaces_ip = data.get("interface_ip", {})
    if device_info:
        device_info["driver"] = data.get("driver")
        device_info["site"] = data.get("site")
        device = translate_device(device_info)
        entities.append(Entity(device=device))

        interface_list = device_info.get("interface_list", [])
        for if_name, interface_info in interfaces.items():
            if if_name in interface_list:
                interface = translate_interface(
                    device, if_name, interface_info)
                entities.append(Entity(interface=interface))
                entities.extend(translate_interface_ips(
                    interface, interfaces_ip))

    return entities
