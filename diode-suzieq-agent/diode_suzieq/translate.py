#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc

from typing import Iterable
from netboxlabs.diode.sdk.diode.v1 import ingester_pb2
from netboxlabs.diode.sdk.diode.v1 import device_pb2
from netboxlabs.diode.sdk.diode.v1 import device_type_pb2
from netboxlabs.diode.sdk.diode.v1 import interface_pb2
from netboxlabs.diode.sdk.diode.v1 import manufacturer_pb2
from netboxlabs.diode.sdk.diode.v1 import platform_pb2
from netboxlabs.diode.sdk.diode.v1 import site_pb2


def translate_device_status(device_status: str) -> str:
    if device_status.lower() == "alive":
        return "active"
    return "active"


def translate_device(device_info: dict) -> device_pb2.Device:
    manufacturer = manufacturer_pb2.Manufacturer(name=device_info["vendor"])
    device_type = device_type_pb2.DeviceType(
        model=device_info["model"],
        manufacturer=manufacturer
    )
    platform = platform_pb2.Platform(
        name=device_info["os"],
        manufacturer=manufacturer
    )
    device = device_pb2.Device(
        name=device_info["hostname"],
        device_type=device_type,
        platform=platform,
        serial=device_info["serialNumber"],
        status=translate_device_status(device_info["status"])
    )
    return device


def translate_interface_type(interface_type: str) -> str:
    if interface_type.lower() == "ethernet":
        return "other"
    return "other"


def translate_interface_state(interface_state: str) -> bool:
    return interface_state.lower() == "up"


def translate_interface(interface_info: dict) -> interface_pb2.Interface:
    device = device_pb2.Device(name=interface_info["hostname"])
    interface = interface_pb2.Interface(
        device=device,
        name=interface_info["ifname"],
        type=translate_interface_type(interface_info["type"]),
        enabled=translate_interface_state(interface_info["adminState"]),
        mtu=interface_info["mtu"],
        mac_address=interface_info["macaddr"],
        speed=interface_info["speed"],
        description=interface_info["description"]
    )
    return interface


def translate_suzieq_to_diode(data: dict) -> Iterable[ingester_pb2.Entity]:
    entities = []

    for device_info in data.get("device", []):
        entities.append(translate_device(device_info))

    for interface_info in data.get("interfaces", []):
        entities.append(translate_interface(interface_info))

    return entities
