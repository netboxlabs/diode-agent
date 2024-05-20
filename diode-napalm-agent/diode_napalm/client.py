#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode SDK Client for NAPALM"""

from typing import Optional
from diode_napalm.version import version_semver
from diode_napalm.translate import translate_data
from netboxlabs.diode.sdk import DiodeClient

APP_NAME = "diode-napalm-agent"
APP_VERSION = version_semver()


class Client:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Client, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.diode_client = None

    def init_client(
        self,
        target: str,
        api_key: Optional[str] = None,
        tls_verify: bool = None
    ):
        self.diode_client = DiodeClient(
            target=target, app_name=APP_NAME, app_version=APP_VERSION, api_key=api_key, tls_verify=tls_verify)

    def ingest(self, data: dict):
        if self.diode_client is None:
            raise ValueError("diode client defined")
        ret = self.diode_client.ingest(translate_data(data))
        print(ret)
        
