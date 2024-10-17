#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode Ping Port Scan."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
from ipaddress import IPv4Network

SCAN_PORTS = [
    {"name": "FTP", "port": 21, "protocol": "tcp"},
    {"name": "SSH", "port": 22, "protocol": "tcp"},
    {"name": "Telnet", "port": 23, "protocol": "tcp"},
    {"name": "DNS", "port": 53, "protocol": "udp"},
    {"name": "HTTP", "port": 80, "protocol": "tcp"},
    {"name": "SNMP", "port": 161, "protocol": "udp"},
    {"name": "SNMP Trap", "port": 162, "protocol": "udp"},
    {"name": "HTTPS", "port": 443, "protocol": "tcp"},
    {"name": "RDP", "port": 3389, "protocol": "tcp"},
]


def is_udp_port_open(ip: str, port: int, timeout: int = 1) -> tuple[int, bool]:
    """
    Check if a UDP port is open on a given IP address.

    Args:
    ----
        ip (str): The IP address to check.
        port (int): The UDP port number to check.
        timeout (int): Timeout in seconds.

    Returns:
    -------
        bool: True if the port is open or no response (firewalled),
              False if unreachable.

    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(b"", (ip, port))
        s.recvfrom(1024)
        return port, True
    except TimeoutError:
        return port, False
    except OSError:
        # ICMP 'Port Unreachable' received
        return port, False
    finally:
        s.close()


def is_tcp_port_open(ip: str, port: int, timeout: int = 1) -> tuple[int, bool]:
    """
    Check if a TCP port is open on a given IP address.

    Args:
    ----
        ip (str): The IP address to check.
        port (int): The TCP port number to check.
        timeout (int): Timeout in seconds.

    Returns:
    -------
        bool: True if the port is open, False otherwise.

    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.shutdown(socket.SHUT_RDWR)
        return port, True
    except TimeoutError:
        return port, False
    except OSError:
        # Connection refused or other socket error
        return port, False
    finally:
        s.close()


def scan_ports(ip: IPv4Network) -> dict[str, bool]:
    """
    Scan predefined TCP and UDP ports on the provided IP address.

    Args:
    ----
        ip (IPv4Network): The IP address to scan.

    Returns:
    -------
        list[dict]: A list of dictionaries containing the name, port,
        protocol, and whether the port is open or closed.

    """
    port_scans = {}
    with ThreadPoolExecutor(max_workers=len(SCAN_PORTS)) as executor:
        futures = []
        for port in SCAN_PORTS:
            if port["protocol"] == "tcp":
                futures.append(executor.submit(is_tcp_port_open, str(ip), port["port"]))
            else:
                futures.append(executor.submit(is_udp_port_open, str(ip), port["port"]))
        for future in as_completed(futures):
            result = future.result()
            if result:
                name = next(port["name"] for port in SCAN_PORTS if port["port"] == result[0])
                port_scans[name] = result[1]

    return port_scans
