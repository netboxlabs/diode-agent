#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode SDK Client for NAPALM."""

import logging
import threading
from typing import Optional

from netboxlabs.diode.sdk import DiodeClient

from diode_napalm.translate import translate_data
from diode_napalm.version import version_semver

APP_NAME = "diode-napalm-agent"
APP_VERSION = version_semver()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Client:
    """
    Singleton class for managing the Diode client for NAPALM.

    This class ensures only one instance of the Diode client is created and provides methods
    to initialize the client and ingest data.

    Attributes
    ----------
        diode_client (DiodeClient): Instance of the DiodeClient.

    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Create a new instance of the Client if one does not already exist.

        Returns
        -------
            Client: The singleton instance of the Client.

        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the Client instance with no Diode client."""
        if not hasattr(self, '_initialized'):  # Prevent reinitialization
            self.diode_client = None
            self._initialized = True

    def init_client(
        self,
        target: str,
        api_key: Optional[str] = None,
        tls_verify: bool = None
    ):
        """
        Initialize the Diode client with the specified target, API key, and TLS verification.

        Args:
        ----
            target (str): The target endpoint for the Diode client.
            api_key (Optional[str]): The API key for authentication (default is None).
            tls_verify (bool): Whether to verify TLS certificates (default is None).

        """
        with self._lock:
            self.diode_client = DiodeClient(
                target=target, app_name=APP_NAME, app_version=APP_VERSION, api_key=api_key, tls_verify=tls_verify)

    def ingest(self, data: dict):
        """
        Ingest data using the Diode client after translating it.

        Args:
        ----
            data (dict): The data to be ingested.

        Raises:
        ------
            ValueError: If the Diode client is not initialized.

        """
        if self.diode_client is None:
            raise ValueError("Diode client not initialized")

        with self._lock:
            ret = self.diode_client.ingest(translate_data(data))

        if not len(ret.errors):
            logger.info("Successful ingestion")
        else:
            logger.error(ret)
