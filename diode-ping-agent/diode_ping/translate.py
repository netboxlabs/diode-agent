#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Translate from NAPALM output format to Diode SDK entities."""

from collections.abc import Iterable

from netboxlabs.diode.sdk.ingester import Entity, IPAddress, Prefix


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

    entities.append(
        Entity(prefix=Prefix(prefix=str(data.get("prefix")), site=data.get("site", {})))
    )

    for active in data.get("active_ips", []):
        description = ""
        if active.get("vendor"):
            description = f"MAC Vendor: {active.get("vendor")}"

        comments = ""
        ports = active.get("ports", {})
        for port in ports:
            if ports[port]:
                comments += f"{port}: OPEN\n\n"
            else:
                comments += f"{port}: unreachable\n\n"

        entities.append(
            Entity(
                ip_address=IPAddress(
                    address=active["ip"], description=description, comments=comments
                )
            )
        )

    return entities
