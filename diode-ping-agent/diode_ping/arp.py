#!/usr/bin/env python
# Copyright 2024 NetBox Labs Inc
"""Diode Ping Agent ARP."""

import binascii
import fcntl
import socket
import struct
from ipaddress import IPv4Network

# Constants
SIOCGIFHWADDR = 0x8927  # Get hardware address
SIOCGIFADDR = 0x8915  # Get IP address


def get_mac_address(ifname: bytes) -> str:
    """
    Retrieve the MAC address for a given network interface.

    Args:
    ----
        ifname (bytes): Network interface name as a byte string.

    Returns:
    -------
        str: MAC address in colon-separated format.

    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(sock.fileno(), SIOCGIFHWADDR, struct.pack("256s", ifname[:15]))
    return ":".join([f"{b:02x}" for b in info[18:24]])


def create_arp_request(
    src_mac: str, src_ip: IPv4Network, target_ip: IPv4Network
) -> bytes:
    """
    Create an ARP request packet.

    Args:
    ----
        src_mac (str): Source MAC address.
        src_ip (IPv4Network): Source IP address.
        target_ip (IPv4Network): Target IP address to send ARP request to.

    Returns:
    -------
        bytes: The crafted ARP request packet.

    """
    eth_header = struct.pack(
        "!6s6s2s",
        b"\xff\xff\xff\xff\xff\xff",  # Destination MAC (Broadcast)
        binascii.unhexlify(src_mac.replace(":", "")),  # Source MAC
        b"\x08\x06",
    )  # ARP protocol

    arp_header = struct.pack(
        "!2s2s1s1s2s6s4s6s4s",
        b"\x00\x01",  # Hardware type (Ethernet)
        b"\x08\x00",  # Protocol type (IP)
        b"\x06",  # Hardware size
        b"\x04",  # Protocol size
        b"\x00\x01",  # Opcode (request)
        binascii.unhexlify(src_mac.replace(":", "")),  # Sender MAC
        socket.inet_aton(str(src_ip)),  # Sender IP
        b"\x00\x00\x00\x00\x00\x00",  # Target MAC
        socket.inet_aton(str(target_ip)),
    )  # Target IP
    return eth_header + arp_header


def parse_arp_response(packet: bytes) -> tuple[str, str]:
    """
    Parse the ARP response packet.

    Args:
    ----
        packet (bytes): Raw packet data.

    Returns:
    -------
        tuple[str, str]: A tuple containing the source IP and MAC address
                         from the ARP response. If not ARP, returns (None, None).

    """
    eth_header = packet[0:14]
    eth = struct.unpack("!6s6s2s", eth_header)

    if eth[2] == b"\x08\x06":  # Check if it's an ARP packet
        arp_header = packet[14:42]
        arp = struct.unpack("!2s2s1s1s2s6s4s6s4s", arp_header)

        src_mac = binascii.hexlify(arp[5]).decode("utf-8")
        src_ip = socket.inet_ntoa(arp[6])
        return src_ip, src_mac
    return None, None


def arp_scan(
    ifname: str, src_ip: IPv4Network, target_ip: IPv4Network
) -> tuple[IPv4Network, str]:
    """
    Perform an ARP scan on the network to find the target MAC address.

    Args:
    ----
        ifname (str): Network interface name.
        src_ip (IPv4Network): Source IP address.
        target_ip (IPv4Network): Target IP address to scan.

    Returns:
    -------
        tuple: A tuple containing the target IP and MAC address if found.

    """
    src_mac = get_mac_address(ifname.encode())
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    sock.bind((ifname, 0))
    arp_request = create_arp_request(src_mac, src_ip, target_ip)
    sock.send(arp_request)
    while True:
        raw_packet = sock.recv(65536)
        src_ip, src_mac = parse_arp_response(raw_packet)
        if src_ip:
            return target_ip, src_mac
