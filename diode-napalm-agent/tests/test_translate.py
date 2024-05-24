#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""NetBox Labs - Translate Tests."""

import pytest
from netboxlabs.diode.sdk.ingester import (
    Device,
    DeviceType,
    Platform,
    Interface,
    IPAddress,
    Entity
)
from diode_napalm.translate import (
    translate_device,
    translate_interface,
    translate_interface_ips,
    translate_data
)


def test_translate_device():
    """Ensure device information is correctly translated."""
    device_info = {
        "hostname": "device1",
        "model": "modelX",
        "vendor": "vendorY",
        "driver": "driverZ",
        "serial_number": "12345",
        "site": "siteA"
    }

    device = translate_device(device_info)
    assert device.name == "device1"
    assert device.device_type.model == "modelX"
    assert device.device_type.manufacturer == "vendorY"
    assert device.platform.name == "driverZ"
    assert device.platform.manufacturer == "vendorY"
    assert device.serial == "12345"
    assert device.status == "active"
    assert device.site == "siteA"


def test_translate_interface():
    """Ensure interface information is correctly translated."""
    device = Device(
        name="device1",
        device_type=DeviceType(model="modelX", manufacturer="vendorY"),
        platform=Platform(name="driverZ", manufacturer="vendorY"),
        serial="12345",
        status="active",
        site="siteA"
    )
    interface_info = {
        "is_enabled": True,
        "mtu": 1500,
        "mac_address": "00:11:22:33:44:55",
        "speed": 1000,
        "description": "uplink"
    }

    interface = translate_interface(device, "eth0", interface_info)
    assert interface.device == device
    assert interface.name == "eth0"
    assert interface.enabled is True
    assert interface.mtu == 1500
    assert interface.mac_address == "00:11:22:33:44:55"
    assert interface.speed == 1000
    assert interface.description == "uplink"


def test_translate_interface_ips():
    """Ensure interface IP addresses are correctly translated."""
    device = Device(
        name="device1",
        device_type=DeviceType(model="modelX", manufacturer="vendorY"),
        platform=Platform(name="driverZ", manufacturer="vendorY"),
        serial="12345",
        status="active",
        site="siteA"
    )
    interface = Interface(
        device=device,
        name="eth0",
        type="other",
        enabled=True,
        mtu=1500,
        mac_address="00:11:22:33:44:55",
        speed=1000,
        description="uplink"
    )
    interfaces_ip = {
        "eth0": {
            "ipv4": {
                "192.168.1.1": {"prefix_length": 24}
            },
            "ipv6": {
                "fe80::1": {"prefix_length": 64}
            }
        }
    }

    ip_entities = list(translate_interface_ips(interface, interfaces_ip))
    assert len(ip_entities) == 2
    assert ip_entities[0].ip_address.address == "192.168.1.1/24"
    assert ip_entities[1].ip_address.address == "fe80::1/64"
    assert ip_entities[0].ip_address.interface == interface
    assert ip_entities[1].ip_address.interface == interface


def test_translate_data():
    """Ensure full data translation works correctly."""
    data = {
        "device": {
            "hostname": "device1",
            "model": "modelX",
            "vendor": "vendorY",
            "serial_number": "12345",
            "interface_list": ["eth0"],
            "site": "siteA"
        },
        "driver": "driverZ",
        "site": "siteA",
        "interface": {
            "eth0": {
                "is_enabled": True,
                "mtu": 1500,
                "mac_address": "00:11:22:33:44:55",
                "speed": 1000,
                "description": "uplink"
            }
        },
        "interface_ip": {
            "eth0": {
                "ipv4": {
                    "192.168.1.1": {"prefix_length": 24}
                },
                "ipv6": {
                    "fe80::1": {"prefix_length": 64}
                }
            }
        }
    }

    entities = list(translate_data(data))
    # 1 device, 1 interface, 2 IPs (but IPs are in one entity)
    assert len(entities) == 3
    device_entity = entities[0].device
    assert device_entity.name == "device1"
    assert device_entity.device_type.model == "modelX"
    assert device_entity.device_type.manufacturer == "vendorY"
    assert device_entity.platform.name == "driverZ"
    assert device_entity.platform.manufacturer == "vendorY"
    assert device_entity.serial == "12345"
    assert device_entity.status == "active"
    assert device_entity.site == "siteA"
