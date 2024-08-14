#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Translate from NAPALM output format to Diode SDK entities."""

from collections.abc import Iterable

from netboxlabs.diode.sdk.ingester import IPAddress, Prefix, Entity


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
    for ip in data.get("active_ips", []):
        entities.append(Entity(ip_address=IPAddress(address=ip)))

    return entities
