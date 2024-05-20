#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Translate from NAPALM output format to Diode SDK entites"""

from typing import Iterable
from netboxlabs.diode.sdk.diode.v1.ingester_pb2 import (
    Entity,
    Site,
    Platform,
    Manufacturer,
    Device,
    DeviceType,
    Interface,
)


def translate_device(device_info: dict) -> Device:
    manufacturer = Manufacturer(name=device_info["vendor"])
    device_type = DeviceType(
        model=device_info["model"],
        manufacturer=manufacturer
    )
    platform = Platform(
        name=device_info["driver"],
        manufacturer=manufacturer
    )
    site = Site(name=device_info["site"])
    device = Device(
        name=device_info["hostname"],
        device_type=device_type,
        platform=platform,
        serial=device_info["serial_number"],
        status="active",
        site=site
    )
    return device


def translate_interface(device: Device, if_name: str, interface_info: dict) -> Interface:
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
    entities = []

    if "device" in data:
        data["device"]["driver"] = data["driver"]
        data["device"]["site"] = data["site"]
        device = translate_device(data["device"])
        entities.append(Entity(device=device))
        if "interface" in data:
            for if_name in data["interface"]:
                if if_name in data["device"]["interface_list"]:
                    entities.append(Entity(interface=translate_interface(
                        device, if_name, data["interface"][if_name])))

    return entities
